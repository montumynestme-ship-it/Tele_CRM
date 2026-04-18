import os
from decimal import Decimal

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .models import CompanyDetails, Quotation

PDF_PRIMARY = colors.HexColor("#1E3A8A")
PDF_BG_SOFT = colors.HexColor("#F1F5F9")
PDF_BORDER = colors.HexColor("#E5E7EB")
PDF_TEXT_SECONDARY = colors.HexColor("#64748B")
PDF_ACCENT = colors.HexColor("#10B981")


BRAND_LOGO_DIR = os.path.join(settings.BASE_DIR, "static", "images", "brand_logos")
BRAND_LOGO_PATHS = [
    os.path.join(BRAND_LOGO_DIR, "brand_7da59e37-c9dd-4aa4-a461-03c211a1c897.png"),
    os.path.join(BRAND_LOGO_DIR, "brand_fd12b7cc-aa54-409b-af14-9088b2e28bbb.png"),
    os.path.join(BRAND_LOGO_DIR, "brand_156b7822-3d8e-4a68-b17b-abf73c31f5a9.png"),
    os.path.join(BRAND_LOGO_DIR, "brand_98957b53-c1e1-4edd-816a-c489e55229e3.png"),
    os.path.join(BRAND_LOGO_DIR, "brand_a557ae29-56eb-40c6-b068-06dccb937fbc.png"),
    os.path.join(BRAND_LOGO_DIR, "brand_7fb20a18-b709-48f2-9682-6280cb6242b2.png"),
    os.path.join(BRAND_LOGO_DIR, "brand_6f6e79b3-8b56-4ed2-8ad9-ad3ea18de613.png"),
    os.path.join(BRAND_LOGO_DIR, "brand_0fbd2157-2f4b-42b6-b67b-8e0e0933e692.png"),
    os.path.join(BRAND_LOGO_DIR, "brand_12ac2519-b9f9-4c89-90d2-ea20db2fa1c7.png"),
]
MAIN_COMPANY_LOGO_PATH = os.path.join(BRAND_LOGO_DIR, "company_logo.png")

STANDARD_MATERIALS = [
    ("Paint Work", "Asian Paint - Royal"),
    ("Plywood", "BWR and BWP (Kitchen & washroom base) - 14 years warranty"),
    ("Laminate", "2K premium finish"),
    ("Veneer", "3K decorative finish"),
    ("Acrylic", "5K high gloss finish"),
    ("Hardware - Hinges", "HIKO / Hafele / Hettich / Godrej"),
    ("Hardware - Locks", "Godrej - 2 years warranty"),
    ("Hardware - Channels", "Tandem / HIKO / Hettich / Hafele"),
    ("Hardware - Knobs/Handles", "Selection range (₹150 - ₹500)"),
    ("Fabric", "Selection range (₹300 - ₹500)"),
    ("False Ceiling", "Gypsum - 10 years warranty"),
    ("Lights", "Panel and COB - Philips / Syska / Astro - 2 years warranty"),
    ("Wires", "RR Kabel / Finolex - 14 years warranty"),
]

MYNEST_INCLUSIONS = [
    "Space management and furniture layout planning",
    "3D Photorealistic (360°) Interior Designing",
    "Comprehensive 2-Layer Execution management",
    "Professional Labour Handling & site coordination",
    "Post-work Debris Cleaning & waste removal",
    "Basic Deep Cleaning before handover",
    "Floor Protection cover during execution",
    "2 years of dedicated Service Warranty",
]


def _items_table(items):
    data = [["No.", "Description", "Remarks"]]
    for idx, item in enumerate(items, start=1):
        data.append([str(idx), item.description, item.remarks or "-"] )
    
    table = Table(data, colWidths=[0.6 * inch, 4.4 * inch, 2.0 * inch], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PDF_BG_SOFT),
                ("GRID", (0, 0), (-1, -1), 0.35, PDF_BORDER),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    return table


def _company_or_default(company):
    if company:
        return company
    fallback = CompanyDetails()
    fallback.company_name = "Mynest.me Design Studio"
    fallback.gst_number = "24DPUPS9833D1Z8"
    fallback.bank_name = "Kotak Bank"
    fallback.account_number = "3549713882"
    fallback.ifsc_code = "KKBK0002560"
    fallback.business_address = (
        "B-707, Infinity Tower, Near Ramada Hotel, Corporate Road, "
        "Prahladnagar, Ahmedabad, Gujarat - 380015"
    )
    fallback.contact_number = "+91 76655 88577, +91 74054 81053"
    fallback.email = "me.mynest@gmail.com"
    return fallback


def _brand_logos_table():
    logos = []
    for path in BRAND_LOGO_PATHS:
        if os.path.exists(path):
            try:
                logos.append(Image(path, width=1.5 * inch, height=0.7 * inch))
            except Exception:
                continue
    if not logos:
        return None

    while len(logos) < 9:
        logos.append("")
    rows = [logos[0:3], logos[3:6], logos[6:9]]
    table = Table(rows, colWidths=[2.3 * inch, 2.3 * inch, 2.3 * inch], rowHeights=[0.85 * inch] * 3)
    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.2, PDF_BORDER),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    return table


class NumberedCanvas:
    def __init__(self, *args, **kwargs):
        from reportlab.pdfgen import canvas
        self._canvas = canvas.Canvas(*args, **kwargs)
        self._saved_page_states = []

    def __getattr__(self, name):
        return getattr(self._canvas, name)

    def showPage(self):
        self._saved_page_states.append(dict(self._canvas.__dict__))
        self._canvas._startPage()

    def save(self):
        page_count = len(self._saved_page_states)
        for state in self._saved_page_states:
            self._canvas.__dict__.update(state)
            self.draw_page_number(page_count)
            self._canvas.showPage()
        self._canvas.save()

    def draw_page_number(self, page_count):
        self._canvas.setFont("Helvetica", 9)
        self._canvas.setFillColor(PDF_TEXT_SECONDARY)
        self._canvas.drawRightString(A4[0] - 30, 18, f"Page {self._canvas._pageNumber} of {page_count}")


def generate_quotation_pdf(quotation: Quotation) -> str:
    company = _company_or_default(CompanyDetails.objects.first())
    filename = f"dynamic_quotation_{quotation.id}.pdf"
    folder = os.path.join(settings.MEDIA_ROOT, "quotations")
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, filename)

    doc = SimpleDocTemplate(file_path, pagesize=A4, leftMargin=28, rightMargin=28, topMargin=24, bottomMargin=24)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("QTitle", parent=styles["Heading1"], alignment=1, fontSize=16, spaceAfter=8)
    subtitle_style = ParagraphStyle("QSub", parent=styles["Normal"], alignment=1, textColor=PDF_TEXT_SECONDARY, spaceAfter=6)
    section_style = ParagraphStyle("QSection", parent=styles["Heading3"], fontSize=12, textColor=PDF_PRIMARY, spaceBefore=8, spaceAfter=6)
    normal = styles["Normal"]
    elements = []

    # Header and branding
    logo_added = False
    if company.logo:
        try:
            elements.append(Image(company.logo.path, width=1.4 * inch, height=0.8 * inch))
            logo_added = True
        except Exception:
            pass
    if not logo_added and os.path.exists(MAIN_COMPANY_LOGO_PATH):
        try:
            elements.append(Image(MAIN_COMPANY_LOGO_PATH, width=1.8 * inch, height=1.0 * inch))
        except Exception:
            pass
    header_table = Table(
        [[
            Paragraph(f"<b>{company.company_name}</b><br/>{company.business_address}<br/>Phone: {company.contact_number} | Email: {company.email}<br/>GST: {company.gst_number}", normal)
        ]],
        colWidths=[7.0 * inch],
    )
    header_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PDF_BG_SOFT), ("GRID", (0, 0), (-1, -1), 0.4, PDF_BORDER), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8)]))
    elements.append(header_table)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("INTERIOR DESIGN QUOTATION", ParagraphStyle("QTitleBlue", parent=title_style, textColor=PDF_PRIMARY)))

    # Client details
    elements.append(Paragraph("CLIENT DETAILS", section_style))
    detail_rows = [
        ["Quotation No", quotation.quotation_number, "Date", quotation.quotation_date.strftime("%d-%m-%Y")],
        ["Client Name", quotation.client_name, "Client Phone", quotation.client_phone or "-"],
        ["Client Email", quotation.client_email or "-", "Project Type", quotation.project_type or "-"],
        ["Project Location", quotation.project_location or "-", "Designer Name", quotation.designer_name or "-"],
    ]
    detail_table = Table(detail_rows, colWidths=[1.3 * inch, 2.2 * inch, 1.3 * inch, 2.2 * inch])
    detail_table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.3, PDF_BORDER), ("FONTNAME", (0, 0), (-1, -1), "Helvetica"), ("BACKGROUND", (0, 0), (-1, 0), PDF_BG_SOFT)]))
    elements.append(detail_table)
    elements.append(Spacer(1, 10))

    # 1. SECTION WISE INTERIOR ITEMS
    for section in quotation.sections.all():
        items = section.items.all()
        if not items.exists():
            continue
            
        elements.append(Paragraph(section.section_name.upper(), section_style))
        elements.append(_items_table(items))
        elements.append(Spacer(1, 10))
    
    elements.append(Spacer(1, 5))

    # 2. MATERIAL LIST (Fixed Standards)
    elements.append(Paragraph("MATERIAL LIST", section_style))
    std_data = [["Category", "Specifications / Brands"]]
    std_data.extend([
        ("Paint Work", "Asian Paint - Royale / Luxury Emulsion"),
        ("Plywood", "BWR and BWP (Kitchen & washroom base) - 14 years warranty"),
        ("Laminate", "1.0mm - 1.2mm Premium finish (2K range)"),
        ("Veneer", "3.5mm - 4.0mm Decorative finish (3K range)"),
        ("Acrylic", "1.5mm High gloss Anti-scratch (5K range)"),
        ("Hardware Brands", "Hettich / Hafele / Godrej / E-Square"),
        ("Hardware - Hinges", "Auto-close soft-touch hinges"),
        ("Hardware - Channels", "Tandem boxes / Soft-close telescopic channels"),
        ("Lighting", "Philips / Syska / Astro - 2 years warranty"),
        ("Wiring", "RR Kabel / Finolex - 14 years warranty"),
        ("False Ceiling", "Gypsum / POP design with 10 years warranty"),
    ])
    std_table = Table(std_data, colWidths=[2.5 * inch, 4.5 * inch])
    std_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, PDF_BORDER),
        ("BACKGROUND", (0, 0), (-1, 0), PDF_BG_SOFT),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    elements.append(std_table)
    elements.append(Spacer(1, 10))

    # 3. MYNEST INCLUSIONS
    elements.append(Paragraph("MYNEST INCLUSIONS", section_style))
    inc_data = [["No.", "Description"]]
    for idx, inc in enumerate(MYNEST_INCLUSIONS, start=1):
        inc_data.append([str(idx), inc])
    inc_table = Table(inc_data, colWidths=[0.6 * inch, 6.4 * inch], repeatRows=1)
    inc_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.3, PDF_BORDER),
        ("BACKGROUND", (0, 0), (-1, 0), PDF_BG_SOFT),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    elements.append(inc_table)
    elements.append(Spacer(1, 10))

    # 4. INTERIOR PACKAGE PRICING OPTIONS
    elements.append(Paragraph("INTERIOR PACKAGE PRICING OPTIONS", section_style))
    base = float(quotation.base_amount)
    semi = base * 1.27
    full = base * 1.54
    sel = quotation.selected_package
    data = [
        ["Option", "Package Details", "Amount (INR)"],
        ["BASIC-ECO", "LAMINATED", f"{base:,.2f}"],
        ["SEMI-LUXURY", "DUCO / VENEER / LAMINATE", f"{semi:,.2f}"],
        ["FULL-LUXURY", "PU-DUCO / VENEER / ACRYLIC / H.LAM", f"{full:,.2f}"],
    ]
    table = Table(data, colWidths=[1.8 * inch, 3.4 * inch, 1.8 * inch])
    style_list = [
        ("GRID", (0, 0), (-1, -1), 0.5, PDF_BORDER),
        ("BACKGROUND", (0, 0), (-1, 0), PDF_BG_SOFT),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]
    if sel == "BASIC":
        style_list.append(("BACKGROUND", (0, 1), (-1, 1), colors.lightyellow))
        style_list.append(("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"))
    elif sel == "SEMI":
        style_list.append(("BACKGROUND", (0, 2), (-1, 2), colors.lightyellow))
        style_list.append(("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"))
    elif sel == "FULL":
        style_list.append(("BACKGROUND", (0, 3), (-1, 3), colors.lightyellow))
        style_list.append(("FONTNAME", (0, 3), (-1, 3), "Helvetica-Bold"))
    table.setStyle(TableStyle(style_list))
    elements.append(table)
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(f"* Selected Package: <b>{dict(Quotation.PACKAGE_CHOICES).get(sel)}</b>", ParagraphStyle("SmallMsg", parent=normal, fontSize=8, textColor=PDF_PRIMARY)))
    elements.append(Spacer(1, 12))

    # Civil work (Commented out as requested)
    """
    if quotation.civil_work_items.exists():
        elements.append(Paragraph("CIVIL WORK", section_style))
        civil_rows = [["Description", "Remarks"]]
        for item in quotation.civil_work_items.all():
            civil_rows.append([item.description, item.remarks or "-"])
        civil_table = Table(civil_rows, colWidths=[5.0 * inch, 2.0 * inch], repeatRows=1)
        civil_table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.35, PDF_BORDER), ("BACKGROUND", (0, 0), (-1, 0), PDF_BG_SOFT)]))
        elements.append(civil_table)
        elements.append(Spacer(1, 10))
    """

    # Payment terms
    elements.append(Paragraph("PAYMENT TERMS", section_style))
    payment_rows = [["Stage", "Percentage", "Description"]]
    if quotation.payment_plans.exists():
        for p in quotation.payment_plans.all():
            payment_rows.append([p.payment_stage, f"{p.percentage}%", p.description or "-"])
    else:
        payment_rows.extend(
            [
                ["Booking Amount", "10%", "Initial booking"],
                ["Phase 1", "65%", "Wiring, base structures, ceiling and civil work"],
                ["Phase 2", "20%", "Shutters, paint, hardware, light fittings"],
                ["Before Handover", "5%", "Final finishing and closure"],
            ]
        )
    payment_table = Table(payment_rows, colWidths=[2.0 * inch, 1.5 * inch, 3.5 * inch], repeatRows=1)
    payment_table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.35, PDF_BORDER), ("BACKGROUND", (0, 0), (-1, 0), PDF_BG_SOFT)]))
    elements.append(payment_table)
    elements.append(Spacer(1, 10))

    # Bank details
    elements.append(Paragraph("BANK DETAILS", section_style))
    bank_table = Table(
        [
            ["Account Name", company.company_name],
            ["Account Number", company.account_number],
            ["IFSC Code", company.ifsc_code],
            ["Bank", company.bank_name],
        ],
        colWidths=[2 * inch, 5 * inch],
    )
    bank_table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.3, PDF_BORDER)]))
    elements.append(bank_table)
    elements.append(Spacer(1, 8))

    # Not included
    elements.append(Paragraph("NOT INCLUDED", section_style))
    not_included = [
        "Electrical automation",
        "VRV / AC systems",
        "Home appliances",
        "Structural construction work",
        "Washroom closet fittings",
        "Any item not mentioned in quotation",
    ]
    for idx, line in enumerate(not_included, start=1):
        elements.append(Paragraph(f"{idx}. {line}", normal))
    elements.append(Spacer(1, 10))

    # Footer
    logos_table = _brand_logos_table()
    signatory_block = Paragraph("<b>Authorized Signatory</b><br/><br/>____________________", normal)
    stamp_block = Paragraph("<b>Company Stamp</b><br/><br/>____________________", normal)
    footer_rows = [[signatory_block, stamp_block]]
    if logos_table:
        footer_rows.append([logos_table, ""])
    footer_rows.append([Paragraph("Thank you for trusting us with your dream space.", ParagraphStyle("Thanks", parent=normal, textColor=PDF_TEXT_SECONDARY)), ""])
    footer_table = Table(footer_rows, colWidths=[5.0 * inch, 2.0 * inch])
    footer_style = [("VALIGN", (0, 0), (-1, -1), "TOP")]
    if logos_table:
        footer_style.append(("SPAN", (0, 1), (1, 1)))
        footer_style.append(("SPAN", (0, 2), (1, 2)))
    else:
        footer_style.append(("SPAN", (0, 1), (1, 1)))
    footer_table.setStyle(TableStyle(footer_style))
    elements.append(footer_table)
    elements.append(Spacer(1, 6))

    doc.build(elements, canvasmaker=NumberedCanvas)
    return f"quotations/{filename}"
