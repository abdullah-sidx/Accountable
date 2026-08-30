"""
Accountable Platform — FastAPI Application Entry Point
========================================================
Exposes core REST endpoints for:
  - Public complaints (CRUD + deduplication trigger)
  - PFMS fund-flow data ingestion & querying
  - Contractor record management
  - Manual escalation trigger
  - RTI PDF generation
  - NLP tender-match analysis
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db, init_db
from app.database import models  # noqa: F401 — ensure models are registered
from app.schemas import (
    ComplaintCreate,
    ComplaintRead,
    ContractorCreate,
    ContractorRead,
    FundFlowCreate,
    FundFlowRead,
    EscalationRead,
)
from app.services.cv_deduplication import deduplicate_complaints
from app.services.nlp_tender_match import match_complaint_to_tenders
from app.services.escalation_worker import trigger_escalation_pipeline
from app.services.rti_pdf_gen import generate_rti_pdf
from app import crud

# ---------------------------------------------------------------------------
# Lifespan: run DB migrations / table creation on startup
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Accountable API",
    description=(
        "Backend for the Accountable civic accountability platform. "
        "Tracks PFMS fund flows, public complaints, contractor records, "
        "and automates RTI filings & escalation workflows."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===========================================================================
# HEALTH
# ===========================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Liveness probe."""
    return {"status": "ok", "service": "accountable-api"}

# ===========================================================================
# COMPLAINTS
# ===========================================================================

@app.post(
    "/api/v1/complaints",
    response_model=ComplaintRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Complaints"],
)
async def create_complaint(
    payload: ComplaintCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a new public complaint.
    Immediately schedules:
      1. Geographic + visual deduplication against existing open complaints.
      2. NLP tender-match analysis to link the complaint to procurement data.
    """
    complaint = await crud.create_complaint(db, payload)

    # Schedule background processing — non-blocking
    background_tasks.add_task(deduplicate_complaints, complaint.id)
    background_tasks.add_task(match_complaint_to_tenders, complaint.id)

    return complaint


@app.get(
    "/api/v1/complaints",
    response_model=list[ComplaintRead],
    tags=["Complaints"],
)
async def list_complaints(
    skip: int = 0,
    limit: int = 50,
    status_filter: str | None = None,
    ward_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Return paginated complaints, optionally filtered by status or ward."""
    return await crud.get_complaints(
        db, skip=skip, limit=limit, status_filter=status_filter, ward_id=ward_id
    )


@app.get(
    "/api/v1/complaints/{complaint_id}",
    response_model=ComplaintRead,
    tags=["Complaints"],
)
async def get_complaint(complaint_id: int, db: AsyncSession = Depends(get_db)):
    complaint = await crud.get_complaint(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


@app.post(
    "/api/v1/complaints/{complaint_id}/deduplicate",
    tags=["Complaints"],
)
async def trigger_deduplication(
    complaint_id: int, background_tasks: BackgroundTasks
):
    """Manually trigger CV deduplication for a single complaint."""
    background_tasks.add_task(deduplicate_complaints, complaint_id)
    return {"message": "Deduplication scheduled", "complaint_id": complaint_id}


# ===========================================================================
# FUND FLOWS  (PFMS data)
# ===========================================================================

@app.post(
    "/api/v1/fund-flows",
    response_model=FundFlowRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Fund Flows"],
)
async def ingest_fund_flow(
    payload: FundFlowCreate, db: AsyncSession = Depends(get_db)
):
    """Ingest a single PFMS fund-flow record."""
    return await crud.create_fund_flow(db, payload)


@app.get(
    "/api/v1/fund-flows",
    response_model=list[FundFlowRead],
    tags=["Fund Flows"],
)
async def list_fund_flows(
    skip: int = 0,
    limit: int = 100,
    project_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Return PFMS fund-flow records, optionally filtered by project."""
    return await crud.get_fund_flows(db, skip=skip, limit=limit, project_id=project_id)


# ===========================================================================
# CONTRACTORS
# ===========================================================================

@app.post(
    "/api/v1/contractors",
    response_model=ContractorRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Contractors"],
)
async def create_contractor(
    payload: ContractorCreate, db: AsyncSession = Depends(get_db)
):
    """Register a contractor record (used for shell-company network mapping)."""
    return await crud.create_contractor(db, payload)


@app.get(
    "/api/v1/contractors",
    response_model=list[ContractorRead],
    tags=["Contractors"],
)
async def list_contractors(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_contractors(db, skip=skip, limit=limit)


@app.get(
    "/api/v1/contractors/{contractor_id}/network",
    tags=["Contractors"],
)
async def get_contractor_network(
    contractor_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Return the shell-company network graph for a contractor
    (identified via shared directors, addresses, and tender patterns).
    """
    network = await crud.get_contractor_network(db, contractor_id)
    if not network:
        raise HTTPException(status_code=404, detail="Contractor not found")
    return network


# ===========================================================================
# ESCALATIONS
# ===========================================================================

@app.get(
    "/api/v1/escalations",
    response_model=list[EscalationRead],
    tags=["Escalations"],
)
async def list_escalations(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_escalations(db, skip=skip, limit=limit)


@app.post(
    "/api/v1/complaints/{complaint_id}/escalate",
    response_model=EscalationRead,
    tags=["Escalations"],
)
async def manual_escalate(
    complaint_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Manually trigger the escalation pipeline for a complaint.
    The worker will advance the complaint to the next authority tier.
    """
    complaint = await crud.get_complaint(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    background_tasks.add_task(trigger_escalation_pipeline, complaint_id)
    return await crud.get_latest_escalation(db, complaint_id)


# ===========================================================================
# RTI PDF GENERATION
# ===========================================================================

@app.post(
    "/api/v1/complaints/{complaint_id}/rti",
    tags=["RTI"],
)
async def generate_rti(
    complaint_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Generate a pre-filled RTI request PDF for the complaint.
    Triggered automatically on Day 14 of non-resolution; can also be called manually.
    """
    complaint = await crud.get_complaint(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    pdf_path = await generate_rti_pdf(complaint)
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"RTI_Complaint_{complaint_id}.pdf",
    )


# ===========================================================================
# NLP TENDER MATCH
# ===========================================================================

@app.get(
    "/api/v1/complaints/{complaint_id}/tender-matches",
    tags=["NLP / Tender Match"],
)
async def get_tender_matches(
    complaint_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Return NLP-derived tender matches and shell-company associations
    already computed for this complaint.
    """
    complaint = await crud.get_complaint(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    return await crud.get_tender_matches(db, complaint_id)