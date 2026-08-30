"""
Accountable Platform — SQLAlchemy ORM Models
=============================================
Covers:
  - Complaint           : Citizen-submitted public complaints
  - ComplaintImage      : Attached images (for CV deduplication)
  - FundFlow            : PFMS fund disbursement records
  - Project             : Government project metadata
  - Contractor          : Registered contractor / vendor entity
  - ContractorDirector  : Director-level link for shell-company mapping
  - Tender              : Public tender record
  - TenderMatch         : NLP-derived complaint ↔ tender association
  - Escalation          : Sequential escalation trail per complaint
  - RTIRequest          : Auto-generated RTI PDF records
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# SQLite requires 'INTEGER PRIMARY KEY' (not BIGINT) to automatically generate rowids.
# Using with_variant ensures BigInteger is used on PostgreSQL and Integer on SQLite.
BigIntPK = BigInteger().with_variant(Integer, "sqlite")


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ComplaintStatus(str, enum.Enum):
    OPEN = "open"
    DUPLICATE = "duplicate"
    IN_PROGRESS = "in_progress"
    ESCALATED = "escalated"
    RTI_FILED = "rti_filed"
    RESOLVED = "resolved"
    CLOSED = "closed"


class EscalationTier(str, enum.Enum):
    WARD_OFFICER = "ward_officer"
    MLA = "mla"
    DISTRICT_COLLECTOR = "district_collector"
    STATE_AUTHORITY = "state_authority"


class EscalationStatus(str, enum.Enum):
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    ESCALATED_FURTHER = "escalated_further"


class FundFlowType(str, enum.Enum):
    RELEASE = "release"
    UTILIZATION = "utilization"
    ADVANCE = "advance"
    REIMBURSEMENT = "reimbursement"


# ===========================================================================
# Ward / Geographic Reference
# ===========================================================================

class Ward(Base):
    """Municipal ward or administrative unit."""

    __tablename__ = "wards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    ward_number = Column(String(20), unique=True, nullable=False)
    district = Column(String(200), nullable=False)
    state = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Officer responsible at ward level
    ward_officer_name = Column(String(200), nullable=True)
    ward_officer_email = Column(String(254), nullable=True)
    mla_name = Column(String(200), nullable=True)
    mla_email = Column(String(254), nullable=True)
    district_collector_name = Column(String(200), nullable=True)
    district_collector_email = Column(String(254), nullable=True)

    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    complaints = relationship("Complaint", back_populates="ward")


# ===========================================================================
# Complaints
# ===========================================================================

class Complaint(Base):
    """
    Citizen-submitted public complaint.
    Tracks full lifecycle: open → escalated → RTI filed → resolved.
    """

    __tablename__ = "complaints"

    id = Column(BigIntPK, primary_key=True, index=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)

    # Geographic location of the issue
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(Text, nullable=True)

    ward_id = Column(Integer, ForeignKey("wards.id", ondelete="SET NULL"), nullable=True)

    # Submitter identity (can be anonymous)
    submitter_name = Column(String(200), nullable=True)
    submitter_contact = Column(String(100), nullable=True)
    is_anonymous = Column(Boolean, default=False, nullable=False)

    status = Column(
        Enum(ComplaintStatus, name="complaint_status"),
        default=ComplaintStatus.OPEN,
        nullable=False,
        index=True,
    )

    # Deduplication
    is_duplicate = Column(Boolean, default=False, nullable=False)
    duplicate_of_id = Column(
        BigIntPK, ForeignKey("complaints.id", ondelete="SET NULL"), nullable=True
    )
    dedup_confidence_score = Column(Float, nullable=True)  # 0.0 – 1.0

    # NLP derived fields
    nlp_category = Column(String(100), nullable=True)   # e.g. "road", "drainage"
    nlp_keywords = Column(JSON, nullable=True)          # extracted keyword list
    sentiment_score = Column(Float, nullable=True)       # -1.0 (neg) to +1.0 (pos)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Day-14 RTI auto-filing deadline
    rti_deadline = Column(DateTime(timezone=True), nullable=True)
    rti_filed = Column(Boolean, default=False, nullable=False)

    # Relationships
    ward = relationship("Ward", back_populates="complaints")
    images = relationship(
        "ComplaintImage", back_populates="complaint", cascade="all, delete-orphan"
    )
    escalations = relationship(
        "Escalation", back_populates="complaint", cascade="all, delete-orphan"
    )
    tender_matches = relationship(
        "TenderMatch", back_populates="complaint", cascade="all, delete-orphan"
    )
    rti_requests = relationship(
        "RTIRequest", back_populates="complaint", cascade="all, delete-orphan"
    )
    duplicate_complaint = relationship(
        "Complaint", remote_side="Complaint.id", foreign_keys=[duplicate_of_id]
    )


class ComplaintImage(Base):
    """
    Images attached to a complaint, stored as file paths.
    Used by the CV deduplication service.
    """

    __tablename__ = "complaint_images"

    id = Column(BigIntPK, primary_key=True, index=True, autoincrement=True)
    complaint_id = Column(
        BigIntPK,
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_path = Column(Text, nullable=False)           # absolute or S3 URI
    file_hash = Column(String(64), nullable=True)      # SHA-256 for fast equality
    cv_feature_vector = Column(JSON, nullable=True)   # serialised ORB/SIFT descriptors
    uploaded_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    complaint = relationship("Complaint", back_populates="images")


# ===========================================================================
# Projects & PFMS Fund Flows
# ===========================================================================

class Project(Base):
    """Government infrastructure / development project."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pfms_project_code = Column(String(100), unique=True, nullable=False)
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    scheme_name = Column(String(300), nullable=True)   # e.g. MGNREGA, PMAY

    total_sanctioned_amount = Column(Numeric(20, 2), nullable=True)
    total_released_amount = Column(Numeric(20, 2), nullable=True)
    total_utilised_amount = Column(Numeric(20, 2), nullable=True)

    ward_id = Column(Integer, ForeignKey("wards.id", ondelete="SET NULL"), nullable=True)
    contractor_id = Column(
        Integer, ForeignKey("contractors.id", ondelete="SET NULL"), nullable=True
    )

    start_date = Column(DateTime(timezone=True), nullable=True)
    expected_completion_date = Column(DateTime(timezone=True), nullable=True)
    actual_completion_date = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    fund_flows = relationship("FundFlow", back_populates="project")
    tenders    = relationship("Tender",   back_populates="project")
    # Reciprocal of Contractor.projects (back_populates="contractor")
    contractor = relationship("Contractor", back_populates="projects", foreign_keys=[contractor_id])



class FundFlow(Base):
    """
    Individual PFMS fund disbursement / utilisation record.
    Maps money movement from central/state treasury to implementing agency.
    """

    __tablename__ = "fund_flows"

    id = Column(BigIntPK, primary_key=True, index=True, autoincrement=True)
    project_id = Column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )

    pfms_transaction_id = Column(String(200), unique=True, nullable=True)
    flow_type = Column(
        Enum(FundFlowType, name="fund_flow_type"),
        nullable=False,
        index=True,
    )

    amount = Column(Numeric(20, 2), nullable=False)
    currency = Column(String(3), default="INR", nullable=False)

    # Treasury / agency chain
    releasing_authority = Column(String(300), nullable=True)
    receiving_agency = Column(String(300), nullable=True)
    beneficiary_account = Column(String(100), nullable=True)

    # Raw PFMS payload preserved for audit
    raw_pfms_payload = Column(JSON, nullable=True)

    transaction_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    # Anomaly flags
    is_flagged = Column(Boolean, default=False, nullable=False)
    flag_reason = Column(Text, nullable=True)

    project = relationship("Project", back_populates="fund_flows")


# ===========================================================================
# Contractors & Shell-Company Network
# ===========================================================================

class Contractor(Base):
    """
    Registered contractor / vendor entity.
    Multiple contractors sharing directors, addresses, or bid patterns
    are linked as a shell-company network.
    """

    __tablename__ = "contractors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_name = Column(String(500), nullable=False)
    registration_number = Column(String(100), unique=True, nullable=True)
    pan_number = Column(String(20), unique=True, nullable=True)
    gst_number = Column(String(20), unique=True, nullable=True)

    registered_address = Column(Text, nullable=True)
    registered_address_lat = Column(Float, nullable=True)
    registered_address_lon = Column(Float, nullable=True)

    # Risk assessment
    is_shell_company_suspect = Column(Boolean, default=False, nullable=False)
    shell_network_cluster_id = Column(Integer, nullable=True, index=True)
    risk_score = Column(Float, default=0.0, nullable=False)  # 0.0 – 1.0

    blacklisted = Column(Boolean, default=False, nullable=False)
    blacklist_reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    directors = relationship(
        "ContractorDirector", back_populates="contractor", cascade="all, delete-orphan"
    )
    tenders = relationship("Tender", back_populates="awarded_contractor")
    projects = relationship("Project", back_populates="contractor")


class ContractorDirector(Base):
    """
    Director / beneficial owner of a contractor entity.
    Shared directors across companies reveal shell networks.
    """

    __tablename__ = "contractor_directors"
    __table_args__ = (
        UniqueConstraint("contractor_id", "din_number", name="uq_contractor_director_din"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    contractor_id = Column(
        Integer,
        ForeignKey("contractors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    full_name = Column(String(300), nullable=False)
    din_number = Column(String(20), nullable=True)   # Director Identification Number
    pan_number = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    contractor = relationship("Contractor", back_populates="directors")


# ===========================================================================
# Tenders
# ===========================================================================

class Tender(Base):
    """Public procurement tender record."""

    __tablename__ = "tenders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tender_id = Column(String(200), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    department = Column(String(300), nullable=True)

    estimated_value = Column(Numeric(20, 2), nullable=True)
    awarded_value = Column(Numeric(20, 2), nullable=True)

    project_id = Column(
        Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True
    )
    awarded_contractor_id = Column(
        Integer,
        ForeignKey("contractors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    published_at = Column(DateTime(timezone=True), nullable=True)
    awarded_at = Column(DateTime(timezone=True), nullable=True)

    # NLP embedding stored as JSON array for similarity search
    nlp_embedding = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    project = relationship("Project", back_populates="tenders")
    awarded_contractor = relationship("Contractor", back_populates="tenders")
    tender_matches = relationship("TenderMatch", back_populates="tender")


# ===========================================================================
# NLP Tender Matches
# ===========================================================================

class TenderMatch(Base):
    """
    NLP-derived association between a public complaint and a tender.
    High-confidence matches suggest the reported issue relates to a
    funded project that may have been poorly executed.
    """

    __tablename__ = "tender_matches"
    __table_args__ = (
        UniqueConstraint("complaint_id", "tender_id", name="uq_complaint_tender"),
    )

    id = Column(BigIntPK, primary_key=True, index=True, autoincrement=True)
    complaint_id = Column(
        BigIntPK,
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tender_id = Column(
        Integer,
        ForeignKey("tenders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    similarity_score = Column(Float, nullable=False)           # cosine similarity 0–1
    keyword_overlap_score = Column(Float, nullable=True)       # Jaccard keyword overlap
    combined_confidence = Column(Float, nullable=False)        # weighted final score

    matched_keywords = Column(JSON, nullable=True)           # list of overlapping terms
    shell_company_flagged = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    complaint = relationship("Complaint", back_populates="tender_matches")
    tender = relationship("Tender", back_populates="tender_matches")


# ===========================================================================
# Escalations
# ===========================================================================

class Escalation(Base):
    """
    One escalation event in the sequential authority chain:
    Ward Officer → MLA → District Collector → State Authority.
    """

    __tablename__ = "escalations"

    id = Column(BigIntPK, primary_key=True, index=True, autoincrement=True)
    complaint_id = Column(
        BigIntPK,
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    tier = Column(
        Enum(EscalationTier, name="escalation_tier"),
        nullable=False,
    )
    status = Column(
        Enum(EscalationStatus, name="escalation_status"),
        default=EscalationStatus.PENDING,
        nullable=False,
    )

    # Who it was routed to
    assigned_to_name = Column(String(300), nullable=True)
    assigned_to_email = Column(String(254), nullable=True)
    assigned_to_phone = Column(String(20), nullable=True)

    notification_sent_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Escalate if unacknowledged after this deadline
    escalate_after = Column(DateTime(timezone=True), nullable=True)

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    complaint = relationship("Complaint", back_populates="escalations")


# ===========================================================================
# RTI Requests
# ===========================================================================

class RTIRequest(Base):
    """
    Auto-generated Right to Information request record.
    Created on Day 14 of non-resolution for a complaint.
    """

    __tablename__ = "rti_requests"

    id = Column(BigIntPK, primary_key=True, index=True, autoincrement=True)
    complaint_id = Column(
        BigIntPK,
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    reference_number = Column(String(100), unique=True, nullable=True)
    pdf_file_path = Column(Text, nullable=False)           # local path or S3 URI
    addressed_to = Column(String(500), nullable=True)      # PIO / authority
    subject = Column(String(1000), nullable=True)

    # Filing metadata
    filed_at = Column(DateTime(timezone=True), nullable=True)
    filing_channel = Column(String(100), nullable=True)    # e.g. "email", "portal"
    acknowledgement_number = Column(String(200), nullable=True)

    auto_generated = Column(Boolean, default=True, nullable=False)  # Day-14 trigger
    generation_triggered_at = Column(DateTime(timezone=True), default=_utcnow)

    created_at = Column(DateTime(timezone=True), default=_utcnow, nullable=False)

    complaint = relationship("Complaint", back_populates="rti_requests")
