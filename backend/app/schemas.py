"""
Accountable Platform — Pydantic Schemas
========================================
Request / response models for all API endpoints.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field

from app.database.models import (
    ComplaintStatus,
    EscalationStatus,
    EscalationTier,
    FundFlowType,
)


# ===========================================================================
# Complaint Schemas
# ===========================================================================

class ComplaintCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=500)
    description: str = Field(..., min_length=10)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    ward_id: Optional[int] = None
    submitter_name: Optional[str] = None
    submitter_contact: Optional[str] = None
    is_anonymous: bool = False


class ComplaintRead(BaseModel):
    id: int
    title: str
    description: str
    latitude: float
    longitude: float
    address: Optional[str]
    ward_id: Optional[int]
    submitter_name: Optional[str]
    is_anonymous: bool
    status: ComplaintStatus
    is_duplicate: bool
    duplicate_of_id: Optional[int]
    dedup_confidence_score: Optional[float]
    nlp_category: Optional[str]
    nlp_keywords: Optional[list[str]]
    rti_filed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ===========================================================================
# Fund Flow Schemas
# ===========================================================================

class FundFlowCreate(BaseModel):
    project_id: int
    pfms_transaction_id: Optional[str] = None
    flow_type: FundFlowType
    amount: float = Field(..., gt=0)
    currency: str = Field(default="INR", max_length=3)
    releasing_authority: Optional[str] = None
    receiving_agency: Optional[str] = None
    beneficiary_account: Optional[str] = None
    raw_pfms_payload: Optional[dict[str, Any]] = None
    transaction_date: datetime


class FundFlowRead(BaseModel):
    id: int
    project_id: int
    pfms_transaction_id: Optional[str]
    flow_type: FundFlowType
    amount: float
    currency: str
    releasing_authority: Optional[str]
    receiving_agency: Optional[str]
    is_flagged: bool
    flag_reason: Optional[str]
    transaction_date: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


# ===========================================================================
# Contractor Schemas
# ===========================================================================

class ContractorCreate(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=500)
    registration_number: Optional[str] = None
    pan_number: Optional[str] = None
    gst_number: Optional[str] = None
    registered_address: Optional[str] = None
    registered_address_lat: Optional[float] = None
    registered_address_lon: Optional[float] = None


class ContractorRead(BaseModel):
    id: int
    company_name: str
    registration_number: Optional[str]
    pan_number: Optional[str]
    gst_number: Optional[str]
    registered_address: Optional[str]
    is_shell_company_suspect: bool
    shell_network_cluster_id: Optional[int]
    risk_score: float
    blacklisted: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ===========================================================================
# Escalation Schemas
# ===========================================================================

class EscalationRead(BaseModel):
    id: int
    complaint_id: int
    tier: EscalationTier
    status: EscalationStatus
    assigned_to_name: Optional[str]
    assigned_to_email: Optional[str]
    notification_sent_at: Optional[datetime]
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    escalate_after: Optional[datetime]
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
