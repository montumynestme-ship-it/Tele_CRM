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


DEFAULT_NOT_INCLUDED = [
    "Electrical automation",
    "VRV / AC systems",
    "Home appliances",
    "Structural construction work",
    "Washroom closet fittings",
    "Any item not mentioned in quotation",
]

PACKAGE_DETAILS = [
    (
        "Economic",
        [
            "Laminate finish in all areas.",
            "Specified brand raw materials with warranty support.",
            "Strong and durable execution as standard.",
        ],
    ),
    (
        "Semi-Luxury Interior",
        [
            "Duco/veneer for living area and master bedroom.",
            "Acrylic finish in kitchen; laminate in other areas.",
            "Imported highlight laminates with premium raw materials.",
        ],
    ),
    (
        "Full-Luxury Interior",
        [
            "PU-Duco, veneer, acrylic and luxury highlighted laminates.",
            "High-end brand materials with maximum warranties.",
            "Luxury aesthetics with top durability and finish quality.",
        ],
    ),
]

BRAND_LOGO_PATHS = [
    r"C:\Users\Admin\.cursor\projects\c-Program-Files-Odoo-19-0-20260411-server-odoo-addons-interior-design-management\assets\c__Users_Admin_AppData_Roaming_Cursor_User_workspaceStorage_db57d6c9e1f7510e8f464991894dc193_images_image-7da59e37-c9dd-4aa4-a461-03c211a1c897.png",
    r"C:\Users\Admin\.cursor\projects\c-Program-Files-Odoo-19-0-20260411-server-odoo-addons-interior-design-management\assets\c__Users_Admin_AppData_Roaming_Cursor_User_workspaceStorage_db57d6c9e1f7510e8f464991894dc193_images_image-fd12b7cc-aa54-409b-af14-9088b2e28bbb.png",
    r"C:\Users\Admin\.cursor\projects\c-Program-Files-Odoo-19-0-20260411-server-odoo-addons-interior-design-management\assets\c__Users_Admin_AppData_Roaming_Cursor_User_workspaceStorage_db57d6c9e1f7510e8f464991894dc193_images_image-156b7822-3d8e-4a68-b17b-abf73c31f5a9.png",
    r"C:\Users\Admin\.cursor\projects\c-Program-Files-Odoo-19-0-20260411-server-odoo-addons-interior-design-management\assets\c__Users_Admin_AppData_Roaming_Cursor_User_workspaceStorage_db57d6c9e1f7510e8f464991894dc193_images_image-98957b53-c1e1-4edd-816a-c489e55229e3.png",
    r"C:\Users\Admin\.cursor\projects\c-Program-Files-Odoo-19-0-20260411-server-odoo-addons-interior-design-management\assets\c__Users_Admin_AppData_Roaming_Cursor_User_workspaceStorage_db57d6c9e1f7510e8f464991894dc193_images_image-a557ae29-56eb-40c6-b068-06dccb937fbc.png",
    r"C:\Users\Admin\.cursor\projects\c-Program-Files-Odoo-19-0-20260411-server-odoo-addons-interior-design-management\assets\c__Users_Admin_AppData_Roaming_Cursor_User_workspaceStorage_db57d6c9e1f7510e8f464991894dc193_images_image-7fb20a18-b709-48f2-9682-6280cb6242b2.png",
    r"C:\Users\Admin\.cursor\projects\c-Program-Files-Odoo-19-0-20260411-server-odoo-addons-interior-design-management\assets\c__Users_Admin_AppData_Roaming_Cursor_User_workspaceStorage_db57d6c9e1f7510e8f464991894dc193_images_image-6f6e79b3-8b56-4ed2-8ad9-ad3ea18de613.png",
    r"C:\Users\Admin\.cursor\projects\c-Program-Files-Odoo-19-0-20260411-server-odoo-addons-interior-design-management\assets\c__Users_Admin_AppData_Roaming_Cursor_User_workspaceStorage_db57d6c9e1f7510e8f464991894dc193_images_image-0fbd2157-2f4b-42b6-b67b-8e0e0933e692.png",
    r"C:\Users\Admin\.cursor\projects\c-Program-Files-Odoo-19-0-20260411-server-odoo-addons-interior-design-management\assets\c__Users_Admin_AppData_Roaming_Cursor_User_workspaceStorage_db57d6c9e1f7510e8f464991894dc193_images_image-12ac2519-b9f9-4c89-90d2-ea20db2fa1c7.png",
]
MAIN_COMPANY_LOGO_PATH = r"C:\Users\Admin\.cursor\projects\c-Program-Files-Odoo-19-0-20260411-server-odoo-addons-interior-design-management\assets\c__Users_Admin_AppData_Roaming_Cursor_User_workspaceStorage_db57d6c9e1f7510e8f464991894dc193_images_mynest-log-1-e1644572796296-300x168-57405ca3-585e-4c54-a0c2-8a524c54287a.png"


def _money(value: Decimal) -> str:
    return f"INR {value:,.2f}"


def _section_table(section):
    data = [["Description", "Qty", "Unit Price", "Total", "Remarks"]]
    section_total = Decimal("0.00")
    for item in section.items.all():
        section_total += item.total_price
        data.append(
            [
                item.description,
                str(item.quantity),
                _money(item.unit_price),
                _money(item.total_price),
                item.remarks or "-",
            ]
        )
    data.append(["Section Total", "", "", "", _money(section_total)])
    table = Table(data, colWidths=[3.3 * inch, 0.8 * inch, 1.1 * inch, 1.1 * inch, 1.0 * inch], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PDF_BG_SOFT),
                ("GRID", (0, 0), (-1, -1), 0.35, PDF_BORDER),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("ALIGN", (2, 1), (3, -1), "RIGHT"),
            ]
        )
    )
    return table, section_total


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

    # Room-wise quotation
    elements.append(Paragraph("ROOM-WISE QUOTATION", section_style))
    interior_total = Decimal("0.00")
    civil_total = Decimal("0.00")

    for section in quotation.sections.all():
        if section.section_name.strip().lower() == "mynest includings":
            display_name = "INCLUSIONS"
        else:
            display_name = section.section_name
        if not section.items.exists():
            continue
        elements.append(Paragraph(section.section_name.upper(), section_style))
        table, section_total = _section_table(section)
        if section_total <= 0:
            continue
        elements[-1] = Paragraph(display_name.upper(), section_style)
        elements.append(table)
        elements.append(Spacer(1, 6))
        if "civil" in section.section_name.lower():
            civil_total += section_total
        else:
            interior_total += section_total

    # Extra civil work model items
    if quotation.civil_work_items.exists():
        elements.append(Paragraph("CIVIL WORK", section_style))
        civil_rows = [["Description", "Qty", "Unit Price", "Total", "Remarks"]]
        for idx, item in enumerate(quotation.civil_work_items.all(), start=1):
            civil_rows.append([item.description, "1", _money(item.price), _money(item.price), item.remarks or "-"])
            civil_total += item.price
        civil_table = Table(civil_rows, colWidths=[3.3 * inch, 0.8 * inch, 1.1 * inch, 1.1 * inch, 1.0 * inch], repeatRows=1)
        civil_table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.35, PDF_BORDER), ("BACKGROUND", (0, 0), (-1, 0), PDF_BG_SOFT)]))
        elements.append(civil_table)
        elements.append(Spacer(1, 8))

    # Project summary
    total_project = interior_total + civil_total
    elements.append(Paragraph("PROJECT SUMMARY", section_style))
    summary_table = Table(
        [
            ["Interior Work Total", _money(interior_total)],
            ["Civil Work Total", _money(civil_total)],
            ["GRAND TOTAL", _money(total_project)],
        ],
        colWidths=[4.5 * inch, 2.5 * inch],
    )
    summary_table.setStyle(
        TableStyle([("GRID", (0, 0), (-1, -1), 0.5, PDF_BORDER), ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"), ("BACKGROUND", (0, 0), (-1, 0), PDF_BG_SOFT)])
    )
    summary_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
                ("TEXTCOLOR", (0, 2), (-1, 2), PDF_ACCENT),
                ("FONTSIZE", (0, 2), (-1, 2), 12),
                ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#ECFDF5")),
            ]
        )
    )
    elements.append(summary_table)
    elements.append(Spacer(1, 8))

    # Package pricing summary (dynamic based on saved base amount)
    effective_base = quotation.base_amount if quotation.base_amount else interior_total
    semi_amount = effective_base + (effective_base * Decimal("0.27"))
    full_amount = effective_base + (effective_base * Decimal("0.54"))
    selected_code = quotation.selected_package or "BASIC"
    selected_amount = effective_base
    selected_label = "LAMINATED (BASIC-ECO)"
    if selected_code == "SEMI":
        selected_amount = semi_amount
        selected_label = "DUCO/VENEER/LAMINATE (Semi-Luxury Interior)"
    elif selected_code == "FULL":
        selected_amount = full_amount
        selected_label = "PU-DUCO/VENEER/ACRYLIC/H.LAM (Full-Luxury Interior)"
    elif quotation.package_amount:
        selected_amount = quotation.package_amount

    elements.append(Paragraph("INTERIOR PACKAGE PRICING", section_style))
    package_table = Table(
        [
            ["LAMINATED (BASIC-ECO)", _money(effective_base)],
            ["DUCO/VENEER/LAMINATE (Semi-Luxury Interior)", _money(semi_amount)],
            ["PU-DUCO/VENEER/ACRYLIC/H.LAM (Full-Luxury Interior)", _money(full_amount)],
            [f"Selected Package: {selected_label}", _money(selected_amount)],
        ],
        colWidths=[5.5 * inch, 1.5 * inch],
    )
    package_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.35, PDF_BORDER),
                ("BACKGROUND", (0, 0), (-1, 0), PDF_BG_SOFT),
                ("FONTNAME", (0, 3), (-1, 3), "Helvetica-Bold"),
            ]
        )
    )
    elements.append(package_table)
    elements.append(Spacer(1, 8))

    # Package options
    elements.append(Paragraph("IN DETAIL", section_style))
    package_detail_rows = [[Paragraph("<b>Package</b>", normal), Paragraph("<b>Description</b>", normal)]]
    for title, bullets in PACKAGE_DETAILS:
        bullet_text = "<br/>".join([f"- {line}" for line in bullets])
        package_detail_rows.append([Paragraph(f"<b>{title}</b>", normal), Paragraph(bullet_text, normal)])
    package_details_table = Table(package_detail_rows, colWidths=[1.8 * inch, 5.2 * inch], repeatRows=1)
    package_details_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.3, PDF_BORDER),
                ("BACKGROUND", (0, 0), (-1, 0), PDF_BG_SOFT),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    elements.append(package_details_table)
    elements.append(Spacer(1, 8))

    # Payment terms
    elements.append(Paragraph("PAYMENT TERMS", section_style))
    payment_rows = [["Stage", "Percentage", "Amount", "Description"]]
    if quotation.payment_plans.exists():
        for p in quotation.payment_plans.all():
            payment_rows.append([p.payment_stage, f"{p.percentage}%", _money(p.amount), p.description or "-"])
    else:
        payment_rows.extend(
            [
                ["Booking Amount", "-", _money(total_project * Decimal("0.10")), "Initial booking"],
                ["Phase 1", "65", _money(total_project * Decimal("0.65")), "Wiring, base structures, ceiling and civil work"],
                ["Phase 2", "35", _money(total_project * Decimal("0.35")), "Shutters, paint, hardware, light fittings"],
                ["Before Handover", "-", _money(total_project * Decimal("0.05")), "Final finishing and closure"],
            ]
        )
    payment_table = Table(payment_rows, colWidths=[1.7 * inch, 1.1 * inch, 1.5 * inch, 2.7 * inch], repeatRows=1)
    payment_table.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.35, PDF_BORDER), ("BACKGROUND", (0, 0), (-1, 0), PDF_BG_SOFT)]))
    elements.append(payment_table)
    elements.append(Spacer(1, 8))

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
    for idx, line in enumerate(DEFAULT_NOT_INCLUDED, start=1):
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
