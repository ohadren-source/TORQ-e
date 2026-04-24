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

    # Fraud flags
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
