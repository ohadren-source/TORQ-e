"""
Card 3 (UHWP) API Routes: Plan Network Management System
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List

from database import get_db
from .schemas import (
    ProgramsQueryRequest, ProgramsQueryResponse, ProgramBasic,
    EligibleProgramsRequest, EligibleProgramsResponse,
    PlanComparisonRequest, PlanComparisonResponse, PlanComparisonDetail,
    HealthCheckResponse
)

router = APIRouter(prefix="/api/card3", tags=["Card 3 - Plan Network Management"])

# ============================================================================
# SEED DATA: Available Plans (In production, this would come from database)
# ============================================================================

PLANS_BY_STATE = {
    "NY": [
        {"name": "Empire BlueCross BlueShield", "type": "HMO", "network": "Managed", "state": "NY", "enrollment": 450000, "adequacy": 92},
        {"name": "UnitedHealthcare Community", "type": "PPO", "network": "Open Network", "state": "NY", "enrollment": 380000, "adequacy": 88},
        {"name": "Molina Healthcare", "type": "HMO", "network": "Managed", "state": "NY", "enrollment": 320000, "adequacy": 85},
        {"name": "Centene Local Plans", "type": "HMO", "network": "Managed", "state": "NY", "enrollment": 290000, "adequacy": 80},
        {"name": "Aetna Medicaid", "type": "Flex PPO", "network": "Tiered", "state": "NY", "enrollment": 210000, "adequacy": 78},
    ],
    "CA": [
        {"name": "Health Net Medicaid", "type": "HMO", "network": "Managed", "state": "CA", "enrollment": 520000, "adequacy": 91},
        {"name": "Covered California", "type": "PPO", "network": "Open Network", "state": "CA", "enrollment": 410000, "adequacy": 89},
        {"name": "LA Care Health Plan", "type": "HMO", "network": "Managed", "state": "CA", "enrollment": 380000, "adequacy": 87},
    ],
    "TX": [
        {"name": "BCBS Texas", "type": "HMO", "network": "Managed", "state": "TX", "enrollment": 480000, "adequacy": 86},
        {"name": "United Health Texas", "type": "PPO", "network": "Open Network", "state": "TX", "enrollment": 350000, "adequacy": 84},
        {"name": "Molina Texas", "type": "HMO", "network": "Managed", "state": "TX", "enrollment": 310000, "adequacy": 82},
    ]
}

# Default plans if state not found
DEFAULT_PLANS = [
    {"name": "Empire BlueCross BlueShield", "type": "HMO", "network": "Managed"},
    {"name": "UnitedHealthcare Community", "type": "PPO", "network": "Open Network"},
    {"name": "Molina Healthcare", "type": "HMO", "network": "Managed"},
]

# Source citations (fixed, director-controlled)
NETWORK_REGISTRY_SOURCE = {
    "name": "Network Registry",
    "url": "https://medicaid.state.ny.gov/network-registry",
    "timestamp": "2026-04-25T10:00:00Z",
    "type": "official"
}

FORMULARY_SOURCE = {
    "name": "Plan Formulary Database",
    "url": "https://medicaid.state.ny.gov/formulary",
    "timestamp": "2026-04-24T15:30:00Z",
    "type": "official"
}

CMS_RATINGS_SOURCE = {
    "name": "CMS Quality Ratings",
    "url": "https://www.cms.gov/Medicare/Prescription-Drug-Coverage/PrescriptionDrugCovContra/index.html",
    "timestamp": "2026-04-20T08:00:00Z",
    "type": "official"
}

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
# PROGRAMS/PLANS QUERY
# ============================================================================

@router.get("/programs", response_model=ProgramsQueryResponse)
async def get_programs(
    state: Optional[str] = Query(None, description="State abbreviation (e.g., 'NY')"),
    requested_count: int = Query(5, description="Number of plans to return"),
    db: Session = Depends(get_db)
):
    """
    Get available Medicaid plans by state.
    Returns top plans with network adequacy metrics.
    """
    try:
        # Get plans for state or default
        state_upper = state.upper() if state else "NY"
        available_plans = PLANS_BY_STATE.get(state_upper, DEFAULT_PLANS)

        # Slice to requested count
        selected_plans = available_plans[:requested_count]

        # Convert to response format
        programs = []
        total_adequacy = 0

        for plan in selected_plans:
            adequacy = plan.get("adequacy", 80)
            total_adequacy += adequacy

            programs.append(ProgramBasic(
                name=plan["name"],
                type=plan["type"],
                network=plan["network"],
                state=plan.get("state"),
                enrollment_count=plan.get("enrollment"),
                network_adequacy_score=adequacy
            ))

        # Calculate overall clarity light based on adequacy score
        avg_adequacy = total_adequacy / len(selected_plans) if selected_plans else 0
        if avg_adequacy >= 85:
            clarity = "green"
        elif avg_adequacy >= 75:
            clarity = "yellow"
        else:
            clarity = "red"

        return ProgramsQueryResponse(
            state=state_upper,
            programs=programs,
            count=len(selected_plans),
            clarity=clarity,
            network_adequacy_score=avg_adequacy,
            sources=[NETWORK_REGISTRY_SOURCE, FORMULARY_SOURCE],
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ELIGIBLE PROGRAMS QUERY
# ============================================================================

@router.get("/eligible-programs", response_model=EligibleProgramsResponse)
async def get_eligible_programs(
    umid: Optional[str] = Query(None, description="Unified Member ID"),
    state: Optional[str] = Query("NY", description="State abbreviation"),
    db: Session = Depends(get_db)
):
    """
    Get programs eligible for a specific member based on their enrollment state.
    Requires member to have completed Card 1 (Member Identity).
    """
    try:
        # Check if member exists (in production, would query database)
        if not umid:
            return EligibleProgramsResponse(
                umid=None,
                eligible_programs=[],
                count=0,
                clarity="yellow",
                member_status="PENDING",
                message="Please complete your profile in Card 1 (Member Identity) to see eligible plans",
                sources=[NETWORK_REGISTRY_SOURCE],
                timestamp=datetime.utcnow()
            )

        # Get eligible plans for this member's state
        state_upper = state.upper() if state else "NY"
        available_plans = PLANS_BY_STATE.get(state_upper, DEFAULT_PLANS)

        # Convert to response format
        eligible = []
        total_adequacy = 0

        for plan in available_plans:
            adequacy = plan.get("adequacy", 80)
            total_adequacy += adequacy

            eligible.append(ProgramBasic(
                name=plan["name"],
                type=plan["type"],
                network=plan["network"],
                state=plan.get("state"),
                enrollment_count=plan.get("enrollment"),
                network_adequacy_score=adequacy
            ))

        # Calculate clarity light
        avg_adequacy = total_adequacy / len(eligible) if eligible else 0
        if avg_adequacy >= 85:
            clarity = "green"
        elif avg_adequacy >= 75:
            clarity = "yellow"
        else:
            clarity = "red"

        return EligibleProgramsResponse(
            umid=umid,
            eligible_programs=eligible,
            count=len(eligible),
            clarity=clarity,
            member_status="ELIGIBLE",
            message=f"Found {len(eligible)} eligible plans in {state_upper}",
            sources=[NETWORK_REGISTRY_SOURCE, FORMULARY_SOURCE],
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PLAN COMPARISON
# ============================================================================

@router.post("/plan-comparison", response_model=PlanComparisonResponse)
async def compare_plans(
    request: PlanComparisonRequest,
    db: Session = Depends(get_db)
):
    """
    Compare selected plans side-by-side.
    Returns detailed comparison with network adequacy metrics.
    """
    try:
        state = request.state.upper()
        available_plans = PLANS_BY_STATE.get(state, DEFAULT_PLANS)

        # Find requested plans
        plans_to_compare = []
        total_adequacy = 0

        for requested_name in request.plans:
            for available_plan in available_plans:
                if available_plan["name"].lower() == requested_name.lower():
                    adequacy = available_plan.get("adequacy", 80)
                    total_adequacy += adequacy

                    plans_to_compare.append(PlanComparisonDetail(
                        name=available_plan["name"],
                        type=available_plan["type"],
                        network=available_plan["network"],
                        premium_cost=None,  # Would be in production DB
                        copay=None,
                        coinsurance=None,
                        deductible=None,
                        out_of_pocket_max=None,
                        specialty_network=True,
                        drug_formulary=True,
                        ratings={"quality_score": adequacy}
                    ))
                    break

        # Calculate clarity light
        avg_adequacy = total_adequacy / len(plans_to_compare) if plans_to_compare else 0
        if avg_adequacy >= 85:
            clarity = "green"
        elif avg_adequacy >= 75:
            clarity = "yellow"
        else:
            clarity = "red"

        # Determine best options
        best_affordability = plans_to_compare[0].name if plans_to_compare else None
        best_coverage = plans_to_compare[0].name if plans_to_compare else None

        return PlanComparisonResponse(
            state=state,
            plans_compared=plans_to_compare,
            clarity=clarity,
            best_for_affordability=best_affordability,
            best_for_coverage=best_coverage,
            best_for_specialty=None,
            sources=[NETWORK_REGISTRY_SOURCE, FORMULARY_SOURCE, CMS_RATINGS_SOURCE],
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
