"""
SOURCE MANAGEMENT API (Phase 1.4)
Strike unreliable sources, add new reliable sources, manage River Path dynamically

Used by Cards 4 (USHI) and Card 5 (UBADA) to improve system over time
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
import json

from database import get_db
from models import (
    SourceRegistry, SourceAction, SourceComparison,
    SourceReliabilityLevel
)
from governance import log_governance_action

router = APIRouter(prefix="/api/sources", tags=["Source Management"])

# ============================================================================
# SOURCE REGISTRY (LIST, VIEW, QUERY)
# ============================================================================

@router.get("/registry")
async def list_active_sources(
    status: str = Query("active", description="active, struck, all"),
    db: Session = Depends(get_db)
):
    """List all registered data sources (active, struck, or all)"""
    try:
        query = db.query(SourceRegistry)

        if status == "active":
            query = query.filter(SourceRegistry.active == True, SourceRegistry.struck == False)
        elif status == "struck":
            query = query.filter(SourceRegistry.struck == True)
        # else: all (no filter)

        sources = query.order_by(SourceRegistry.quality_score.desc()).all()

        return {
            "total": len(sources),
            "sources": [
                {
                    "id": source.id,
                    "name": source.source_name,
                    "type": source.source_type,
                    "active": source.active,
                    "struck": source.struck,
                    "quality_score": source.quality_score,
                    "reliability_level": source.reliability_level.value if source.reliability_level else "UNKNOWN",
                    "success_rate": source.success_rate,
                    "last_queried": source.last_queried.isoformat() if source.last_queried else None,
                    "query_count": source.query_count,
                    "average_latency_seconds": source.average_latency_seconds
                }
                for source in sources
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/registry/{source_id}")
async def get_source_details(
    source_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific source"""
    source = db.query(SourceRegistry).filter(SourceRegistry.id == source_id).first()

    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    return {
        "id": source.id,
        "name": source.source_name,
        "type": source.source_type,
        "url": source.source_url,
        "active": source.active,
        "struck": source.struck,
        "strike_reason": source.strike_reason,
        "strike_effective_date": source.strike_effective_date.isoformat() if source.strike_effective_date else None,
        "quality_score": source.quality_score,
        "reliability_level": source.reliability_level.value if source.reliability_level else "UNKNOWN",
        "success_rate": source.success_rate,
        "query_count": source.query_count,
        "last_queried": source.last_queried.isoformat() if source.last_queried else None,
        "average_latency_seconds": source.average_latency_seconds,
        "contact_email": source.contact_email,
        "sla_notes": source.sla_notes,
        "created_at": source.created_at.isoformat(),
        "updated_at": source.updated_at.isoformat()
    }


# ============================================================================
# STRIKE SOURCE (BLACKLIST AS UNRELIABLE)
# ============================================================================

@router.post("/strike")
async def strike_source(
    source_id: str,
    reason: str,  # Why is this source unreliable?
    evidence: List[str],  # Evidence of unreliability (URLs, incident reports, etc.)
    initiated_by: str,  # User ID
    expected_impact: Optional[str] = None,  # What happens when we strike this
    restoration_date: Optional[str] = None,  # When might it be restored?
    db: Session = Depends(get_db)
):
    """
    Strike (blacklist) a source as unreliable

    Once struck:
    - River Path algorithm will skip this source
    - Future queries won't use this source
    - All source selections are logged + justified
    """
    try:
        source = db.query(SourceRegistry).filter(SourceRegistry.id == source_id).first()

        if not source:
            raise HTTPException(status_code=404, detail="Source not found")

        if source.struck:
            raise HTTPException(status_code=400, detail="Source is already struck")

        # Create strike action
        action = SourceAction(
            source_id=source_id,
            source_name=source.source_name,
            action="STRIKE",
            initiated_by=initiated_by,
            reason=reason,
            evidence=json.dumps(evidence),
            expected_impact=expected_impact,
            effective_date=datetime.utcnow(),
            restoration_date=restoration_date
        )

        # Mark source as struck
        source.struck = True
        source.strike_reason = reason
        source.strike_effective_date = datetime.utcnow()

        db.add(action)
        db.commit()

        # Log to governance audit trail
        await log_governance_action(
            action="STRIKE_SOURCE",
            action_type="source_management",
            actor_id=initiated_by,
            domain="source_management",
            domain_id=source_id,
            change_summary=f"Struck source: {source.source_name}",
            justification=reason,
            evidence=evidence,
            db=db
        )

        return {
            "action_id": action.id,
            "source_id": source_id,
            "source_name": source.source_name,
            "status": "STRUCK",
            "reason": reason,
            "effective_date": action.effective_date.isoformat(),
            "message": f"Source '{source.source_name}' has been struck as unreliable. Future queries will skip this source."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ADD NEW SOURCE
# ============================================================================

@router.post("/add")
async def add_new_source(
    source_name: str,
    source_type: str,  # state, federal, mco, external, internal
    source_url: str,
    quality_score: float,  # Initial assessment (0.0-1.0)
    reason: str,  # Why is this source reliable?
    evidence: List[str],  # Evidence of reliability
    initiated_by: str,  # User ID
    testing_plan: Optional[str] = None,  # How will we validate this source?
    sla_notes: Optional[str] = None,
    contact_email: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Propose a new reliable source for River Path

    New sources:
    1. Are added to registry
    2. Require testing before production use
    3. Get gradual expansion in River Path (2-week test, then monitoring)
    """
    try:
        # Check if source already exists
        existing = db.query(SourceRegistry).filter(
            SourceRegistry.source_name == source_name
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Source already registered")

        # Create new source
        new_source = SourceRegistry(
            source_name=source_name,
            source_type=source_type,
            source_url=source_url,
            quality_score=quality_score,
            reliability_level=self._score_to_level(quality_score),
            active=False,  # Not active until testing complete
            sla_notes=sla_notes,
            contact_email=contact_email
        )

        # Create action
        action = SourceAction(
            source_id=new_source.id,
            source_name=source_name,
            action="ADD",
            initiated_by=initiated_by,
            reason=reason,
            evidence=json.dumps(evidence),
            expected_impact=testing_plan or "Testing in progress",
            effective_date=datetime.utcnow()
        )

        db.add(new_source)
        db.add(action)
        db.commit()

        # Log to governance audit trail
        await log_governance_action(
            action="ADD_SOURCE",
            action_type="source_management",
            actor_id=initiated_by,
            domain="source_management",
            domain_id=new_source.id,
            change_summary=f"Added new source: {source_name}",
            justification=reason,
            evidence=evidence,
            db=db
        )

        return {
            "action_id": action.id,
            "source_id": new_source.id,
            "source_name": source_name,
            "status": "TESTING",
            "quality_score": quality_score,
            "message": f"Source '{source_name}' added. Testing for 2 weeks before production use."
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SOURCE ACTION HISTORY (IMMUTABLE)
# ============================================================================

@router.get("/history/{source_id}")
async def get_source_action_history(
    source_id: str,
    db: Session = Depends(get_db)
):
    """Get immutable history of all source management decisions"""
    actions = db.query(SourceAction).filter(
        SourceAction.source_id == source_id
    ).order_by(SourceAction.initiated_at.desc()).all()

    return {
        "source_id": source_id,
        "total_actions": len(actions),
        "actions": [
            {
                "id": action.id,
                "action": action.action,
                "initiated_by": action.initiated_by,
                "initiated_at": action.initiated_at.isoformat(),
                "approved_by": action.approved_by,
                "approved_at": action.approved_at.isoformat() if action.approved_at else None,
                "reason": action.reason,
                "effective_date": action.effective_date.isoformat(),
                "restoration_date": action.restoration_date.isoformat() if action.restoration_date else None
            }
            for action in actions
        ]
    }


# ============================================================================
# SOURCE DISAGREEMENT TRACKING
# ============================================================================

@router.post("/disagreement")
async def log_source_disagreement(
    query_type: str,  # member_lookup, provider_lookup, eligibility_check
    source_1_id: str,
    source_1_result: dict,
    source_1_confidence: float,
    source_2_id: str,
    source_2_result: dict,
    source_2_confidence: float,
    domain: str,
    domain_id: str,
    disagreement_percentage: float,  # 0-100 (how much they differ)
    disagreement_type: str,  # timing_lag, definition_difference, data_error, genuine_change
    detected_by: str = "SYSTEM",
    db: Session = Depends(get_db)
):
    """
    Log when two sources disagree (for analysis + improvement)

    Examples:
    - eMedNY says provider "ACTIVE" but MCO says "RESTRICTED"
    - State DB says member "ELIGIBLE" but SSA says "INCOME_TOO_HIGH"
    """
    try:
        source_1 = db.query(SourceRegistry).filter(SourceRegistry.id == source_1_id).first()
        source_2 = db.query(SourceRegistry).filter(SourceRegistry.id == source_2_id).first()

        comparison = SourceComparison(
            query_type=query_type,
            query_domain=domain,
            query_domain_id=domain_id,
            source_1_id=source_1_id,
            source_1_name=source_1.source_name if source_1 else "UNKNOWN",
            source_1_result=json.dumps(source_1_result),
            source_1_confidence=source_1_confidence,
            source_2_id=source_2_id,
            source_2_name=source_2.source_name if source_2 else "UNKNOWN",
            source_2_result=json.dumps(source_2_result),
            source_2_confidence=source_2_confidence,
            disagreement_detected=True,
            disagreement_percentage=disagreement_percentage,
            disagreement_type=disagreement_type,
            detected_at=datetime.utcnow()
        )

        db.add(comparison)
        db.commit()

        return {
            "comparison_id": comparison.id,
            "sources": [
                source_1.source_name if source_1 else "UNKNOWN",
                source_2.source_name if source_2 else "UNKNOWN"
            ],
            "disagreement_percentage": disagreement_percentage,
            "disagreement_type": disagreement_type,
            "message": f"Source disagreement logged for investigation"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/disagreements")
async def list_source_disagreements(
    days_back: int = Query(30),
    disagreement_type: Optional[str] = None,
    limit: int = Query(100),
    db: Session = Depends(get_db)
):
    """List source disagreements for pattern analysis"""
    from datetime import timedelta

    cutoff = datetime.utcnow() - timedelta(days=days_back)
    query = db.query(SourceComparison).filter(
        SourceComparison.detected_at >= cutoff,
        SourceComparison.disagreement_detected == True
    )

    if disagreement_type:
        query = query.filter(SourceComparison.disagreement_type == disagreement_type)

    comparisons = query.order_by(SourceComparison.detected_at.desc()).limit(limit).all()

    return {
        "period_days": days_back,
        "total_disagreements": len(comparisons),
        "disagreements": [
            {
                "id": comp.id,
                "sources": [comp.source_1_name, comp.source_2_name],
                "query_type": comp.query_type,
                "disagreement_type": comp.disagreement_type,
                "disagreement_percentage": comp.disagreement_percentage,
                "detected_at": comp.detected_at.isoformat()
            }
            for comp in comparisons
        ]
    }


# ============================================================================
# INTERNAL HELPERS
# ============================================================================

def _score_to_level(score: float) -> SourceReliabilityLevel:
    """Convert numeric score to reliability level"""
    if score >= 0.95:
        return SourceReliabilityLevel.AUTHORITATIVE
    elif score >= 0.85:
        return SourceReliabilityLevel.HIGH
    elif score >= 0.70:
        return SourceReliabilityLevel.MEDIUM
    elif score >= 0.50:
        return SourceReliabilityLevel.LOW
    else:
        return SourceReliabilityLevel.UNRELIABLE
