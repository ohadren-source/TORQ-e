"""
Card 2 (UPID) API Routes: Provider System
REAL DATA: Queries provider enrollment and claim data from public repositories via public_data_schema
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional, Dict
import asyncio

from database import get_db
from models import Provider
from .schemas import (
    ProviderLookupRequest, ProviderIdentityResponse,
    ProviderEnrollmentCheckRequest, ProviderEnrollmentStatusResponse,
    ClaimSubmissionRequest, ClaimValidationResponse, ClaimRoutingResponse, ClaimSubmissionResponse,
    ClaimStatusRequest, ClaimStatusResponse,
    FraudAnalysisRequest, FraudSignalResponse
)
from .provider_lookup import ProviderLookupExecutor
from .claims_routing import ClaimValidator, ClaimRouter, ClaimMonitor
from .fraud_detection import FraudDetectionEngine

router = APIRouter(prefix="/api/card2", tags=["Card 2 - Provider System"])

# ============================================================================
# DEPENDENCY: Get Public Data Schema from App State
# ============================================================================

def get_public_data_schema(request: Request) -> Optional[Dict]:
    """
    Retrieve public_data_schema from app.state.
    Populated by data_crawler.py on startup.
    """
    try:
        return getattr(request.app.state, 'public_data_schema', None)
    except:
        return None

# ============================================================================
# PROVIDER IDENTIFICATION (River Path)
# ============================================================================

@router.post("/lookup", response_model=ProviderIdentityResponse)
async def lookup_provider(
    request: ProviderLookupRequest,
    db: Session = Depends(get_db),
    public_data_schema: Optional[Dict] = Depends(get_public_data_schema)
):
    """
    Look up provider by NPI
    Executes River Path across REAL public provider data sources (eMedNY, MCO panels, NPI database)
    """
    try:
        provider_lookup = ProviderLookupExecutor(db, public_data_schema=public_data_schema)
        result = await provider_lookup.execute(
            npi=request.npi,
            first_name=request.first_name,
            last_name=request.last_name
        )

        if result.error:
            provider_lookup.log_query("PROVIDER", "ESCALATED")
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "PROVIDER_NOT_FOUND",
                    "message": result.error,
                    "escalation_action": "Verify NPI or contact EMEDNY"
                }
            )

        provider = provider_lookup.save_provider_to_db()
        provider_lookup.log_query("PROVIDER", "SUCCESS")

        return ProviderIdentityResponse(
            upid=result.upid,
            npi=request.npi,
            first_name=request.first_name,
            last_name=request.last_name,
            practice_name=result.provider_data.get("practice_name"),
            specialty=result.provider_data.get("specialty"),
            data_source=result.data_source.value if result.data_source else "UNKNOWN",
            confidence_score=result.confidence,
            caveats=result.caveats,
            status="SUCCESS"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# PROVIDER ENROLLMENT
# ============================================================================

@router.post("/enrollment/check", response_model=ProviderEnrollmentStatusResponse)
async def check_enrollment_status(
    request: ProviderEnrollmentCheckRequest,
    db: Session = Depends(get_db),
    public_data_schema: Optional[Dict] = Depends(get_public_data_schema)
):
    """
    Check provider's enrollment status (FFS + MCOs)
    Queries REAL enrollment data from public repositories
    Returns detailed breakdown of where provider is enrolled
    """
    try:
        provider = db.query(Provider).filter(Provider.upid == request.upid).first()
        if not provider:
            raise HTTPException(status_code=404, detail="Provider not found")

        # Get MCO enrollments
        mco_enrollments = {}
        if provider.mco_enrollments:
            for mco_enroll in provider.mco_enrollments:
                mco_enrollments[mco_enroll.mco_name] = mco_enroll.status.value

        # Compute confidence score
        # Higher confidence if credentials valid, enrolled in multiple plans, FFS active
        confidence = 0.90 if (provider.license_status.value == "VALID" and provider.ffs_enrolled and len([m for m in mco_enrollments.values() if m == "ACTIVE"]) > 0) else \
                    0.75 if (provider.license_status.value == "VALID" or provider.ffs_enrolled) else \
                    0.50

        return ProviderEnrollmentStatusResponse(
            upid=request.upid,
            npi=provider.npi,
            ffs_status=provider.ffs_status.value if provider.ffs_status else "UNKNOWN",
            ffs_claims_portal="ePACES" if provider.ffs_enrolled else None,
            mco_enrollments=mco_enrollments,
            total_plans=len([m for m in mco_enrollments.values() if m == "ACTIVE"]),
            credentials_valid=provider.license_status.value == "VALID" if provider.license_status else False,
            confidence_score=confidence,
            message_for_provider=f"You are enrolled in {len([m for m in mco_enrollments.values() if m == 'ACTIVE'])} MCO plans" +
                               (" and FFS" if provider.ffs_enrolled else ""),
            next_steps="Contact MCO or EMEDNY with questions" if provider.ffs_status else "Apply to EMEDNY for FFS enrollment"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CLAIM SUBMISSION
# ============================================================================

@router.post("/claims/validate", response_model=ClaimValidationResponse)
async def validate_claim(
    request: ClaimSubmissionRequest,
    db: Session = Depends(get_db),
    public_data_schema: Optional[Dict] = Depends(get_public_data_schema)
):
    """
    Validate claim before submission
    Queries REAL claim validation rules from public repositories
    Prevents dirty claims from being submitted
    """
    try:
        validator = ClaimValidator(db, public_data_schema=public_data_schema)
        claim_dict = request.dict()
        is_valid, report = validator.validate_claim(claim_dict)

        # Compute confidence score
        # Higher confidence if no errors and few warnings
        confidence = 0.95 if (len(report["errors"]) == 0 and len(report["warnings"]) == 0) else \
                    0.75 if (len(report["errors"]) == 0) else \
                    0.40

        return ClaimValidationResponse(
            valid=report["valid"],
            errors=report["errors"],
            warnings=report["warnings"],
            confidence_score=confidence,
            action=report["action"],
            message=report["message"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/claims/submit", response_model=ClaimSubmissionResponse)
async def submit_claim(
    request: ClaimSubmissionRequest,
    db: Session = Depends(get_db),
    public_data_schema: Optional[Dict] = Depends(get_public_data_schema)
):
    """
    Submit validated claim with intelligent routing
    Routes claims based on REAL enrollment data from public repositories
    """
    try:
        # Validate first
        validator = ClaimValidator(db, public_data_schema=public_data_schema)
        claim_dict = request.dict()
        is_valid, validation_report = validator.validate_claim(claim_dict)

        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "CLAIM_VALIDATION_FAILED",
                    "errors": validation_report["errors"],
                    "message": "Fix errors before submitting"
                }
            )

        # Route claim
        router = ClaimRouter(db, public_data_schema=public_data_schema)
        routing = router.route_claim(claim_dict)

        if "error" in routing:
            raise HTTPException(status_code=404, detail=routing["error"])

        # Submit
        submission = router.submit_claim(request.provider_upid, claim_dict, routing)

        return ClaimSubmissionResponse(**submission)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CLAIM STATUS TRACKING
# ============================================================================

@router.post("/claims/status", response_model=ClaimStatusResponse)
async def check_claim_status(
    request: ClaimStatusRequest,
    db: Session = Depends(get_db),
    public_data_schema: Optional[Dict] = Depends(get_public_data_schema)
):
    """
    Check claim status with automatic escalation if past deadline
    Queries REAL claim processing timelines from public repositories
    """
    try:
        monitor = ClaimMonitor(db, public_data_schema=public_data_schema)
        status_data = monitor.check_claim_status(request.claim_id)

        if "error" in status_data:
            raise HTTPException(status_code=404, detail=status_data["error"])

        return ClaimStatusResponse(**status_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# FRAUD DETECTION
# ============================================================================

@router.post("/fraud/analyze", response_model=FraudSignalResponse)
async def analyze_claim_for_fraud(
    request: FraudAnalysisRequest,
    db: Session = Depends(get_db),
    public_data_schema: Optional[Dict] = Depends(get_public_data_schema)
):
    """
    Analyze claim for fraud signals in real-time
    Compares against REAL provider/member data from public repositories
    """
    try:
        engine = FraudDetectionEngine(db, public_data_schema=public_data_schema)
        analysis = engine.analyze_claim(
            request.claim_data,
            request.provider_upid,
            request.member_umid
        )

        return FraudSignalResponse(**analysis)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
