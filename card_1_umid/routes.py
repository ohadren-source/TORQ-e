"""
Card 1 (UMID) API Routes: Member Eligibility System
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio

from database import get_db
from models import Member, MemberEligibility
from .schemas import (
    MemberLookupRequest, MemberIdentityResponse,
    EligibilityCheckRequest, EligibilityStatusResponse, EligibilityDetailedResponse,
    RecertificationCheckRequest, RecertificationStatusResponse,
    DocumentUploadRequest, DocumentUploadResponse,
    IncomeReportRequest, IncomeChangeResponse,
    ErrorResponse, HealthCheckResponse
)
from .river_path import RiverPathExecutor
from .eligibility import EligibilityDetermination
from .confidence import ConfidenceScorer, TieredConfidenceReporting

router = APIRouter(prefix="/api/card1", tags=["Card 1 - Member Eligibility"])

# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health", response_model=HealthCheckResponse)
async def health_check(db: Session = Depends(get_db)):
    """System health check"""
    try:
        # Try a simple query
        db.execute("SELECT 1")
        db_status = "healthy"
    except:
        db_status = "down"

    return HealthCheckResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        database=db_status,
        timestamp=datetime.utcnow()
    )

# ============================================================================
# MEMBER IDENTIFICATION (River Path)
# ============================================================================

@router.post("/lookup", response_model=MemberIdentityResponse)
async def lookup_member(
    request: MemberLookupRequest,
    db: Session = Depends(get_db)
):
    """
    Look up member by name, DOB, SSN
    Executes River Path algorithm across multiple data sources
    Returns UMID if successful
    """
    try:
        # Execute River Path
        river_path = RiverPathExecutor(db)
        result = await river_path.execute(
            first_name=request.first_name,
            last_name=request.last_name,
            dob=request.date_of_birth,
            ssn=request.ssn
        )

        if result.error:
            # River Path failed
            river_path.log_query("MEMBER", "ESCALATED")
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": "MEMBER_NOT_FOUND",
                    "error_message": result.error,
                    "escalation_needed": True,
                    "escalation_action": "Contact local Medicaid office or call 1-800-541-2831"
                }
            )

        # Save member to database
        member = river_path.save_member_to_db()
        river_path.log_query("MEMBER", "SUCCESS")

        return MemberIdentityResponse(
            umid=result.umid,
            first_name=request.first_name,
            last_name=request.last_name,
            date_of_birth=request.date_of_birth,
            state_case_number=result.member_data.get("state_case_number"),
            data_source=result.data_source.value,
            confidence_score=result.confidence,
            flags=result.flags,
            status="SUCCESS"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ELIGIBILITY CHECKING
# ============================================================================

@router.post("/eligibility/check", response_model=EligibilityStatusResponse)
async def check_eligibility_member_view(
    request: EligibilityCheckRequest,
    db: Session = Depends(get_db)
):
    """
    Check member eligibility (MEMBER-FACING VIEW)
    Returns simplified, plain-language response
    """
    try:
        # Get member
        member = db.query(Member).filter(Member.umid == request.umid).first()
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        # Determine eligibility
        eligibility_determiner = EligibilityDetermination(db, member)
        status, eligibility_record, confidence = eligibility_determiner.determine_status()

        # Get plan
        plan = eligibility_determiner.get_plan_assignment()

        # Generate confidence score
        scorer = ConfidenceScorer()
        confidence_dict = scorer.to_dict()
        confidence_dict["score"] = confidence

        # Get caveat if needed
        caveat = scorer.generate_caveat(
            confidence,
            {
                "application_status": status.value,
                "income_verified": eligibility_record.reported_income is not None,
                "documents_provided": 0,  # Count from database in production
                "days_since_verification": 0
            }
        )

        # Member-facing messaging
        are_you_covered = "YES" if status == "ACTIVE" else "NO" if status == "INACTIVE" else "PENDING"

        return EligibilityStatusResponse(
            umid=request.umid,
            member_name=f"{member.first_name} {member.last_name}",
            are_you_covered=are_you_covered,
            coverage_until=eligibility_record.coverage_end_date,
            next_recertification=eligibility_determiner.get_next_recertification_date(eligibility_record),
            days_until_recert=eligibility_determiner.get_days_until_recertification(eligibility_record),
            your_plan=plan.plan_name if plan else "Fee-For-Service (Default)",
            plan_phone=plan.plan_member_services_phone if plan else "1-800-541-2831",
            questions_contact="Call your plan or NY Medicaid at 1-800-541-2831",
            caveats=caveat
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/eligibility/detailed", response_model=EligibilityDetailedResponse)
async def check_eligibility_provider_view(
    request: EligibilityCheckRequest,
    db: Session = Depends(get_db)
):
    """
    Check member eligibility (PROVIDER/ANALYST-FACING VIEW)
    Returns detailed breakdown with confidence components
    """
    try:
        # Get member
        member = db.query(Member).filter(Member.umid == request.umid).first()
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        # Determine eligibility
        eligibility_determiner = EligibilityDetermination(db, member)
        status, eligibility_record, confidence = eligibility_determiner.determine_status()

        # Get plan
        plan = eligibility_determiner.get_plan_assignment()

        # Confidence scoring
        scorer = ConfidenceScorer()
        confidence_dict = scorer.to_dict()
        confidence_dict["score"] = confidence
        confidence_dict["level"] = scorer.get_confidence_level_label(confidence)

        return EligibilityDetailedResponse(
            umid=request.umid,
            member_name=f"{member.first_name} {member.last_name}",
            eligibility_status=status.value,
            coverage_period={
                "start_date": eligibility_record.coverage_start_date,
                "end_date": eligibility_record.coverage_end_date
            },
            assigned_plan=plan.plan_name if plan else None,
            plan_type=plan.plan_type.value if plan else "FFS",
            confidence_score=confidence,
            confidence_level=scorer.get_confidence_level_label(confidence),
            confidence_components=confidence_dict["components"],
            data_sources_used=[member.primary_data_source.value],
            caveats=[scorer.generate_caveat(confidence, {})],
            analyst_recommendation="APPROVE" if confidence >= 0.85 else "REVIEW" if confidence >= 0.60 else "ESCALATE"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RECERTIFICATION MANAGEMENT
# ============================================================================

@router.post("/recertification/status", response_model=RecertificationStatusResponse)
async def check_recertification_status(
    request: RecertificationCheckRequest,
    db: Session = Depends(get_db)
):
    """
    Check recertification deadline and status
    """
    try:
        member = db.query(Member).filter(Member.umid == request.umid).first()
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        eligibility = db.query(MemberEligibility).filter(
            MemberEligibility.member_id == member.id
        ).order_by(MemberEligibility.created_at.desc()).first()

        if not eligibility:
            raise HTTPException(status_code=404, detail="No eligibility record found")

        determiner = EligibilityDetermination(db, member)
        days_until_recert = determiner.get_days_until_recertification(eligibility)

        # Determine status
        if days_until_recert is None:
            recert_status = "UNKNOWN"
        elif days_until_recert > 60:
            recert_status = "ON_TRACK"
        elif 30 <= days_until_recert <= 60:
            recert_status = "ALERT_60_DAYS"
        elif 0 < days_until_recert < 30:
            recert_status = "ALERT_URGENT"
        else:
            recert_status = "OVERDUE"

        return RecertificationStatusResponse(
            umid=request.umid,
            recertification_date=eligibility.recertification_date,
            days_until_due=days_until_recert,
            status=recert_status,
            next_action=f"Upload recertification documents by {eligibility.recertification_date}",
            upload_documents_here="/api/card1/documents/upload"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DOCUMENT MANAGEMENT
# ============================================================================

@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    request: DocumentUploadRequest,
    db: Session = Depends(get_db)
):
    """
    Upload member document (ID, pay stub, address proof, etc.)
    """
    try:
        member = db.query(Member).filter(Member.umid == request.umid).first()
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        # In production: decode base64, validate image, extract metadata with OCR
        # For now: placeholder
        legibility_score = 0.95  # Simulated

        document_id = f"DOC-{member.umid}-{datetime.utcnow().timestamp()}"

        return DocumentUploadResponse(
            document_id=document_id,
            document_type=request.document_type,
            upload_status="VERIFIED",
            legibility_score=legibility_score,
            verification_message="Document received and verified",
            next_step="Awaiting caseworker review"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# INCOME REPORTING
# ============================================================================

@router.post("/income/report", response_model=IncomeChangeResponse)
async def report_income_change(
    request: IncomeReportRequest,
    db: Session = Depends(get_db)
):
    """
    Report income change and check impact on eligibility
    """
    try:
        member = db.query(Member).filter(Member.umid == request.umid).first()
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")

        eligibility = db.query(MemberEligibility).filter(
            MemberEligibility.member_id == member.id
        ).order_by(MemberEligibility.created_at.desc()).first()

        if not eligibility:
            raise HTTPException(status_code=404, detail="No eligibility record found")

        determiner = EligibilityDetermination(db, member)
        impact = determiner.check_income_impact(request.new_income, eligibility)

        return IncomeChangeResponse(
            umid=request.umid,
            current_income=impact["current_income"],
            new_income=request.new_income,
            income_limit=eligibility.income_limit,
            impact_on_coverage=impact["impact"],
            member_message=impact["member_message"],
            recommendation=impact["recommendation"],
            confidence_score=impact["confidence"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WRAPPER FUNCTIONS FOR CHAT INTEGRATION
# ============================================================================
# These wrapper functions map chat.py's expected function names to actual implementations

async def check_eligibility(member_id: str):
    """Wrapper for check_eligibility_member_view - used by chat.py"""
    request = EligibilityCheckRequest(umid=member_id, check_type="current")
    return await check_eligibility_member_view(request)


async def check_recertification(member_id: str):
    """Wrapper for check_recertification_status - used by chat.py"""
    request = RecertificationCheckRequest(umid=member_id)
    return await check_recertification_status(request)
