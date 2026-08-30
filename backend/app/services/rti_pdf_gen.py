"""
Accountable Platform — RTI PDF Generation Service
==================================================
Automatically drafts a Right to Information (RTI) request PDF on Day 14
of non-resolution for a public complaint.

The generated PDF includes:
  - Applicant details (submitter or platform proxy)
  - Public Information Officer (PIO) address
  - Structured RTI questions derived from the complaint description,
    linked tender data, and PFMS fund-flow anomalies.
  - Declaration & date section

Libraries used
--------------
  - reportlab  : PDF layout engine (no LaTeX dependency).
  - jinja2     : Plain-text template rendering for question blocks.

Entry point
-----------
    pdf_path = await generate_rti_pdf(complaint: Complaint) -> str

Called by:
  - POST /api/v1/complaints/{id}/rti   (manual trigger)
  - Day-14 scheduler hook              (automatic trigger)
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from jinja2 import Environment, BaseLoader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.database.db import async_session_factory
from app.database.models import Complaint, RTIRequest, TenderMatch
from app.config import settings

from sqlalchemy import select
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Output directory
# ---------------------------------------------------------------------------

RTI_OUTPUT_DIR = Path(settings.RTI_PDF_DIR).resolve()
RTI_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Jinja2 template for RTI question block
# ---------------------------------------------------------------------------

_RTI_QUESTIONS_TEMPLATE = """
Under the Right to Information Act, 2005, I hereby request the following information:

1. Please provide certified copies of all work orders, agreements, and contracts
   related to the project/work described as:
   "{{ complaint.title }}"
   at or near {{ location }}.

2. Please provide the complete PFMS fund flow details — including amounts sanctioned,
   released, and utilised — for the above project, broken down by financial year.

3. Please provide the name, registration number, PAN, and GST details of the
   contractor(s) awarded this work, along with their bid amounts.

{% if tender_refs %}
4. The following public tender(s) appear related to this complaint. Please confirm
   whether work under these tenders was completed as per specifications:
   {% for t in tender_refs %}
   - Tender ID: {{ t.tender_id }} | Title: {{ t.title }} | Dept: {{ t.department or 'N/A' }}
   {% endfor %}
{% endif %}

5. Please provide inspection / quality-certification reports, if any, certifying
   completion of the above work to the contractual standard.

6. Please provide the names and designations of officials who inspected, certified,
   and authorised payment for the above work.

7. If the work is pending or incomplete, please provide the reason for delay,
   the revised completion date, and the action taken against the contractor.

8. Please provide copies of any grievances, representations, or complaints already
   received regarding the above project, and the action taken thereon.
"""

_jinja_env = Environment(loader=BaseLoader(), autoescape=False)
_rti_question_template = _jinja_env.from_string(_RTI_QUESTIONS_TEMPLATE)


# ---------------------------------------------------------------------------
# PDF style helpers
# ---------------------------------------------------------------------------

def _build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "RTITitle",
            parent=base["Title"],
            fontSize=16,
            leading=20,
            spaceAfter=6,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#1a237e"),
        ),
        "subtitle": ParagraphStyle(
            "RTISubtitle",
            parent=base["Normal"],
            fontSize=11,
            leading=14,
            spaceAfter=4,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#283593"),
        ),
        "section_header": ParagraphStyle(
            "RTISectionHeader",
            parent=base["Heading2"],
            fontSize=11,
            leading=14,
            spaceBefore=10,
            spaceAfter=4,
            textColor=colors.HexColor("#1a237e"),
            borderPad=2,
        ),
        "body": ParagraphStyle(
            "RTIBody",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            spaceAfter=4,
            alignment=TA_JUSTIFY,
        ),
        "label": ParagraphStyle(
            "RTILabel",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#424242"),
        ),
        "value": ParagraphStyle(
            "RTIValue",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            fontName="Helvetica-Bold",
        ),
        "footer": ParagraphStyle(
            "RTIFooter",
            parent=base["Normal"],
            fontSize=8,
            leading=10,
            alignment=TA_CENTER,
            textColor=colors.grey,
        ),
    }


# ---------------------------------------------------------------------------
# Helper: info table row
# ---------------------------------------------------------------------------

def _info_row(label: str, value: str, styles: dict) -> Table:
    data = [[Paragraph(label, styles["label"]), Paragraph(value or "—", styles["value"])]]
    tbl = Table(data, colWidths=[5 * cm, 12 * cm])
    tbl.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    return tbl


# ---------------------------------------------------------------------------
# Core PDF builder
# ---------------------------------------------------------------------------

def _build_pdf(
    output_path: str,
    complaint: Complaint,
    tender_refs: list[TenderMatch],
    pio_name: str,
    pio_address: str,
    applicant_name: str,
) -> None:
    """Render the RTI PDF to *output_path* using ReportLab."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"RTI Application — Complaint #{complaint.id}",
        author="Accountable Platform",
    )

    styles = _build_styles()
    story = []
    now_str = datetime.now(timezone.utc).strftime("%d %B %Y")

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------
    story.append(Paragraph("APPLICATION UNDER THE RIGHT TO INFORMATION ACT, 2005", styles["title"]))
    story.append(Paragraph("(Central / State Government — As Applicable)", styles["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1a237e")))
    story.append(Spacer(1, 8 * mm))

    # ------------------------------------------------------------------
    # Complaint meta
    # ------------------------------------------------------------------
    story.append(Paragraph("A. COMPLAINT REFERENCE", styles["section_header"]))
    story.append(_info_row("Complaint ID:", f"#{complaint.id}", styles))
    story.append(_info_row("Filed On:", complaint.created_at.strftime("%d %b %Y"), styles))
    story.append(_info_row("Platform Status:", complaint.status.value.replace("_", " ").title(), styles))
    story.append(_info_row("Days Since Filing:", str((datetime.now(timezone.utc) - complaint.created_at).days), styles))
    story.append(Spacer(1, 6 * mm))

    # ------------------------------------------------------------------
    # Addressing the PIO
    # ------------------------------------------------------------------
    story.append(Paragraph("B. ADDRESSED TO", styles["section_header"]))
    story.append(_info_row("To:", f"{pio_name}", styles))
    story.append(_info_row("Address:", pio_address, styles))
    story.append(_info_row("Date:", now_str, styles))
    story.append(Spacer(1, 6 * mm))

    # ------------------------------------------------------------------
    # Applicant
    # ------------------------------------------------------------------
    story.append(Paragraph("C. APPLICANT DETAILS", styles["section_header"]))
    story.append(_info_row("Name:", applicant_name, styles))
    story.append(
        _info_row(
            "Contact:",
            complaint.submitter_contact or "Via Accountable Platform",
            styles,
        )
    )
    story.append(Spacer(1, 6 * mm))

    # ------------------------------------------------------------------
    # Subject
    # ------------------------------------------------------------------
    story.append(Paragraph("D. SUBJECT", styles["section_header"]))
    subject_text = (
        f"Request for Information regarding public complaint: <b>{complaint.title}</b> "
        f"at or near {complaint.address or 'location as per GPS coordinates provided'}."
    )
    story.append(Paragraph(subject_text, styles["body"]))
    story.append(Spacer(1, 4 * mm))

    # ------------------------------------------------------------------
    # RTI Questions
    # ------------------------------------------------------------------
    story.append(Paragraph("E. INFORMATION SOUGHT", styles["section_header"]))

    location_str = complaint.address or f"Lat {complaint.latitude:.5f}, Lon {complaint.longitude:.5f}"

    # Render Jinja2 template
    rti_questions_text = _rti_question_template.render(
        complaint=complaint,
        location=location_str,
        tender_refs=[tm.tender for tm in tender_refs if tm.tender],
    )

    # Each line becomes a separate Paragraph for proper wrapping
    for line in rti_questions_text.strip().splitlines():
        stripped = line.strip()
        if stripped:
            story.append(Paragraph(stripped, styles["body"]))
        else:
            story.append(Spacer(1, 3 * mm))

    story.append(Spacer(1, 6 * mm))

    # ------------------------------------------------------------------
    # Original complaint text
    # ------------------------------------------------------------------
    story.append(Paragraph("F. ORIGINAL COMPLAINT DESCRIPTION", styles["section_header"]))
    story.append(Paragraph(complaint.description, styles["body"]))
    story.append(Spacer(1, 6 * mm))

    # ------------------------------------------------------------------
    # Declaration
    # ------------------------------------------------------------------
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("DECLARATION", styles["section_header"]))
    declaration = (
        "I state that the information sought does not fall within the restrictions "
        "contained in Section 8 of the RTI Act and, to the best of my knowledge, "
        "it pertains to no such matter. I am willing to pay the prescribed fee. "
        "The application has been auto-generated by the Accountable Platform on "
        f"behalf of the complainant on {now_str}."
    )
    story.append(Paragraph(declaration, styles["body"]))
    story.append(Spacer(1, 10 * mm))

    # Signature block
    sig_data = [
        ["", ""],
        ["Date: " + now_str, applicant_name],
        ["", "(Applicant / Authorised Representative)"],
    ]
    sig_table = Table(sig_data, colWidths=[9 * cm, 8 * cm])
    sig_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(sig_table)
    story.append(Spacer(1, 8 * mm))

    # Footer
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Spacer(1, 2 * mm))
    story.append(
        Paragraph(
            f"Auto-generated by Accountable Platform | Complaint #{complaint.id} | {now_str}",
            styles["footer"],
        )
    )

    doc.build(story)


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

async def _load_complaint_with_relations(
    complaint_id: int,
) -> Optional[Complaint]:
    """Load complaint with ward and tender matches."""
    async with async_session_factory() as db:
        result = await db.execute(
            select(Complaint)
            .options(
                selectinload(Complaint.ward),
                selectinload(Complaint.tender_matches).selectinload(TenderMatch.tender),
            )
            .where(Complaint.id == complaint_id)
        )
        return result.scalars().first()


async def _save_rti_record(
    complaint_id: int,
    pdf_path: str,
    pio_name: str,
    subject: str,
) -> None:
    """Persist RTIRequest record and mark complaint.rti_filed = True."""
    async with async_session_factory() as db:
        rti = RTIRequest(
            complaint_id=complaint_id,
            pdf_file_path=pdf_path,
            addressed_to=pio_name,
            subject=subject,
            auto_generated=True,
            generation_triggered_at=datetime.now(timezone.utc),
        )
        db.add(rti)

        # Mark complaint
        from app.database.models import Complaint as C  # local to avoid circular
        result = await db.execute(select(C).where(C.id == complaint_id))
        complaint = result.scalars().first()
        if complaint:
            complaint.rti_filed = True
            complaint.status = C.__table__.c  # placeholder — resolved below
            from app.database.models import ComplaintStatus
            complaint.status = ComplaintStatus.RTI_FILED

        await db.commit()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def generate_rti_pdf(complaint: Complaint) -> str:
    """
    Generate an RTI PDF for *complaint* and return the absolute file path.

    Steps
    -----
    1. Load related tender matches (for question generation).
    2. Resolve PIO details from ward / config defaults.
    3. Render the PDF with ReportLab.
    4. Persist an RTIRequest record in the DB.
    5. Return the absolute path for FileResponse streaming.
    """
    # Re-load with full relations if needed
    full_complaint = await _load_complaint_with_relations(complaint.id)
    if not full_complaint:
        raise ValueError(f"Complaint {complaint.id} not found")

    # Resolve PIO
    ward = full_complaint.ward
    if ward:
        pio_name = ward.district_collector_name or "The Public Information Officer"
        pio_address = (
            f"Office of the District Collector, {ward.district}, {ward.state}"
        )
    else:
        pio_name = "The Public Information Officer"
        pio_address = settings.DEFAULT_PIO_ADDRESS

    # Applicant name
    if full_complaint.is_anonymous or not full_complaint.submitter_name:
        applicant_name = "Accountable Platform (Authorised Representative)"
    else:
        applicant_name = full_complaint.submitter_name

    # Output path
    filename = f"RTI_Complaint_{full_complaint.id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.pdf"
    output_path = str(RTI_OUTPUT_DIR / filename)

    subject = (
        f"RTI Application — Public Complaint #{full_complaint.id}: {full_complaint.title}"
    )

    # Build PDF
    logger.info("Generating RTI PDF for complaint %d → %s", full_complaint.id, output_path)
    _build_pdf(
        output_path=output_path,
        complaint=full_complaint,
        tender_refs=full_complaint.tender_matches,
        pio_name=pio_name,
        pio_address=pio_address,
        applicant_name=applicant_name,
    )

    # Persist DB record
    await _save_rti_record(
        complaint_id=full_complaint.id,
        pdf_path=output_path,
        pio_name=pio_name,
        subject=subject,
    )

    logger.info("RTI PDF generated: %s", output_path)
    return output_path


# ---------------------------------------------------------------------------
# Day-14 Scheduler hook
# ---------------------------------------------------------------------------

async def run_day14_rti_sweep() -> None:
    """
    Scan complaints that:
      - Have NOT been resolved or closed.
      - Were created ≥ 14 days ago.
      - Have NOT already had an RTI filed.

    Called by APScheduler / Celery beat daily.
    """
    from datetime import timedelta

    cutoff = datetime.now(timezone.utc) - timedelta(days=14)

    async with async_session_factory() as db:
        result = await db.execute(
            select(Complaint).where(
                Complaint.rti_filed.is_(False),
                Complaint.created_at <= cutoff,
                Complaint.status.notin_(
                    ["resolved", "closed"]
                ),
            )
        )
        due_complaints: list[Complaint] = list(result.scalars().all())

    logger.info(
        "Day-14 RTI sweep: %d complaints due for RTI filing", len(due_complaints)
    )

    for complaint in due_complaints:
        try:
            await generate_rti_pdf(complaint)
        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "RTI PDF generation failed for complaint %d: %s", complaint.id, exc
            )
