"""
Accountable Platform — Async CRUD Layer
========================================
All database operations are async SQLAlchemy 2.x style.

Functions
---------
  Complaints  : create_complaint, get_complaint, get_complaints
  Fund Flows  : create_fund_flow, get_fund_flows
  Contractors : create_contractor, get_contractors, get_contractor_network
  Escalations : get_escalations, get_latest_escalation
  Tender Match: get_tender_matches
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import (
    Complaint,
    ComplaintStatus,
    Contractor,
    ContractorDirector,
    Escalation,
    EscalationStatus,
    FundFlow,
    TenderMatch,
)
from app.schemas import (
    ComplaintCreate,
    ContractorCreate,
    FundFlowCreate,
)


# ===========================================================================
# Complaints
# ===========================================================================

async def create_complaint(db: AsyncSession, payload: ComplaintCreate) -> Complaint:
    """
    Persist a new complaint and return the saved ORM object.
    Sets the RTI deadline to 14 days from submission automatically.
    """
    now = datetime.now(timezone.utc)
    complaint = Complaint(
        title=payload.title,
        description=payload.description,
        latitude=payload.latitude,
        longitude=payload.longitude,
        address=payload.address,
        ward_id=payload.ward_id,
        submitter_name=payload.submitter_name,
        submitter_contact=payload.submitter_contact,
        is_anonymous=payload.is_anonymous,
        status=ComplaintStatus.OPEN,
        rti_deadline=now + timedelta(days=14),
    )
    db.add(complaint)
    await db.flush()          # populate complaint.id without committing
    await db.refresh(complaint)
    return complaint


async def get_complaint(db: AsyncSession, complaint_id: int) -> Optional[Complaint]:
    """Return a single Complaint by primary key, or None."""
    result = await db.execute(
        select(Complaint).where(Complaint.id == complaint_id)
    )
    return result.scalars().first()


async def get_complaints(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    status_filter: Optional[str] = None,
    ward_id: Optional[int] = None,
) -> list[Complaint]:
    """
    Return a paginated list of complaints.

    Parameters
    ----------
    skip          : Number of rows to skip (offset).
    limit         : Maximum rows to return.
    status_filter : Optional ComplaintStatus value string (e.g. "open").
    ward_id       : Optional ward primary key to filter by.
    """
    query = select(Complaint)

    if status_filter:
        try:
            status_enum = ComplaintStatus(status_filter)
            query = query.where(Complaint.status == status_enum)
        except ValueError:
            pass  # Silently ignore unknown status values — return unfiltered

    if ward_id is not None:
        query = query.where(Complaint.ward_id == ward_id)

    query = query.order_by(Complaint.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


# ===========================================================================
# Fund Flows  (PFMS disbursement records)
# ===========================================================================

async def create_fund_flow(db: AsyncSession, payload: FundFlowCreate) -> FundFlow:
    """
    Persist a new PFMS fund-flow record.

    The schema exposes `sanctioned_amount`, `contractor_received`, and
    `actual_work_value` as first-class fields.  These map to the ORM
    columns via the FundFlow model's extended attribute set.
    """
    fund_flow = FundFlow(
        project_id=payload.project_id,
        pfms_transaction_id=payload.pfms_transaction_id,
        flow_type=payload.flow_type,
        # Core financial trio
        amount=payload.sanctioned_amount,          # ORM stores as `amount`
        currency=payload.currency,
        releasing_authority=payload.releasing_authority,
        receiving_agency=payload.receiving_agency,
        beneficiary_account=payload.beneficiary_account,
        raw_pfms_payload=payload.raw_pfms_payload,
        transaction_date=payload.transaction_date,
    )

    # Store the extended financial breakdown as extra attributes.
    # These are transparently persisted via the JSON raw_pfms_payload
    # field when a migration adds dedicated columns; for now they live
    # alongside the record as a convenience accessor.
    if fund_flow.raw_pfms_payload is None:
        fund_flow.raw_pfms_payload = {}
    fund_flow.raw_pfms_payload["sanctioned_amount"] = payload.sanctioned_amount
    fund_flow.raw_pfms_payload["contractor_received"] = payload.contractor_received
    fund_flow.raw_pfms_payload["actual_work_value"] = payload.actual_work_value

    # Auto-flag if disbursement exceeds sanctioned amount by more than 5 %
    if payload.contractor_received > payload.sanctioned_amount * 1.05:
        fund_flow.is_flagged = True
        fund_flow.flag_reason = (
            f"Contractor received ₹{payload.contractor_received:,.2f} which exceeds "
            f"sanctioned ₹{payload.sanctioned_amount:,.2f} by more than 5%."
        )

    db.add(fund_flow)
    await db.flush()
    await db.refresh(fund_flow)
    return fund_flow


async def get_fund_flows(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[str] = None,
) -> list[FundFlow]:
    """
    Return a paginated list of fund-flow records.

    Parameters
    ----------
    project_id : Optional project primary key (passed as string from query param).
    """
    query = select(FundFlow)

    if project_id is not None:
        try:
            query = query.where(FundFlow.project_id == int(project_id))
        except ValueError:
            pass  # Non-integer project_id — ignore filter

    query = query.order_by(FundFlow.transaction_date.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


# ===========================================================================
# Contractors
# ===========================================================================

async def create_contractor(db: AsyncSession, payload: ContractorCreate) -> Contractor:
    """
    Persist a new contractor record.
    The schema field `name` maps to the ORM column `company_name`.
    """
    contractor = Contractor(
        company_name=payload.name,           # schema→ORM field mapping
        registration_number=payload.registration_number,
        pan_number=payload.pan_number,
        gst_number=payload.gst_number,
        registered_address=payload.registered_address,
        registered_address_lat=payload.registered_address_lat,
        registered_address_lon=payload.registered_address_lon,
    )
    db.add(contractor)
    await db.flush()
    await db.refresh(contractor)
    return contractor


async def get_contractors(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> list[Contractor]:
    """Return a paginated list of contractor records."""
    result = await db.execute(
        select(Contractor)
        .order_by(Contractor.company_name)
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_contractor_network(
    db: AsyncSession,
    contractor_id: int,
) -> Optional[dict[str, Any]]:
    """
    Build a shell-company network graph for *contractor_id*.

    Returns a dict with:
      nodes : list of contractor nodes in the same cluster.
      edges : list of {source, target, shared_director} for shared directors.
      cluster_id : the shell_network_cluster_id (or None for isolated nodes).

    Falls back to a mock graph when the contractor has no cluster assigned,
    so the endpoint always returns a useful response for development/testing.
    """
    result = await db.execute(
        select(Contractor).where(Contractor.id == contractor_id)
    )
    root: Optional[Contractor] = result.scalars().first()

    if root is None:
        return None

    # ----- Build real graph if a cluster exists -----
    cluster_id = root.shell_network_cluster_id
    if cluster_id is not None:
        cluster_result = await db.execute(
            select(Contractor).where(Contractor.shell_network_cluster_id == cluster_id)
        )
        cluster_members = list(cluster_result.scalars().all())
    else:
        cluster_members = [root]

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    director_index: dict[str, list[int]] = {}

    for contractor in cluster_members:
        nodes.append(
            {
                "id": contractor.id,
                "name": contractor.company_name,
                "registration_number": contractor.registration_number,
                "risk_score": contractor.risk_score,
                "is_shell_suspect": contractor.is_shell_company_suspect,
                "blacklisted": contractor.blacklisted,
            }
        )
        dir_result = await db.execute(
            select(ContractorDirector).where(
                ContractorDirector.contractor_id == contractor.id
            )
        )
        for director in dir_result.scalars().all():
            key = (
                director.din_number
                or director.pan_number
                or director.full_name.lower()
            )
            director_index.setdefault(key, []).append(contractor.id)

    # Create edges where directors are shared across companies
    for din, c_ids in director_index.items():
        if len(c_ids) > 1:
            for i in range(len(c_ids)):
                for j in range(i + 1, len(c_ids)):
                    edges.append(
                        {
                            "source": c_ids[i],
                            "target": c_ids[j],
                            "relationship": "shared_director",
                            "shared_director_id": din,
                        }
                    )

    # ----- If only one node and no real edges, return an indicative mock -----
    if len(nodes) == 1 and not edges:
        edges = [
            {
                "source": contractor_id,
                "target": contractor_id,
                "relationship": "self",
                "note": "No shell-network cluster assigned yet. "
                        "Run the NLP analysis pipeline to identify linked entities.",
            }
        ]

    return {
        "contractor_id": contractor_id,
        "cluster_id": cluster_id,
        "nodes": nodes,
        "edges": edges,
        "summary": {
            "total_entities": len(nodes),
            "shared_director_links": len([e for e in edges if e.get("relationship") == "shared_director"]),
            "any_blacklisted": any(n["blacklisted"] for n in nodes),
            "max_risk_score": max((n["risk_score"] for n in nodes), default=0.0),
        },
    }


# ===========================================================================
# Escalations
# ===========================================================================

async def get_escalations(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
) -> list[Escalation]:
    """Return a paginated, chronologically sorted list of all escalation events."""
    result = await db.execute(
        select(Escalation)
        .order_by(Escalation.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_latest_escalation(
    db: AsyncSession,
    complaint_id: int,
) -> Optional[Escalation]:
    """
    Return the most recent Escalation row for *complaint_id*, or None.
    Also injects `previous_level` by looking up the preceding escalation row
    so the EscalationRead schema can expose it without an extra query.
    """
    # Fetch the two most recent escalations — latest + the one before
    result = await db.execute(
        select(Escalation)
        .where(Escalation.complaint_id == complaint_id)
        .order_by(Escalation.created_at.desc())
        .limit(2)
    )
    rows = list(result.scalars().all())

    if not rows:
        return None

    latest = rows[0]
    # Inject previous_level as a transient attribute for schema serialisation
    if len(rows) == 2:
        prev_tier = rows[1].tier
        latest.__dict__["previous_level"] = (
            prev_tier.value if hasattr(prev_tier, "value") else prev_tier
        )
    else:
        latest.__dict__["previous_level"] = None

    return latest


# ===========================================================================
# Tender Matches  (NLP results)
# ===========================================================================

async def get_tender_matches(
    db: AsyncSession,
    complaint_id: int,
) -> list[dict[str, Any]]:
    """
    Return NLP tender-match results for *complaint_id*, ordered by confidence.

    Each result dict is enriched with:
      - tender title, department, and awarded contractor name
      - a human-readable `analysis_summary`

    Returns a mock result set when no matches exist yet, so the endpoint
    always returns a useful response during development / before the NLP
    pipeline has run.
    """
    result = await db.execute(
        select(TenderMatch)
        .options(
            selectinload(TenderMatch.tender),
            selectinload(TenderMatch.complaint),
        )
        .where(TenderMatch.complaint_id == complaint_id)
        .order_by(TenderMatch.combined_confidence.desc())
    )
    matches: list[TenderMatch] = list(result.scalars().all())

    if not matches:
        # ── Mock response for dev / pre-pipeline state ──────────────────────
        return [
            {
                "id": None,
                "complaint_id": complaint_id,
                "tender_id": None,
                "tender_title": "NLP pipeline has not yet run for this complaint.",
                "tender_department": None,
                "awarded_contractor_name": None,
                "similarity_score": 0.0,
                "keyword_overlap_score": 0.0,
                "combined_confidence": 0.0,
                "matched_keywords": [],
                "shell_company_flagged": False,
                "analysis_summary": (
                    "No tender matches found. Submit the complaint first and wait "
                    "for the background NLP pipeline to complete. "
                    "You can also POST /api/v1/complaints/{id}/deduplicate to trigger manually."
                ),
                "created_at": None,
            }
        ]

    # ── Enrich real matches with joined data ─────────────────────────────────
    output: list[dict[str, Any]] = []
    for m in matches:
        tender = m.tender
        tender_title = tender.title if tender else "Unknown tender"
        tender_dept = tender.department if tender else None
        contractor_name: Optional[str] = None
        if tender and tender.awarded_contractor:
            contractor_name = tender.awarded_contractor.company_name

        confidence_label = (
            "High" if m.combined_confidence >= 0.75
            else "Medium" if m.combined_confidence >= 0.50
            else "Low"
        )
        shell_warning = (
            " ⚠️ Awarded contractor is flagged as a shell-company suspect."
            if m.shell_company_flagged
            else ""
        )

        output.append(
            {
                "id": m.id,
                "complaint_id": m.complaint_id,
                "tender_id": m.tender_id,
                "tender_title": tender_title,
                "tender_department": tender_dept,
                "awarded_contractor_name": contractor_name,
                "similarity_score": round(m.similarity_score, 4),
                "keyword_overlap_score": round(m.keyword_overlap_score or 0.0, 4),
                "combined_confidence": round(m.combined_confidence, 4),
                "matched_keywords": m.matched_keywords or [],
                "shell_company_flagged": m.shell_company_flagged,
                "analysis_summary": (
                    f"{confidence_label} confidence match ({m.combined_confidence:.0%}) "
                    f"between complaint and tender '{tender_title}'.{shell_warning}"
                ),
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
        )

    return output
