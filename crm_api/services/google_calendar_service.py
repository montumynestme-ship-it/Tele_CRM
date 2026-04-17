import os
import logging
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/calendar"]
logger = logging.getLogger(__name__)


class GoogleCalendarConfigError(Exception):
    pass


def _calendar_client():
    creds = None
    
    # 1. Try OAuth2 Refresh Token
    if settings.GOOGLE_REFRESH_TOKEN:
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
                logger.warning("GOOGLE_REFRESH_TOKEN is present but invalid.")
        except Exception as e:
            logger.error("Google OAuth2 Initialization Failed: %s. Check if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are correct.", str(e))
            creds = None
    else:
        logger.info("GOOGLE_REFRESH_TOKEN is missing. This is required for personal calendar sync.")

    # 2. Fallback to Service Account
    if not creds and settings.GOOGLE_SERVICE_ACCOUNT_FILE:
        if os.path.exists(settings.GOOGLE_SERVICE_ACCOUNT_FILE):
            try:
                import json
                with open(settings.GOOGLE_SERVICE_ACCOUNT_FILE, 'r') as f:
                    data = json.load(f)
                    if data.get('type') == 'service_account':
                        creds = service_account.Credentials.from_service_account_file(
                            settings.GOOGLE_SERVICE_ACCOUNT_FILE,
                            scopes=SCOPES,
                        )
                        if settings.GOOGLE_CALENDAR_DELEGATED_USER:
                            creds = creds.with_subject(settings.GOOGLE_CALENDAR_DELEGATED_USER)
                    else:
                        logger.error("The file %s is an OAuth Client Secret, not a Service Account JSON. Please use the Refresh Token method instead.", settings.GOOGLE_SERVICE_ACCOUNT_FILE)
            except Exception as e:
                logger.error("Service Account Loading Failed: %s", str(e))
        else:
            logger.error("Service account file not found at: %s", settings.GOOGLE_SERVICE_ACCOUNT_FILE)

    if not creds:
        error_msg = ("Google Calendar Sync Failed: No valid credentials. "
                     "Please run 'python generate_token.py' to get a Refresh Token and add it to your .env file.")
        raise GoogleCalendarConfigError(error_msg)
    
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def _calendar_id() -> str:
    return settings.GOOGLE_CALENDAR_ID or "primary"


def _build_event_payload(meeting) -> dict:
    start_time = meeting.date
    if timezone.is_naive(start_time):
        start_time = timezone.make_aware(start_time)
    end_time = meeting.date + timedelta(hours=1)
    if timezone.is_naive(end_time):
        end_time = timezone.make_aware(end_time)
    
    client_name = meeting.client_name or meeting.lead.name
    meeting_type_label = meeting.get_type_display() if hasattr(meeting, 'get_type_display') else str(meeting.type)
    
    # Custom summary format: "[Client Name] - [Meeting Type] Meeting"
    summary = f"{client_name} - {meeting_type_label}"
    if "meeting" not in summary.lower():
        summary += " Meeting"

    attendees = set()
    if meeting.assigned_user and meeting.assigned_user.email:
        attendees.add(meeting.assigned_user.email)
    if meeting.created_by and meeting.created_by.email:
        attendees.add(meeting.created_by.email)
    if meeting.lead.assigned_to and meeting.lead.assigned_to.email:
        attendees.add(meeting.lead.assigned_to.email)

    User = get_user_model()
    for admin_email in User.objects.filter(role="ADMIN").exclude(email="").values_list("email", flat=True):
        attendees.add(admin_email)

    return {
        "summary": summary,
        "description": (
            f"Client: {client_name}\n"
            f"Meeting Type: {meeting_type_label}\n"
            f"Notes: {meeting.notes or 'No additional notes.'}\n\n"
            "Automatically scheduled via TeleCRM"
        ),
        "start": {"dateTime": start_time.isoformat(), "timeZone": settings.GOOGLE_CALENDAR_TIMEZONE},
        "end": {"dateTime": end_time.isoformat(), "timeZone": settings.GOOGLE_CALENDAR_TIMEZONE},
        "attendees": [{"email": email} for email in sorted(attendees)],
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": 30},
                {"method": "popup", "minutes": 15},
                {"method": "popup", "minutes": 5},
            ],
        },
    }


def create_google_event(meeting) -> str | None:
    try:
        service = _calendar_client()
        event = service.events().insert(calendarId=_calendar_id(), body=_build_event_payload(meeting)).execute()
        return event.get("id")
    except Exception as exc:  # noqa: BLE001
        logger.error("Google Calendar error creating event for meeting %s: %s", meeting.pk, str(exc))
        raise


def update_google_event(meeting) -> str | None:
    if not meeting.google_calendar_event_id:
        return None
    try:
        service = _calendar_client()
        event = (
            service.events()
            .update(calendarId=_calendar_id(), eventId=meeting.google_calendar_event_id, body=_build_event_payload(meeting))
            .execute()
        )
        return event.get("id")
    except Exception as exc:  # noqa: BLE001
        logger.error("Google Calendar error updating event for meeting %s: %s", meeting.pk, str(exc))
        raise


def upsert_meeting_event(meeting) -> str | None:
    if meeting.google_calendar_event_id:
        return update_google_event(meeting)
    return create_google_event(meeting)


def delete_meeting_event(*, event_id: str) -> None:
    if not event_id:
        return
    try:
        service = _calendar_client()
        service.events().delete(calendarId=_calendar_id(), eventId=event_id).execute()
    except Exception as exc:  # noqa: BLE001
        logger.error("Google Calendar error deleting event %s: %s", event_id, str(exc))
        raise
