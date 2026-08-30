"""
Accountable Platform — CRUD Layer
===================================
Thin async database access layer called by FastAPI route handlers.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import (
    Complaint,
    Contractor,
    ContractorDirector,
    Escalation,
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
    from datetime import datetime, timedelta, timezone

    complaint = Complaint(
        **payload.model_dump(),
        rti_deadline=datetime.now(timezone.utc) + timedelta(days=14),
    )
    db.add(complaint)
    await db.flush()
    await db.refresh(complaint)
    return complaint


async def get_complaint(db: AsyncSession, complaint_id: int) -> Optional[Complaint]:
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
    query = select(Complaint)
    if status_filter:
        query = query.where(Complaint.status == status_filter)
    if ward_id:
        query = query.where(Complaint.ward_id == ward_id)
    query = query.offset(skip).limit(limit).order_by(Complaint.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


# ===========================================================================
# Fund Flows
# ===========================================================================

async def create_fund_flow(db: AsyncSession, payload: FundFlowCreate) -> FundFlow:
    fund_flow = FundFlow(**payload.model_dump())
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
    query = select(FundFlow)
    if project_id:
        query = query.where(FundFlow.project_id == int(project_id))
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


# ===========================================================================
# Contractors
# ===========================================================================

async def create_contractor(db: AsyncSession, payload: ContractorCreate) -> Contractor:
    contractor = Contractor(**payload.model_dump())
    db.add(contractor)
    await db.flush()
    await db.refresh(contractor)
    return contractor


async def get_contractors(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[Contractor]:
    result = await db.execute(select(Contractor).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_contractor_network(
    db: AsyncSession, contractor_id: int
) -> Optional[dict]:
    """
    Build a shell-company network graph for the given contractor.
    Returns nodes (contractors) and edges (shared directors/addresses).
    """
    root_result = await db.execute(
        select(Contractor).where(Contractor.id == contractor_id)
    )
    root = root_result.scalars().first()
    if not root:
        return None

    # Find all contractors in the same shell cluster
    cluster_id = root.shell_network_cluster_id
    if cluster_id:
        cluster_result = await db.execute(
            select(Contractor).where(Contractor.shell_network_cluster_id == cluster_id)
        )
        cluster_members = list(cluster_result.scalars().all())
    else:
        cluster_members = [root]

    # Gather directors for each member
    nodes = []
    edges = []
    director_index: dict[str, list[int]] = {}

    for contractor in cluster_members:
        nodes.append(
            {
                "id": contractor.id,
                "name": contractor.company_name,
                "risk_score": contractor.risk_score,
                "is_shell_suspect": contractor.is_shell_company_suspect,
            }
        )
        dir_result = await db.execute(
            select(ContractorDirector).where(
                ContractorDirector.contractor_id == contractor.id
            )
        )
        for director in dir_result.scalars().all():
            key = director.din_number or director.pan_number or director.full_name.lower()
            director_index.setdefault(key, []).append(contractor.id)

    # Create edges where directors are shared
    for din, contractor_ids in director_index.items():
        if len(contractor_ids) > 1:
            for i in range(len(contractor_ids)):
                for j in range(i + 1, len(contractor_ids)):
                    edges.append(
                        {
                            "source": contractor_ids[i],
                            "target": contractor_ids[j],
                            "shared_director": din,
                        }
                    )

    return {"nodes": nodes, "edges": edges, "cluster_id": cluster_id}


# ===========================================================================
# Escalations
# ===========================================================================

async def get_escalations(
    db: AsyncSession, skip: int = 0, limit: int = 50
) -> list[Escalation]:
    result = await db.execute(
        select(Escalation).offset(skip).limit(limit).order_by(Escalation.created_at.desc())
    )
    return list(result.scalars().all())


async def get_latest_escalation(
    db: AsyncSession, complaint_id: int
) -> Optional[Escalation]:
    result = await db.execute(
        select(Escalation)
        .where(Escalation.complaint_id == complaint_id)
        .order_by(Escalation.created_at.desc())
        .limit(1)
    )
    return result.scalars().first()


# ===========================================================================
# Tender Matches
# ===========================================================================

async def get_tender_matches(
    db: AsyncSession, complaint_id: int
) -> list[TenderMatch]:
    result = await db.execute(
        select(TenderMatch)
        .where(TenderMatch.complaint_id == complaint_id)
        .order_by(TenderMatch.combined_confidence.desc())
    )
    return list(result.scalars().all())
