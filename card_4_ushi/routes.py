"""
Card 4 (USHI) - Government Stakeholder API Routes
Expose 5 Claude tools for government operations with REAL data from public repositories
"""

from fastapi import APIRouter, HTTPException, Depends, Body, Request
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
import json

from database import get_db
from .query_engine import (
    query_aggregate_metrics,
    detect_fraud_signals,
    assess_data_quality,
    view_governance_log,
    flag_data_issue
)

router = APIRouter(prefix="/api/card4", tags=["Card 4 - USHI (Government)"])

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
# TOOL 1: QUERY AGGREGATE METRICS
# ============================================================================

@router.post("/metrics")
async def get_metrics(
    metric_type: str = Body(...),  # enrollment_rate, denial_rate, processing_time, approval_rate
    date_range_days: int = Body(30),
    filter_by: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    public_data_schema: Optional[Dict] = Depends(get_public_data_schema)
):
    """
    Query system-wide aggregate metrics from REAL public repositories (HIPAA-compliant)

    Returns only aggregate counts/percentages, never individual records
    """
    try:
        result = await query_aggregate_metrics(
            metric_type=metric_type,
            date_range_days=date_range_days,
            filter_by=filter_by,
            db=db,
            public_data_schema=public_data_schema
        )

        # query_aggregate_metrics already returns {status, data, confidence_score, crawler_report, caveat}
        # Return it directly — don't double-wrap
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TOOL 2: DETECT inauthenticity SIGNALS
# ============================================================================

@router.post("/inauthenticity-signals")
async def detect_signals(
    entity_type: str = Body("provider"),  # provider, member, claim_pattern
    threshold_sigma: float = Body(2.0),
    db: Session = Depends(get_db),
    public_data_schema: Optional[Dict] = Depends(get_public_data_schema)
):
    """
    Detect statistical anomalies (inauthenticity signals) from REAL data sources

    Returns outliers + patterns (aggregate, HIPAA-compliant)
    Recommends escalation to Card 5 (UBADA) for detailed investigation
    """
    try:
        result = await detect_fraud_signals(
            entity_type=entity_type,
            threshold_sigma=threshold_sigma,
            db=db,
            public_data_schema=public_data_schema
        )

        return {
            "status": "success",
            "data": result,
            "confidence_score": result.get("confidence_score", 0.0),
            "recommendation": "Escalate to Card 5 (UBADA) for detailed investigation"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TOOL 3: ASSESS DATA QUALITY
# ============================================================================

@router.post("/data-quality")
async def check_data_quality(
    domain: str = Body("enrollment"),  # enrollment, claims, provider_data
    db: Session = Depends(get_db),
    public_data_schema: Optional[Dict] = Depends(get_public_data_schema)
):
    """
    Assess cross-source data consistency from REAL public repositories

    Reports agreement rates between sources (eMedNY vs MCO vs SSA, etc.)
    Identifies conflict types and recommendations
    """
    try:
        result = await assess_data_quality(
            domain=domain,
            db=db,
            public_data_schema=public_data_schema
        )

        return {
            "status": "success",
            "data": result,
            "quality_score": result.get("overall_quality_score") or result.get("completeness_score", 0.0)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TOOL 4: VIEW GOVERNANCE LOG
# ============================================================================

@router.get("/governance-log")
async def get_governance_log(
    filter_by: Optional[str] = None,
    days_back: int = 30,
    limit: int = 50,
    db: Session = Depends(get_db),
    public_data_schema: Optional[Dict] = Depends(get_public_data_schema)
):
    """
    Access immutable governance audit trail

    Returns WHO/WHAT/WHEN/WHY for all governance actions
    Immutable record for compliance
    """
    try:
        result = await view_governance_log(
            filter_by=filter_by,
            days_back=days_back,
            limit=limit,
            db=db,
            public_data_schema=public_data_schema
        )

        return {
            "status": "success",
            "data": result,
            "note": "Immutable audit trail - every action is logged with justification"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# TOOL 5: FLAG DATA ISSUE
# ============================================================================

@router.post("/flag-issue")
async def create_flag(
    issue_type: str = Body(...),  # data_quality, fraud_suspicion, compliance_gap, system_error
    domain: str = Body(...),  # claims, enrollment, provider_data
    title: str = Body(...),
    description: str = Body(...),
    justification: str = Body(...),
    evidence: List[str] = Body(...),
    flagged_by: str = Body(...),
    db: Session = Depends(get_db),
    public_data_schema: Optional[Dict] = Depends(get_public_data_schema)
):
    """
    Create governance flag (create governance action)

    Creates immutable record for audit trail with reference to real data sources
    """
    try:
        result = await flag_data_issue(
            issue_type=issue_type,
            domain=domain,
            title=title,
            description=description,
            justification=justification,
            evidence=evidence,
            flagged_by=flagged_by,
            db=db,
            public_data_schema=public_data_schema
        )

        return {
            "status": "success",
            "data": result,
            "flag_id": result.get("flag_id"),
            "note": "Flag created and logged to immutable audit trail"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Card 4 health check"""
    return {
        "status": "healthy",
        "card": "4 (USHI)",
        "tools": 5,
        "tools_available": [
            "query_aggregate_metrics",
            "detect_fraud_signals",
            "assess_data_quality",
            "view_governance_log",
            "flag_data_issue"
        ]
    }


# ============================================================================
# ON-DEMAND CRAWL ENDPOINT (triggered by Elaborate button)
# ============================================================================

@router.post("/crawl")
async def crawl_and_refresh(request: Request):
    """
    Trigger on-demand crawl of all public repositories.
    Called by the Elaborate button — crawls, stores schema, returns summary.
    """
    try:
        from data_crawler import discover_public_data
        import json

        schema = await discover_public_data()
        request.app.state.public_data_schema = schema

        # Persist to disk
        with open("public_data_schema.json", "w") as f:
            json.dump(schema, f, indent=2)

        return {
            "status": "success",
            "urls_visited": schema.get("total_urls_visited", 0),
            "sources_discovered": schema.get("total_data_sources_discovered", 0),
            "summary": schema.get("summary", {}),
            "errors": schema.get("errors", [])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crawl failed: {str(e)}")
