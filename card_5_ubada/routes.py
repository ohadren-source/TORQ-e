"""
Card 5 (UBADA) - Data Analyst & Fraud Investigation API Routes
Expose 5 Claude tools for investigation and data correction
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from typing import Optional, List
import json

from database import get_db
from .query_engine import (
    explore_claims_data,
    compute_outlier_scores,
    navigate_relationship_graph,
    create_investigation_project,
    request_data_correction
)

router = APIRouter(prefix="/api/card5", tags=["Card 5 - UBADA (Data Analyst)"])

# ============================================================================
# TOOL 1: EXPLORE CLAIMS DATA
# ============================================================================

@router.post("/explore-claims")
async def explore_claims(
    filter_by: Optional[dict] = Body(None),
    aggregation: Optional[str] = Body(None),
    limit: int = Body(1000),
    db: Session = Depends(get_db)
):
    """
    Interactive query interface for claims data with full access.

    UBADA has full data access (names, SSNs, NPIs).
    Every query creates immutable audit record.
    """
    try:
        result = await explore_claims_data(
            filter_by=filter_by,
            aggregation=aggregation,
            limit=limit,
            db=db
        )

        return {
            "status": "success",
            "data": result,
            "query_logged": True,
            "audit_note": "Full data access query logged to immutable audit trail"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TOOL 2: COMPUTE OUTLIER SCORES
# ============================================================================

@router.post("/outlier-detection")
async def detect_outliers(
    entity_type: str = Body("provider"),
    metric: str = Body("billing_amount"),
    threshold_sigma: float = Body(2.0),
    db: Session = Depends(get_db)
):
    """
    Statistical anomaly detection for fraud signal identification.

    Returns outliers with Z-scores, risk levels, and confidence scores.
    Focus: Evidence quality for investigation recommendations.
    """
    try:
        result = await compute_outlier_scores(
            entity_type=entity_type,
            metric=metric,
            threshold_sigma=threshold_sigma,
            db=db
        )

        return {
            "status": "success",
            "data": result,
            "confidence_score": result.get("confidence_score", 0.0),
            "outliers_found": result.get("outliers_detected", 0)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TOOL 3: NAVIGATE RELATIONSHIP GRAPH
# ============================================================================

@router.post("/network-explorer")
async def explore_network(
    focus_entity: str = Body(...),
    relationship_type: str = Body("all"),
    depth: int = Body(1),
    db: Session = Depends(get_db)
):
    """
    Explore provider/member networks for pattern analysis.

    Identify co-billing arrangements, referral patterns, facility relationships.
    Returns network topology and unusual pattern flags.
    """
    try:
        result = await navigate_relationship_graph(
            focus_entity=focus_entity,
            relationship_type=relationship_type,
            depth=depth,
            db=db
        )

        return {
            "status": "success",
            "data": result,
            "connections_found": len(result.get("direct_connections", [])),
            "patterns_detected": len(result.get("unusual_patterns", []))
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TOOL 4: CREATE INVESTIGATION PROJECT
# ============================================================================

@router.post("/investigation/create")
async def create_investigation(
    title: str = Body(...),
    investigation_type: str = Body(...),
    lead_analyst: str = Body(...),
    team_members: List[str] = Body(...),
    initial_findings: str = Body(...),
    severity: str = Body("MEDIUM"),
    db: Session = Depends(get_db)
):
    """
    Create formal investigation project with team workspace.

    Every comment, finding, decision logged to immutable audit trail.
    Includes workflow tracking (OPEN → INVESTIGATING → RESOLVED/CLOSED).
    """
    try:
        result = await create_investigation_project(
            title=title,
            investigation_type=investigation_type,
            lead_analyst=lead_analyst,
            team_members=team_members,
            initial_findings=initial_findings,
            severity=severity,
            db=db
        )

        return {
            "status": "success",
            "data": result,
            "case_number": result.get("case_number"),
            "workspace_ready": True,
            "audit_trail_enabled": True
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TOOL 5: REQUEST DATA CORRECTION
# ============================================================================

@router.post("/data-correction/request")
async def request_correction(
    domain: str = Body(...),
    entity_id: str = Body(...),
    field_name: str = Body(...),
    current_value: str = Body(...),
    proposed_value: str = Body(...),
    change_reason: str = Body(...),
    evidence: List[str] = Body(...),
    proposed_by: str = Body(...),
    db: Session = Depends(get_db)
):
    """
    Request data correction with full audit trail.

    Workflow: PROPOSED → REVIEWED → APPROVED → APPLIED → LOGGED.
    Once approved, creates immutable record of change with original value preserved.
    """
    try:
        result = await request_data_correction(
            domain=domain,
            entity_id=entity_id,
            field_name=field_name,
            current_value=current_value,
            proposed_value=proposed_value,
            change_reason=change_reason,
            evidence=evidence,
            proposed_by=proposed_by,
            db=db
        )

        return {
            "status": "success",
            "data": result,
            "correction_id": result.get("correction_id"),
            "workflow_status": "PROPOSED",
            "note": "Awaiting approval review"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Card 5 health check"""
    return {
        "status": "healthy",
        "card": "5 (UBADA)",
        "tools": 5,
        "tools_available": [
            "explore_claims_data",
            "compute_outlier_scores",
            "navigate_relationship_graph",
            "create_investigation_project",
            "request_data_correction"
        ]
    }
