"""
Accountable Platform — Escalation Worker
=========================================
Routes unresolved complaints sequentially through authority tiers:

    Ward Officer  →  MLA  →  District Collector  →  State Authority

Escalation rules
----------------
- A complaint is escalated when it remains unresolved (status ≠ resolved/closed)
  after TIER_SLA_HOURS hours at the current tier.
- The worker is invoked:
    a) As a FastAPI BackgroundTask (manual trigger via API).
    b) As a periodic Celery/APScheduler beat task (automatic, every hour).
- Each escalation event creates a new Escalation row with the next tier.
- Notifications are sent to the authority's registered email.

Entry point
-----------
    await trigger_escalation_pipeline(complaint_id: int) -> None
    await run_scheduled_escalation_sweep()        # periodic scheduler hook
"""

from __future__ import annotations

import logging
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.db import async_session_factory
from app.database.models import (
    Complaint,
    ComplaintStatus,
    Escalation,
    EscalationStatus,
    EscalationTier,
    Ward,
)
from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# SLA configuration (hours before auto-escalation to next tier)
# ---------------------------------------------------------------------------

TIER_SLA_HOURS: dict[EscalationTier, int] = {
    EscalationTier.WARD_OFFICER: 72,        # 3 days
    EscalationTier.MLA: 120,               # 5 days
    EscalationTier.DISTRICT_COLLECTOR: 168, # 7 days
    EscalationTier.STATE_AUTHORITY: 240,    # 10 days — terminal tier
}

# Ordered tier sequence
TIER_SEQUENCE: list[EscalationTier] = [
    EscalationTier.WARD_OFFICER,
    EscalationTier.MLA,
    EscalationTier.DISTRICT_COLLECTOR,
    EscalationTier.STATE_AUTHORITY,
]


def _next_tier(current: EscalationTier) -> Optional[EscalationTier]:
    """Return the next tier in the sequence, or None at the terminal tier."""
    try:
        idx = TIER_SEQUENCE.index(current)
        return TIER_SEQUENCE[idx + 1] if idx + 1 < len(TIER_SEQUENCE) else None
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Authority contact resolution
# ---------------------------------------------------------------------------

def _resolve_authority(
    tier: EscalationTier, ward: Optional[Ward]
) -> tuple[str, str]:
    """
    Return (authority_name, authority_email) for a given tier and ward.
    Falls back to config-level defaults when ward data is absent.
    """
    if ward:
        mapping: dict[EscalationTier, tuple[str, str]] = {
            EscalationTier.WARD_OFFICER: (
                ward.ward_officer_name or "Ward Officer",
                ward.ward_officer_email or settings.DEFAULT_WARD_OFFICER_EMAIL,
            ),
            EscalationTier.MLA: (
                ward.mla_name or "MLA Office",
                ward.mla_email or settings.DEFAULT_MLA_EMAIL,
            ),
            EscalationTier.DISTRICT_COLLECTOR: (
                ward.district_collector_name or "District Collector",
                ward.district_collector_email or settings.DEFAULT_COLLECTOR_EMAIL,
            ),
            EscalationTier.STATE_AUTHORITY: (
                "State Grievance Authority",
                settings.DEFAULT_STATE_AUTHORITY_EMAIL,
            ),
        }
        return mapping.get(tier, ("Unknown Authority", settings.DEFAULT_WARD_OFFICER_EMAIL))

    # No ward data — use global defaults
    defaults: dict[EscalationTier, tuple[str, str]] = {
        EscalationTier.WARD_OFFICER: ("Ward Officer", settings.DEFAULT_WARD_OFFICER_EMAIL),
        EscalationTier.MLA: ("MLA Office", settings.DEFAULT_MLA_EMAIL),
        EscalationTier.DISTRICT_COLLECTOR: ("District Collector", settings.DEFAULT_COLLECTOR_EMAIL),
        EscalationTier.STATE_AUTHORITY: ("State Authority", settings.DEFAULT_STATE_AUTHORITY_EMAIL),
    }
    return defaults[tier]


# ---------------------------------------------------------------------------
# Email notification
# ---------------------------------------------------------------------------

def _build_email_body(complaint: Complaint, tier: EscalationTier, authority_name: str) -> str:
    """Render a plain-text escalation notification email."""
    return f"""Dear {authority_name},

A public complaint has been escalated to your office as it remains unresolved.

Complaint ID : #{complaint.id}
Title        : {complaint.title}
Description  : {complaint.description[:500]}...
Location     : {complaint.address or f'Lat {complaint.latitude}, Lon {complaint.longitude}'}
Status       : {complaint.status.value}
Submitted on : {complaint.created_at.strftime('%d %b %Y %H:%M UTC')}
Current Tier : {tier.value.replace('_', ' ').title()}

Please acknowledge and act on this complaint within the stipulated SLA period.
Failure to respond may result in further escalation or automatic RTI filing.

Regards,
Accountable Platform (Automated Escalation System)
"""


def _send_email_notification(
    to_name: str,
    to_email: str,
    subject: str,
    body: str,
) -> None:
    """
    Send an SMTP email notification.
    Uses settings.SMTP_* for configuration.
    Exceptions are logged but not re-raised to avoid blocking the worker.
    """
    if not settings.SMTP_HOST:
        logger.warning("SMTP not configured; skipping email to %s", to_email)
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM_EMAIL
        msg["To"] = to_email
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            if settings.SMTP_USERNAME:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, [to_email], msg.as_string())

        logger.info("Escalation email sent to %s <%s>", to_name, to_email)

    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to send escalation email to %s: %s", to_email, exc)


# ---------------------------------------------------------------------------
# Escalation creation helpers
# ---------------------------------------------------------------------------

async def _get_active_escalation(
    db: AsyncSession, complaint_id: int
) -> Optional[Escalation]:
    """Return the latest escalation record for the complaint."""
    result = await db.execute(
        select(Escalation)
        .where(Escalation.complaint_id == complaint_id)
        .order_by(Escalation.created_at.desc())
        .limit(1)
    )
    return result.scalars().first()


async def _create_escalation(
    db: AsyncSession,
    complaint: Complaint,
    tier: EscalationTier,
    authority_name: str,
    authority_email: str,
) -> Escalation:
    """Persist a new Escalation record and send notification email."""
    sla_hours = TIER_SLA_HOURS[tier]
    now = datetime.now(timezone.utc)

    escalation = Escalation(
        complaint_id=complaint.id,
        tier=tier,
        status=EscalationStatus.PENDING,
        assigned_to_name=authority_name,
        assigned_to_email=authority_email,
        notification_sent_at=now,
        escalate_after=now + timedelta(hours=sla_hours),
    )
    db.add(escalation)

    # Update complaint status
    complaint.status = ComplaintStatus.ESCALATED

    await db.flush()  # get the escalation.id

    # Send notification (non-blocking — failures are logged only)
    subject = f"[Accountable] Complaint #{complaint.id} Escalated to {tier.value.replace('_', ' ').title()}"
    body = _build_email_body(complaint, tier, authority_name)
    _send_email_notification(authority_name, authority_email, subject, body)

    return escalation


# ---------------------------------------------------------------------------
# Core escalation pipeline
# ---------------------------------------------------------------------------

async def trigger_escalation_pipeline(complaint_id: int) -> None:
    """
    Advance a single complaint to the next escalation tier.

    Logic
    -----
    1. Load complaint + ward.
    2. Find the current active escalation (if any).
    3. Determine the target tier:
       - No prior escalation → start at WARD_OFFICER.
       - Prior escalation exists → advance to next tier.
    4. Mark prior escalation as ESCALATED_FURTHER.
    5. Create new Escalation record; send notification email.
    """
    async with async_session_factory() as db:
        result = await db.execute(
            select(Complaint)
            .options(selectinload(Complaint.ward))
            .where(Complaint.id == complaint_id)
        )
        complaint: Optional[Complaint] = result.scalars().first()

        if not complaint:
            logger.error("trigger_escalation_pipeline: complaint %d not found", complaint_id)
            return

        if complaint.status in (ComplaintStatus.RESOLVED, ComplaintStatus.CLOSED):
            logger.info(
                "Complaint %d already %s; skipping escalation", complaint_id, complaint.status
            )
            return

        # Current escalation
        current_escalation = await _get_active_escalation(db, complaint_id)

        if current_escalation is None:
            target_tier = EscalationTier.WARD_OFFICER
        else:
            next_t = _next_tier(current_escalation.tier)
            if next_t is None:
                logger.warning(
                    "Complaint %d already at terminal tier %s; no further escalation",
                    complaint_id,
                    current_escalation.tier,
                )
                return
            # Mark current as escalated further
            current_escalation.status = EscalationStatus.ESCALATED_FURTHER
            target_tier = next_t

        ward: Optional[Ward] = complaint.ward
        authority_name, authority_email = _resolve_authority(target_tier, ward)

        new_escalation = await _create_escalation(
            db, complaint, target_tier, authority_name, authority_email
        )

        await db.commit()

        logger.info(
            "Complaint %d escalated to %s (Escalation ID %d) → %s <%s>",
            complaint_id,
            target_tier.value,
            new_escalation.id,
            authority_name,
            authority_email,
        )


# ---------------------------------------------------------------------------
# Periodic sweep (APScheduler / Celery beat hook)
# ---------------------------------------------------------------------------

async def run_scheduled_escalation_sweep() -> None:
    """
    Scan all open complaints whose current escalation tier SLA has expired
    and automatically advance them to the next tier.

    Call this from your scheduler every hour:

        scheduler.add_job(
            run_scheduled_escalation_sweep,
            trigger="interval",
            hours=1,
        )
    """
    now = datetime.now(timezone.utc)

    async with async_session_factory() as db:
        # Find escalations that are overdue and still pending
        result = await db.execute(
            select(Escalation)
            .where(
                Escalation.status == EscalationStatus.PENDING,
                Escalation.escalate_after <= now,
            )
            .order_by(Escalation.complaint_id, Escalation.created_at.desc())
        )
        overdue_escalations: list[Escalation] = list(result.scalars().all())

    # Deduplicate by complaint — only process the latest escalation per complaint
    seen_complaints: set[int] = set()
    to_process: list[int] = []

    for esc in overdue_escalations:
        if esc.complaint_id not in seen_complaints:
            seen_complaints.add(esc.complaint_id)
            to_process.append(esc.complaint_id)

    logger.info(
        "Escalation sweep: %d complaints due for escalation at %s",
        len(to_process),
        now.isoformat(),
    )

    for complaint_id in to_process:
        try:
            await trigger_escalation_pipeline(complaint_id)
        except Exception as exc:  # noqa: BLE001
            logger.exception(
                "Error escalating complaint %d: %s", complaint_id, exc
            )
