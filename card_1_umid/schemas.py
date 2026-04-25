"""
Pydantic schemas for Card 1 (UMID) API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class MemberLookupRequest(BaseModel):
    """Request to lookup/identify a member"""
    first_name: str
    last_name: str
    date_of_birth: str = Field(..., description="YYYY-MM-DD format")
    ssn: str = Field(..., description="9-digit SSN")

class EligibilityCheckRequest(BaseModel):
    """Request to check member eligibility"""
    umid: str = Field(..., description="Unified Member ID")
    today_date: Optional[str] = Field(None, description="Date to check eligibility for (YYYY-MM-DD). Default: today")

class RecertificationCheckRequest(BaseModel):
    """Request to check recertification status"""
    umid: str

class DocumentUploadRequest(BaseModel):
    """Request to upload member document"""
    umid: str
    document_type: str = Field(..., description="ID, Pay Stub, Address Proof, etc.")
    document_filename: str
    document_base64: str = Field(..., description="Base64-encoded document image")

class IncomeReportRequest(BaseModel):
    """Request to report income change"""
    umid: str
    new_income: float
    income_source: str = Field(..., description="Wages, SSI, Self-employed, etc.")
    effective_date: str = Field(..., description="YYYY-MM-DD")

# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class MemberIdentityResponse(BaseModel):
    """Response with member identity and UMID"""
    umid: str
    first_name: str
    last_name: str
    date_of_birth: str
    state_case_number: Optional[str]
    data_source: str
    confidence_score: float
    flags: List[str]
    status: str  # "SUCCESS" or "ESCALATE"

class EligibilityStatusResponse(BaseModel):
    """Member-facing eligibility response (simplified)"""
    umid: str
    member_name: str
    are_you_covered: str  # "YES", "NO", "PENDING"
    coverage_until: Optional[str]
    next_recertification: Optional[str]
    days_until_recert: Optional[int]
    your_plan: Optional[str]
    plan_phone: Optional[str]
    questions_contact: str  # "Call [number]"
    confidence_score: float  # CRITICAL: Claude uses this for traffic light display
    caveats: Optional[str]

class EligibilityDetailedResponse(BaseModel):
    """Provider/Analyst-facing eligibility response (detailed)"""
    umid: str
    member_name: str
    eligibility_status: str  # ACTIVE, INACTIVE, PENDING, DENIED
    coverage_period: Dict  # {start_date, end_date}
    assigned_plan: Optional[str]
    plan_type: Optional[str]  # FFS or MCO
    confidence_score: float
    confidence_level: str  # HIGH, MEDIUM, LOW
    confidence_components: Dict
    data_sources_used: List[str]
    caveats: Optional[List[str]]
    analyst_recommendation: Optional[str]

class RecertificationStatusResponse(BaseModel):
    """Recertification deadline and status"""
    umid: str
    recertification_date: Optional[str]
    days_until_due: Optional[int]
    status: str  # "ON_TRACK", "ALERT_60_DAYS", "ALERT_URGENT", "OVERDUE"
    confidence_score: float  # CRITICAL: Claude uses this for traffic light display
    next_action: str
    upload_documents_here: Optional[str]

class DocumentUploadResponse(BaseModel):
    """Response after document upload"""
    document_id: str
    document_type: str
    upload_status: str  # "RECEIVED", "VERIFIED", "MANUAL_REVIEW", "REJECTED"
    legibility_score: Optional[float]
    verification_message: str
    next_step: str

class IncomeChangeResponse(BaseModel):
    """Response after income report"""
    umid: str
    current_income: float
    new_income: float
    income_limit: float
    impact_on_coverage: str  # "ELIGIBLE", "INELIGIBLE", "AT_LIMIT"
    member_message: str
    recommendation: str
    confidence_score: float

class ErrorResponse(BaseModel):
    """Error response"""
    error_code: str
    error_message: str
    escalation_needed: bool
    escalation_action: Optional[str]

class HealthCheckResponse(BaseModel):
    """API health check"""
    status: str  # "healthy", "degraded", "down"
    database: str
    timestamp: datetime
