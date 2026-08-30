"""
Accountable Platform — Pydantic v2 Schemas
===========================================
Provides Base / Create / Read schema triads for every API resource.

Naming convention
-----------------
  *Base   – shared fields (no DB-generated fields)
  *Create – what the client POSTs (extends Base, may add write-only fields)
  *Read   – what the API returns (extends Base, adds DB-generated fields)

All *Read schemas set  model_config = ConfigDict(from_attributes=True)
so they can be constructed directly from SQLAlchemy ORM objects.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.database.models import (
    ComplaintStatus,
    EscalationStatus,
    EscalationTier,
    FundFlowType,
)


# ===========================================================================
# Complaint
# ===========================================================================

class ComplaintBase(BaseModel):
    """Fields shared by create and read complaint schemas."""
    title: str = Field(..., min_length=5, max_length=500, examples=["Broken road near park"])
    description: str = Field(..., min_length=10, examples=["Large pothole causing accidents"])
    latitude: float = Field(..., ge=-90, le=90, examples=[19.0760])
    longitude: float = Field(..., ge=-180, le=180, examples=[72.8777])
    address: Optional[str] = Field(None, examples=["Linking Road, Bandra, Mumbai"])
    ward_id: Optional[int] = Field(None, examples=[42])
    submitter_name: Optional[str] = Field(None, examples=["Priya Sharma"])
    submitter_contact: Optional[str] = Field(None, examples=["9876543210"])
    is_anonymous: bool = Field(False)


class ComplaintCreate(ComplaintBase):
    """Payload expected when a client creates a new complaint."""
    pass  # All fields come from ComplaintBase; extra write-only fields can go here


class ComplaintRead(ComplaintBase):
    """Complaint data returned by the API, including all DB-generated fields."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: ComplaintStatus
    is_duplicate: bool
    duplicate_of_id: Optional[int] = None
    dedup_confidence_score: Optional[float] = None
    nlp_category: Optional[str] = None
    nlp_keywords: Optional[list[str]] = None
    sentiment_score: Optional[float] = None
    rti_filed: bool
    rti_deadline: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None


# ===========================================================================
# Fund Flow  (PFMS disbursement records)
# ===========================================================================

class FundFlowBase(BaseModel):
    """Fields shared by create and read fund-flow schemas."""
    project_id: int = Field(..., examples=[1])
    # Human-readable project label — denormalised for convenient API responses
    project_name: Optional[str] = Field(
        None,
        description="Friendly project name (populated from the joined Project row on read).",
        examples=["PMAY Housing Block B"],
    )
    pfms_transaction_id: Optional[str] = Field(None, examples=["PFMS-2024-00123"])
    flow_type: FundFlowType = Field(..., examples=["release"])

    # Core financial figures
    sanctioned_amount: float = Field(
        ..., gt=0, description="Total amount sanctioned for the project (₹).", examples=[5000000.0]
    )
    contractor_received: float = Field(
        ..., ge=0, description="Amount actually released to the contractor (₹).", examples=[4500000.0]
    )
    actual_work_value: float = Field(
        ..., ge=0, description="Independently assessed value of work completed (₹).", examples=[3200000.0]
    )

    currency: str = Field(default="INR", max_length=3, examples=["INR"])
    releasing_authority: Optional[str] = Field(None, examples=["State Finance Department"])
    receiving_agency: Optional[str] = Field(None, examples=["Municipal Corporation of Mumbai"])
    beneficiary_account: Optional[str] = Field(None, examples=["SBIN000XXXX"])
    raw_pfms_payload: Optional[dict[str, Any]] = Field(
        None, description="Raw JSON payload received from the PFMS portal."
    )
    transaction_date: datetime = Field(..., examples=["2024-03-15T10:30:00Z"])


class FundFlowCreate(FundFlowBase):
    """Payload expected when ingesting a new PFMS fund-flow record."""
    pass


class FundFlowRead(FundFlowBase):
    """Fund-flow record returned by the API."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_flagged: bool
    flag_reason: Optional[str] = None
    created_at: datetime

    @classmethod
    def from_orm_with_project(cls, fund_flow, project_name: Optional[str] = None) -> "FundFlowRead":
        """
        Convenience factory that merges the joined project name into the schema.
        Usage: FundFlowRead.from_orm_with_project(fund_flow_obj, project_name="PMAY Block B")
        """
        data = cls.model_validate(fund_flow)
        if project_name is not None:
            data.project_name = project_name
        return data


# ===========================================================================
# Contractor
# ===========================================================================

class ContractorBase(BaseModel):
    """Fields shared by create and read contractor schemas."""
    name: str = Field(
        ..., min_length=2, max_length=500,
        description="Registered company / contractor name.",
        examples=["Apex Constructions Pvt Ltd"],
    )
    registration_number: Optional[str] = Field(
        None, description="Company registration number (MCA / RoC).", examples=["U45200MH2010PTC123456"]
    )
    pan_number: Optional[str] = Field(None, examples=["AABCP1234Q"])
    gst_number: Optional[str] = Field(None, examples=["27AABCP1234Q1ZV"])
    registered_address: Optional[str] = Field(
        None, examples=["101, Business Park, Andheri East, Mumbai - 400059"]
    )
    registered_address_lat: Optional[float] = Field(None, ge=-90, le=90)
    registered_address_lon: Optional[float] = Field(None, ge=-180, le=180)


class ContractorCreate(ContractorBase):
    """Payload expected when registering a new contractor."""
    pass


class ContractorRead(ContractorBase):
    """Contractor record returned by the API."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_shell_company_suspect: bool
    shell_network_cluster_id: Optional[int] = None
    risk_score: float
    blacklisted: bool
    blacklist_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Resolved from the ORM's `company_name` column (model uses that name)
    @classmethod
    def model_validate(cls, obj, *, strict=None, from_attributes=None, context=None, experimental_allow_partial=None):
        """
        Bridge between the ORM column `company_name` and the schema field `name`.
        SQLAlchemy model stores the value as `company_name`; this schema exposes it as `name`.
        """
        if hasattr(obj, "company_name") and not hasattr(obj, "name"):
            obj.__dict__.setdefault("name", obj.company_name)
        return super().model_validate(
            obj,
            strict=strict,
            from_attributes=from_attributes if from_attributes is not None else True,
            context=context,
        )


# ===========================================================================
# Escalation
# ===========================================================================

class EscalationBase(BaseModel):
    """Fields shared by all escalation schemas."""
    complaint_id: int = Field(..., examples=[101])
    tier: EscalationTier = Field(..., examples=["ward_officer"])
    status: EscalationStatus = Field(default=EscalationStatus.PENDING)
    assigned_to_name: Optional[str] = Field(None, examples=["Ramesh Patil"])
    assigned_to_email: Optional[EmailStr] = Field(None, examples=["ward42@municipality.gov.in"])
    assigned_to_phone: Optional[str] = Field(None, examples=["+912212345678"])
    notes: Optional[str] = None


class EscalationRead(EscalationBase):
    """
    Escalation record returned by the API.
    Exposes `previous_level` and `new_level` as convenience aliases to match
    the spec (the ORM stores the tier progression as separate Escalation rows).
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    # Convenience fields expected by main.py / frontend consumers
    previous_level: Optional[str] = Field(
        None,
        description="Tier value of the preceding escalation row (None if first escalation).",
        examples=["ward_officer"],
    )
    new_level: str = Field(
        ...,
        description="Tier value of this escalation row.",
        examples=["mla"],
    )
    escalated_at: datetime = Field(
        ..., description="Timestamp when this escalation was created (maps to created_at)."
    )
    notification_sent_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    escalate_after: Optional[datetime] = None
    created_at: datetime

    @classmethod
    def model_validate(cls, obj, *, strict=None, from_attributes=None, context=None, experimental_allow_partial=None):
        """
        Map ORM fields to the schema's convenience aliases:
          tier          → new_level
          created_at    → escalated_at
        """
        if hasattr(obj, "__dict__"):
            d = obj.__dict__
            # tier → new_level
            if "new_level" not in d and "tier" in d:
                tier = d["tier"]
                obj.__dict__["new_level"] = tier.value if hasattr(tier, "value") else tier
            # created_at → escalated_at
            if "escalated_at" not in d and "created_at" in d:
                obj.__dict__["escalated_at"] = d["created_at"]

        return super().model_validate(
            obj,
            strict=strict,
            from_attributes=from_attributes if from_attributes is not None else True,
            context=context,
        )


# ===========================================================================
# Tender Match  (NLP result, read-only)
# ===========================================================================

class TenderMatchRead(BaseModel):
    """NLP tender-match result returned by the API."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    complaint_id: int
    tender_id: int
    similarity_score: float
    keyword_overlap_score: Optional[float] = None
    combined_confidence: float
    matched_keywords: Optional[list[str]] = None
    shell_company_flagged: bool
    created_at: datetime

    # Tender metadata joined for convenience
    tender_title: Optional[str] = Field(None, description="Title of the matched tender.")
    tender_department: Optional[str] = Field(None, description="Department that issued the tender.")
    awarded_contractor_name: Optional[str] = Field(None, description="Contractor awarded the tender.")
