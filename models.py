from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Enum, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

Base = declarative_base()

# ============================================================================
# CARD 1: UMID (Unified Member Identity & Data)
# ============================================================================

class EligibilityStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PENDING = "PENDING"
    DENIED = "DENIED"

class PlanType(str, enum.Enum):
    FFS = "FFS"  # Fee-For-Service
    MCO = "MCO"  # Managed Care Organization
    SNP = "SNP"  # Special Needs Plan

class DataSource(str, enum.Enum):
    STATE_MEDICAID = "STATE_MEDICAID"
    SSA_WAGE_RECORDS = "SSA_WAGE_RECORDS"
    HOUSEHOLD_ENROLLMENT = "HOUSEHOLD_ENROLLMENT"
    NPI_DATABASE = "NPI_DATABASE"

class Member(Base):
    __tablename__ = "members"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    umid = Column(String, unique=True, index=True)  # Unified Member ID

    # Personal identifiers
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(String, nullable=False)  # YYYY-MM-DD
    ssn = Column(String, unique=True, index=True)  # Encrypted in production

    # Contact
    address = Column(String)
    phone_number = Column(String)
    email = Column(String)

    # Enrollment
    state_case_number = Column(String, unique=True, index=True)
    household_id = Column(String)

    # Data source tracking
    primary_data_source = Column(Enum(DataSource))
    last_verified_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    eligibility_records = relationship("MemberEligibility", back_populates="member")
    plan_assignments = relationship("MemberPlanAssignment", back_populates="member")
    documents = relationship("MemberDocument", back_populates="member")
    audit_logs = relationship("AuditLog", back_populates="member")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MemberEligibility(Base):
    __tablename__ = "member_eligibility"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    member_id = Column(String, ForeignKey("members.id"), nullable=False, index=True)

    # Eligibility status
    status = Column(Enum(EligibilityStatus), nullable=False)
    eligibility_group = Column(String)  # e.g., "Parent/Caretaker", "Pregnant", "Disabled"

    # Coverage period
    coverage_start_date = Column(String)  # YYYY-MM-DD
    coverage_end_date = Column(String)
    recertification_date = Column(String)

    # Income & assets
    reported_income = Column(Float)
    income_limit = Column(Float)
    assets = Column(Float)
    assets_limit = Column(Float)
    lookback_period_months = Column(Integer, default=3)

    # Application details
    application_date = Column(String)
    approval_date = Column(String)
    denial_reason = Column(Text)

    # Flags for escalation
    needs_manual_review = Column(Boolean, default=False)
    recert_alert_sent = Column(Boolean, default=False)

    # Confidence in this determination
    confidence_score = Column(Float)  # 0.0 to 1.0
    confidence_reason = Column(Text)  # Explanation of how confidence was determined

    # Relationships
    member = relationship("Member", back_populates="eligibility_records")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MemberPlanAssignment(Base):
    __tablename__ = "member_plan_assignments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    member_id = Column(String, ForeignKey("members.id"), nullable=False, index=True)

    # Plan assignment
    plan_name = Column(String)  # e.g., "Empire BCBS", "Aetna", "FFS"
    plan_type = Column(Enum(PlanType))
    plan_mco_id = Column(String)  # For MCO plans

    # Assignment type
    is_default = Column(Boolean, default=False)
    assignment_effective_date = Column(String)
    assignment_end_date = Column(String)

    # Network status
    in_network = Column(Boolean, default=True)
    network_verification_date = Column(DateTime)

    # Special needs tracking
    is_snp = Column(Boolean, default=False)
    snp_specialty = Column(String)  # e.g., "Chronic Conditions", "Disability"

    # Member services
    plan_member_services_phone = Column(String)
    plan_claims_portal_url = Column(String)

    # Relationships
    member = relationship("Member", back_populates="plan_assignments")

    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MemberDocument(Base):
    __tablename__ = "member_documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    member_id = Column(String, ForeignKey("members.id"), nullable=False, index=True)

    # Document details
    document_type = Column(String)  # e.g., "ID", "Pay Stub", "Address Proof"
    document_filename = Column(String)
    document_path = Column(String)  # Path to encrypted storage

    # OCR extraction
    extracted_name = Column(String)
    extracted_dob = Column(String)
    extracted_address = Column(String)
    extracted_date = Column(String)
    extracted_expiration_date = Column(String)

    # Verification
    legibility_score = Column(Float)  # 0.0 to 1.0
    verification_status = Column(String)  # "VERIFIED", "MANUAL_REVIEW", "REJECTED"

    # Relationships
    member = relationship("Member", back_populates="documents")

    uploaded_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    member_id = Column(String, ForeignKey("members.id"), nullable=False, index=True)

    # Query details
    query_type = Column(String)  # e.g., "eligibility_check", "plan_lookup", "recert_alert"
    request_source = Column(String)  # e.g., "MEMBER", "PROVIDER", "ANALYST"

    # Results
    result_status = Column(String)  # e.g., "SUCCESS", "ESCALATED", "ERROR"
    result_confidence = Column(Float)

    # Tracking
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(String)  # For tracking who requested the query
    ip_address = Column(String)

    # Relationships
    member = relationship("Member", back_populates="audit_logs")


# ============================================================================
# CARD 2: UPID (Unified Provider Identity & Data)
# ============================================================================

class ProviderEnrollmentStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"
    PENDING = "PENDING"
    NOT_ENROLLED = "NOT_ENROLLED"

class CredentialStatus(str, enum.Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    EXPIRED = "EXPIRED"
    PENDING = "PENDING"

class Provider(Base):
    __tablename__ = "providers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    upid = Column(String, unique=True, index=True)  # Unified Provider ID

    # Identification
    npi = Column(String, unique=True, index=True)  # National Provider ID
    first_name = Column(String)
    last_name = Column(String)
    practice_name = Column(String)

    # License & credentials
    state_license_number = Column(String)
    license_state = Column(String)
    specialty = Column(String)

    # Practice details
    practice_address = Column(String)
    practice_phone = Column(String)
    practice_website = Column(String)

    # Enrollment info
    ffs_enrolled = Column(Boolean, default=False)
    ffs_tax_id = Column(String)
    ffs_status = Column(Enum(ProviderEnrollmentStatus))
    ffs_enrollment_date = Column(String)

    # Credentials tracking
    license_status = Column(Enum(CredentialStatus))
    malpractice_insurance_active = Column(Boolean)
    federal_exclusion_status = Column(String)  # "EXCLUDED" or "CLEAR"
    federal_exclusion_effective_date = Column(String)

    # Relationships
    mco_enrollments = relationship("ProviderMCOEnrollment", back_populates="provider")
    claims = relationship("Claim", back_populates="provider")
    audit_logs = relationship("ProviderAuditLog", back_populates="provider")

    last_verified_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProviderMCOEnrollment(Base):
    __tablename__ = "provider_mco_enrollments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    provider_id = Column(String, ForeignKey("providers.id"), nullable=False, index=True)

    # MCO details
    mco_name = Column(String)  # e.g., "Empire BCBS", "Aetna Medicaid"
    mco_id = Column(String, unique=True, index=True)

    # Enrollment status
    status = Column(Enum(ProviderEnrollmentStatus))
    enrollment_date = Column(String)
    termination_date = Column(String)

    # Network type
    network_type = Column(String)  # "IN_NETWORK", "CONTRACTED", "OUT_OF_NETWORK"

    # Claims submission
    claims_portal_url = Column(String)
    claims_submitter_id = Column(String)

    # Payment
    mco_tax_id = Column(String)
    payment_method = Column(String)  # "Direct Deposit", "Check", "EFT"

    # Member services
    member_services_phone = Column(String)

    # Relationships
    provider = relationship("Provider", back_populates="mco_enrollments")

    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ClaimStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    PAID = "PAID"
    DENIED = "DENIED"
    APPEALED = "APPEALED"
    ESCALATED = "ESCALATED"

class Claim(Base):
    __tablename__ = "claims"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    claim_id = Column(String, unique=True, index=True)

    # Provider & member
    provider_id = Column(String, ForeignKey("providers.id"), nullable=False, index=True)
    member_umid = Column(String, index=True)  # Reference to UMID (for audit trail)

    # Service details
    service_date = Column(String)
    service_type = Column(String)  # e.g., "Office Visit", "Lab Test"
    procedure_code = Column(String)  # CPT code
    diagnosis_code = Column(String)  # ICD-10 code

    # Claim details
    submitted_date = Column(DateTime, default=datetime.utcnow, index=True)
    routing_plan = Column(String)  # Which plan this was routed to
    claims_portal_submitted = Column(String)  # Which portal it was sent to
    confirmation_number = Column(String)

    # Amount
    claim_amount = Column(Float)
    approved_amount = Column(Float)
    paid_amount = Column(Float)
    patient_responsibility = Column(Float)

    # Status tracking
    status = Column(Enum(ClaimStatus), index=True)
    status_last_updated = Column(DateTime)
    expected_payment_date = Column(String)
    actual_payment_date = Column(String)

    # Denial/Appeal info
    denial_reason = Column(Text)
    denial_date = Column(String)
    appeal_submitted_date = Column(String)
    appeal_decision = Column(String)

    # inauthenticity flags
    fraud_risk_score = Column(Float)  # 0.0 to 1.0
    fraud_flags = Column(Text)  # JSON array of flag descriptions

    # Relationships
    provider = relationship("Provider", back_populates="claims")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProviderAuditLog(Base):
    __tablename__ = "provider_audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    provider_id = Column(String, ForeignKey("providers.id"), nullable=False, index=True)

    # Query details
    query_type = Column(String)  # e.g., "enrollment_check", "credential_verify", "claim_submit"
    request_source = Column(String)

    # Results
    result_status = Column(String)

    # Relationships
    provider = relationship("Provider", back_populates="audit_logs")

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(String)


# ============================================================================
# GOVERNANCE, INVESTIGATIONS, SOURCE MANAGEMENT (Cards 4 & 5)
# ============================================================================

class GovernanceActionType(str, enum.Enum):
    DATA_QUALITY_ISSUE = "DATA_QUALITY_ISSUE"
    FRAUD_SUSPICION = "FRAUD_SUSPICION"
    COMPLIANCE_GAP = "COMPLIANCE_GAP"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    DATA_CORRECTION = "DATA_CORRECTION"
    POLICY_CHANGE = "POLICY_CHANGE"

class GovernanceStatus(str, enum.Enum):
    FLAGGED = "FLAGGED"
    INVESTIGATING = "INVESTIGATING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CLOSED = "CLOSED"

class SourceReliabilityLevel(str, enum.Enum):
    AUTHORITATIVE = "AUTHORITATIVE"  # 0.95+
    HIGH = "HIGH"                    # 0.85-0.94
    MEDIUM = "MEDIUM"                # 0.70-0.84
    LOW = "LOW"                      # 0.50-0.69
    UNRELIABLE = "UNRELIABLE"        # <0.50 or struck

class GovernanceFlag(Base):
    """Governance action: Flag data issue, inauthenticity suspicion, compliance gap, etc."""
    __tablename__ = "governance_flags"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Flag details
    action_type = Column(Enum(GovernanceActionType), nullable=False, index=True)
    status = Column(Enum(GovernanceStatus), default=GovernanceStatus.FLAGGED, index=True)

    # Domain (what it affects)
    domain = Column(String)  # e.g., "claims", "enrollment", "provider_data", "member_data"
    domain_id = Column(String, index=True)  # Reference to specific record (claim_id, umid, upid, etc.)

    # Content
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    justification = Column(Text)  # Why this flag was raised
    evidence_links = Column(Text)  # JSON array of URLs/references

    # Governance workflow
    flagged_by = Column(String, nullable=False)  # User ID of who flagged
    flagged_at = Column(DateTime, default=datetime.utcnow, index=True)

    assigned_to = Column(String)  # User investigating
    approved_by = Column(String)  # User who approved action
    approved_at = Column(DateTime)

    # Resolution
    resolution_notes = Column(Text)
    resolved_at = Column(DateTime)

    # Audit trail
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GovernanceApproval(Base):
    """Approval record for governance actions"""
    __tablename__ = "governance_approvals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Reference to flag
    flag_id = Column(String, ForeignKey("governance_flags.id"), nullable=False, index=True)

    # Approval details
    approved_by = Column(String, nullable=False)
    approved_at = Column(DateTime, default=datetime.utcnow)
    approval_notes = Column(Text)

    # For appeal/rejection
    is_approved = Column(Boolean, nullable=False)
    rejection_reason = Column(Text)


class AuditLogEntry(Base):
    """Immutable governance audit trail (separate from member/provider audit logs)"""
    __tablename__ = "governance_audit_log"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # What action
    action = Column(String, nullable=False, index=True)  # "FLAG", "STRIKE_SOURCE", "ADD_SOURCE", "APPROVE_FLAG", etc.
    action_type = Column(String)  # Category for filtering

    # Who did it
    actor_id = Column(String, nullable=False, index=True)  # User ID
    actor_role = Column(String)  # USHI, UBADA, Admin

    # What changed
    domain = Column(String, index=True)  # "governance", "source_management", "investigation"
    domain_id = Column(String, index=True)  # Reference to affected record
    change_summary = Column(String)
    change_details = Column(Text)  # JSON object with before/after

    # Why
    justification = Column(Text)
    evidence = Column(Text)  # JSON array of supporting evidence

    # Immutability
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    # NOTE: In production, this table is append-only. No updates, no deletes.

    created_at = Column(DateTime, default=datetime.utcnow)


class InvestigationProject(Base):
    """authenticity investigation project (Card 5)"""
    __tablename__ = "investigation_projects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Project identity
    case_number = Column(String, unique=True, index=True)  # e.g., "FR-2026-04-0847"
    title = Column(String, nullable=False)
    description = Column(Text)

    # Focus
    investigation_type = Column(String)  # "inauthenticity", "data_quality", "pattern_analysis"
    suspect_entity_type = Column(String)  # "provider", "member", "claim_pattern"
    suspect_entity_id = Column(String, index=True)  # upid, umid, claim_id

    # Team
    lead_analyst = Column(String, nullable=False)  # User ID
    team_members = Column(Text)  # JSON array of user IDs

    # Status
    status = Column(String, default="OPEN", index=True)  # OPEN, INVESTIGATING, ESCALATED, CLOSED, ARCHIVED
    severity = Column(String)  # LOW, MEDIUM, HIGH, CRITICAL

    # Findings
    findings_summary = Column(Text)
    confidence_in_findings = Column(Float)  # 0.0 to 1.0
    risk_score = Column(Float)  # inauthenticity likelihood

    # Workflow
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    escalated_at = Column(DateTime)
    closed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InvestigationComment(Base):
    """Comments on investigation (collaboration)"""
    __tablename__ = "investigation_comments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Reference
    project_id = Column(String, ForeignKey("investigation_projects.id"), nullable=False, index=True)

    # Content
    comment_by = Column(String, nullable=False)  # User ID
    comment = Column(Text, nullable=False)
    comment_type = Column(String)  # "note", "finding", "question", "evidence"

    # Evidence attachment
    evidence_attachment = Column(Text)  # URL or reference

    # Status
    requires_response = Column(Boolean, default=False)
    resolved = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DataCorrection(Base):
    """Proposal to fix data in system"""
    __tablename__ = "data_corrections"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # What's being fixed
    domain = Column(String, nullable=False)  # "member_data", "provider_data", "claim_data", "field_mapping"
    domain_id = Column(String, nullable=False, index=True)  # What record is being fixed
    field_name = Column(String, nullable=False)  # What field

    # Change
    current_value = Column(Text)
    proposed_value = Column(Text)
    change_reason = Column(Text, nullable=False)

    # Proposer
    proposed_by = Column(String, nullable=False)
    proposed_at = Column(DateTime, default=datetime.utcnow)

    # Approval
    approved_by = Column(String)
    approved_at = Column(DateTime)
    approval_notes = Column(Text)

    # Applied
    applied = Column(Boolean, default=False)
    applied_at = Column(DateTime)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OutlierFinding(Base):
    """inauthenticity signal finding (statistical anomaly)"""
    __tablename__ = "outlier_findings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Outlier details
    entity_type = Column(String)  # "provider", "member", "claim_pattern"
    entity_id = Column(String, index=True)  # upid, umid, etc.

    # Metric & scores
    metric = Column(String)  # "billing_amount", "claim_approval_rate", "referral_concentration"
    metric_value = Column(Float)
    peer_average = Column(Float)
    z_score = Column(Float)  # Standard deviations from mean
    percentile = Column(Float)  # 0-100

    # Confidence
    confidence = Column(Float)  # 0.0 to 1.0
    sample_size = Column(Integer)  # How many data points

    # Risk assessment
    risk_level = Column(String)  # LOW, MEDIUM, HIGH, CRITICAL
    risk_score = Column(Float)  # 0.0 to 1.0

    # Investigation link
    investigation_id = Column(String, ForeignKey("investigation_projects.id"))

    # Detection
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    detected_by = Column(String)  # System vs analyst

    created_at = Column(DateTime, default=datetime.utcnow)


class SourceRegistry(Base):
    """Master list of all data sources (eMedNY, MCO, NPI, SSA, etc.)"""
    __tablename__ = "source_registry"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Source identity
    source_name = Column(String, unique=True, nullable=False, index=True)  # e.g., "eMedNY FFS", "MCO Aggregator", "NPI Database"
    source_type = Column(String)  # "state", "federal", "mco", "external", "internal"
    source_url = Column(String)

    # Reliability
    quality_score = Column(Float)  # 0.0 to 1.0 (how authoritative)
    reliability_level = Column(Enum(SourceReliabilityLevel), default=SourceReliabilityLevel.MEDIUM)

    # Status
    active = Column(Boolean, default=True)
    struck = Column(Boolean, default=False)  # True if struck as unreliable
    strike_reason = Column(Text)
    strike_effective_date = Column(DateTime)

    # Usage
    last_queried = Column(DateTime)
    query_count = Column(Integer, default=0)
    success_rate = Column(Float)  # Percent of queries that returned data

    # Latency
    average_latency_seconds = Column(Float)
    max_latency_seconds = Column(Float)

    # Metadata
    contact_email = Column(String)
    sla_notes = Column(Text)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SourceAction(Base):
    """Immutable audit trail of source management decisions (strike/add/demote/upgrade)"""
    __tablename__ = "source_actions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # What source
    source_id = Column(String, ForeignKey("source_registry.id"), nullable=False, index=True)
    source_name = Column(String)  # Denormalized for readability

    # Action
    action = Column(String, nullable=False, index=True)  # "STRIKE", "ADD", "RESTORE", "DEMOTE", "UPGRADE"

    # Who & Why
    initiated_by = Column(String, nullable=False)
    initiated_at = Column(DateTime, default=datetime.utcnow, index=True)

    approved_by = Column(String)  # Empty until approved
    approved_at = Column(DateTime)

    # Justification
    reason = Column(Text, nullable=False)
    evidence = Column(Text)  # JSON array of evidence links

    # Impact
    expected_impact = Column(Text)  # What happens when this source is struck/added
    observed_impact = Column(Text)  # What actually happened

    # Timeline
    effective_date = Column(DateTime, nullable=False)
    restoration_date = Column(DateTime)  # If struck, when might it be restored

    # Immutability
    created_at = Column(DateTime, default=datetime.utcnow)


class SourceComparison(Base):
    """Track when sources disagree"""
    __tablename__ = "source_comparisons"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Query identity
    query_type = Column(String)  # "member_lookup", "provider_lookup", "eligibility_check"
    query_domain = Column(String)  # What domain
    query_domain_id = Column(String, index=True)  # Specific member/provider

    # Sources compared
    source_1_id = Column(String, ForeignKey("source_registry.id"), nullable=False)
    source_1_name = Column(String)
    source_1_result = Column(Text)  # JSON result
    source_1_confidence = Column(Float)

    source_2_id = Column(String, ForeignKey("source_registry.id"), nullable=False)
    source_2_name = Column(String)
    source_2_result = Column(Text)  # JSON result
    source_2_confidence = Column(Float)

    # Disagreement
    disagreement_detected = Column(Boolean, default=False)
    disagreement_percentage = Column(Float)  # 0-100 (how much they differ)
    disagreement_type = Column(String)  # "timing_lag", "definition_difference", "data_error", "genuine_change"

    # Resolution
    resolution = Column(Text)  # How we resolved it
    resolved_by = Column(String)  # User who investigated
    resolved_at = Column(DateTime)

    # Timestamps
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
