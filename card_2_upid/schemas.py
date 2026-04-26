"""
Pydantic schemas for Card 2 (UPID) API requests and responses
"""

from pydantic import BaseModel
from typing import Optional, List, Dict

# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class ProviderLookupRequest(BaseModel):
    """Request to lookup provider"""
    npi: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class ProviderEnrollmentCheckRequest(BaseModel):
    """Request to check provider enrollment status"""
    upid: str

class ClaimSubmissionRequest(BaseModel):
    """Request to submit claim"""
    member_umid: str
    provider_upid: str
    service_date: str  # YYYY-MM-DD
    procedure_code: str  # CPT code (5 digits)
    diagnosis_code: str  # ICD-10 code
    amount: float
    authorization_number: Optional[str] = None

class ClaimStatusRequest(BaseModel):
    """Request to check claim status"""
    claim_id: str

class FraudAnalysisRequest(BaseModel):
    """Request to analyze claim for inauthenticity"""
    claim_data: Dict
    provider_upid: str
    member_umid: str

# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class ProviderIdentityResponse(BaseModel):
    """Response with provider identity and UPID"""
    upid: str
    npi: str
    first_name: Optional[str]
    last_name: Optional[str]
    practice_name: Optional[str]
    specialty: Optional[str]
    data_source: str
    confidence_score: float
    caveats: Optional[str] = None  # Data quality warnings (conflict between sources, etc.)
    status: str

class ProviderEnrollmentStatusResponse(BaseModel):
    """Provider enrollment status"""
    upid: str
    npi: str
    ffs_status: str  # ACTIVE, SUSPENDED, TERMINATED, NOT_ENROLLED
    ffs_claims_portal: Optional[str]
    mco_enrollments: Dict  # MCO name -> status
    total_plans: int
    credentials_valid: bool
    confidence_score: float  # CRITICAL: Claude uses this for traffic light display
    message_for_provider: str
    next_steps: Optional[str]

class ClaimValidationResponse(BaseModel):
    """Claim validation result"""
    valid: bool
    errors: List[str]
    warnings: List[str]
    confidence_score: float  # CRITICAL: Claude uses this for traffic light display
    action: str  # SUBMIT or REJECT
    message: str

class ClaimRoutingResponse(BaseModel):
    """Claim routing information"""
    routing_plan: str
    claims_portal: str
    expected_payment_date: str
    payment_method: str
    tax_id: str

class ClaimSubmissionResponse(BaseModel):
    """Response after claim submission"""
    status: str
    claim_id: str
    confirmation_number: str
    routed_to: str
    expected_payment_date: str
    next_step: str

class ClaimStatusResponse(BaseModel):
    """Claim status tracking"""
    claim_id: str
    status: str  # SUBMITTED, PENDING, APPROVED, PAID, DENIED
    days_since_submission: int
    expected_payment_date: str
    escalation: Optional[str] = None
    action: Optional[str] = None

class FraudSignalResponse(BaseModel):
    """authenticity verification results"""
    risk_score: float
    risk_level: str  # LOW, MEDIUM, HIGH
    signals: List[str]
    r