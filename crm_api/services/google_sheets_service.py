import os
import re
import logging
from typing import List, Dict, Any, Optional

from django.conf import settings
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.contrib.auth import get_user_model
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from crm_api.models import Lead, ActivityTimeline
from crm_api.services.lead_reminder_service import schedule_callback_followup

logger = logging.getLogger(__name__)

# Scopes for Google Sheets API
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

class GoogleSheetsService:
    """
    Service to handle fetching and processing leads from Google Sheets.
    """
    
    def __init__(self):
        self.creds = self._load_credentials()
        self.service = build("sheets", "v4", credentials=self.creds, cache_discovery=False)
        self.user_model = get_user_model()
        
    def _load_credentials(self):
        creds = None
        
        # 1. Try OAuth2 Refresh Token
        if getattr(settings, "GOOGLE_REFRESH_TOKEN", None):
            try:
                creds = Credentials(
                    token=None,
                    refresh_token=settings.GOOGLE_REFRESH_TOKEN,
                    client_id=settings.GOOGLE_CLIENT_ID,
                    client_secret=settings.GOOGLE_CLIENT_SECRET,
                    token_uri="https://oauth2.googleapis.com/token",
                    scopes=SCOPES
                )
                if creds and creds.refresh_token:
                    if creds.expired:
                        creds.refresh(Request())
                else:
                    creds = None
            except Exception as e:
                logger.error(f"Google Sheets OAuth2 Initialization Failed: {str(e)}")
                creds = None

        # 2. Try Service Account if OAuth2 failed
        if not creds and getattr(settings, "GOOGLE_SERVICE_ACCOUNT_FILE", None):
            if os.path.exists(settings.GOOGLE_SERVICE_ACCOUNT_FILE):
                try:
                    import json
                    with open(settings.GOOGLE_SERVICE_ACCOUNT_FILE, 'r') as f:
                        data = json.load(f)
                        if data.get('type') == 'service_account':
                            creds = service_account.Credentials.from_service_account_file(
                                settings.GOOGLE_SERVICE_ACCOUNT_FILE, scopes=SCOPES
                            )
                        else:
                            logger.info("Provided credentials file is not a Service Account JSON.")
                except Exception as e:
                    logger.error(f"Service Account Loading Failed: {str(e)}")
            else:
                logger.error(f"Service account file not found: {settings.GOOGLE_SERVICE_ACCOUNT_FILE}")

        if not creds:
            raise Exception("No valid Google credentials found (Refresh Token or Service Account).")
            
        return creds

    def fetch_sheet_data(self, sheet_id: str, range_name: str) -> List[List[Any]]:
        """
        Fetches raw data from the specified Google Sheet.
        """
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=sheet_id, range=range_name
            ).execute()
            return result.get("values", [])
        except Exception as e:
            logger.error(f"Error fetching Google Sheet data: {str(e)}")
            return []

    def normalize_header(self, header: str) -> str:
        """
        Normalizes header name: lowercase, strip, remove special characters.
        """
        if not header:
            return ""
        # Remove non-alphanumeric except spaces
        header = re.sub(r'[^a-zA-Z0-9\s]', '', str(header))
        return header.strip().lower()

    def get_column_mapping(self, headers: List[str]) -> Dict[str, int]:
        """
        Dynamically maps normalized headers to Lead model fields using aliases.
        """
        field_aliases = {
            "name": ["name", "full name", "customer name", "client name", "lead name"],
            "phone": ["phone", "mobile", "contact", "phone number", "mobile number", "contact number"],
            "email": ["email", "email address", "mail id"],
            "location": ["city", "location", "address", "area", "residence"],
            "budget": ["budget", "amount", "price", "est budget", "estimated budget"],
            "source": ["source", "lead source", "channel"],
        }
        
        mapping = {}
        normalized_headers = [self.normalize_header(h) for h in headers]
        
        for field, aliases in field_aliases.items():
            for idx, h_norm in enumerate(normalized_headers):
                if h_norm in aliases:
                    mapping[field] = idx
                    break
        
        return mapping

    def normalize_phone(self, phone: str) -> str:
        """
        Cleans phone number: keeps only digits.
        """
        if not phone:
            return ""
        return re.sub(r'\D', '', str(phone))

    def normalize_email(self, email: str) -> str:
        """
        Normalizes email: lowercase and strip.
        """
        if not email:
            return ""
        return str(email).strip().lower()

    def process_rows(self, data: List[List[Any]]) -> Dict[str, int]:
        """
        Processes sheet data and inserts leads.
        Returns stats: total, created, duplicates, errors.
        """
        if not data or len(data) < 2:
            return {"total": 0, "created": 0, "duplicates": 0, "errors": 0}
            
        headers = data[0]
        rows = data[1:]
        mapping = self.get_column_mapping(headers)
        
        # We need at least phone or name to identify a lead
        if "phone" not in mapping and "email" not in mapping:
            logger.error("Mapping failed: Neither 'phone' nor 'email' column found.")
            return {"total": len(rows), "created": 0, "duplicates": 0, "errors": 1}

        stats = {"total": len(rows), "created": 0, "duplicates": 0, "errors": 0}
        
        # Get default assignee (Admin)
        default_assignee = self.user_model.objects.filter(role="ADMIN").first()
        
        for row in rows:
            try:
                # Extract data based on mapping
                name = row[mapping["name"]] if "name" in mapping and mapping["name"] < len(row) else ""
                phone_raw = row[mapping["phone"]] if "phone" in mapping and mapping["phone"] < len(row) else ""
                email_raw = row[mapping["email"]] if "email" in mapping and mapping["email"] < len(row) else ""
                location = row[mapping["location"]] if "location" in mapping and mapping["location"] < len(row) else ""
                budget_raw = row[mapping["budget"]] if "budget" in mapping and mapping["budget"] < len(row) else 0
                source_raw = row[mapping["source"]] if "source" in mapping and mapping["source"] < len(row) else "Google Sheet"
                
                phone = self.normalize_phone(phone_raw)
                email = self.normalize_email(email_raw)
                
                # Skip if basic info is missing
                if not phone and not email:
                    continue
                
                # Duplicate check: Phone OR Email
                exists = False
                if phone and Lead.objects.filter(phone=phone).exists():
                    exists = True
                elif email and Lead.objects.filter(email=email).exists():
                    exists = True
                    
                if exists:
                    stats["duplicates"] += 1
                    continue
                
                # Clean budget
                try:
                    if isinstance(budget_raw, str):
                        budget = float(re.sub(r'[^\d.]', '', budget_raw)) if budget_raw else 0
                    else:
                        budget = float(budget_raw) if budget_raw else 0
                except (ValueError, TypeError):
                    budget = 0

                # Create Lead
                with transaction.atomic():
                    lead = Lead.objects.create(
                        name=name or f"Lead {phone or email}",
                        phone=phone,
                        email=email,
                        location=location,
                        budget=budget,
                        source=source_raw or "Google Sheet",
                        status="NEW",
                        assigned_to=default_assignee
                    )
                    
                    # Create Timeline Log
                    ActivityTimeline.objects.create(
                        lead=lead,
                        action="Lead Created (Google Sheet Sync)",
                        notes=f"Automatically imported from Google Sheet. Initial Source: {source_raw}",
                        performed_by=default_assignee
                    )
                    
                    # Parity: Schedule callback if possible
                    try:
                        schedule_callback_followup(lead, "Google Sheet sync automated follow-up.")
                    except Exception as e:
                        logger.warning(f"Failed to schedule follow-up for lead {lead.id}: {str(e)}")
                    
                stats["created"] += 1
                
            except Exception as e:
                logger.error(f"Error processing row {row}: {str(e)}")
                stats["errors"] += 1
                
        return stats
