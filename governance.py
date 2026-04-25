"""
GOVERNANCE & AUDIT TRAIL API (Phase 1.3)
Immutable append-only governance logging + retrieval endpoints

Used by Cards 4 (USHI) and Card 5 (UBADA) for audit compliance
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import json

from database import get_db
from models import (
    GovernanceFlag, GovernanceApproval, AuditLogEntry,
    GovernanceActionType, GovernanceStatus
)

router = APIRouter(prefix="/api/governance", tags=["Governance & Audit Trail"])

# ============================================================================
# GOVERNANCE FLAGS (CREATE, RETRIEVE, APPROVE)
# ============================================================================

@router.post("/flag")
async def create_governance_flag(
    action_type: str,  # DATA_QUALITY_ISSUE, FRAUD_SUSPICION, COMPLIANCE_GAP, etc.
    domain: str,  # claims, enrollment, provider_data, member_data
    domain_id: str,  # Specific record being flagged (claim_id, umid, upid)
    title: str,
    description: str,
    justification: str,
    flagged_by: str,  # User ID of who's flagging
    evidence_links: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """
    Create a governance flag (governance action)

    Examples:
    - "DATA_QUALITY_ISSUE" on member enrollment (source conflict)
    - "FRAUD_SUSPICION" on provider billing pattern
    - "COMPLIANCE_GAP" on system performance
    """
    try:
        flag = GovernanceFlag(
            action_type=action_type,
            domain=domain,
            domain_id=domain_id,
            title=title,
            description=description,
            justification=justification,
            flagged_by=flagged_by,
            evidence_links=json.dumps(evidence_links or []),
            status=GovernanceStatus.FLAGGED
        )

        db.add(flag)
        db.commit()
        db.refresh(flag)

        # Log to audit trail
        await log_governance_action(
            action="FLAG",
            action_type="governance_flag",
            actor_id=flagged_by,
            domain="governance",
            domain_id=flag.id,
            change_summary=f"Created flag: {title}",
            justification=justification,
            db=db
        )

        return {
            "flag_id": flag.id,
            "status": flag.status.value,
            "created_at": flag.created_at.isoformat(),
            "message": f"Flag created: {title}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/flag/{flag_id}")
async def get_governance_flag(
    flag_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve governance flag details"""
    flag = db.query(GovernanceFlag).filter(GovernanceFlag.id == flag_id).first()

    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found")

    return {
        "id": flag.id,
        "action_type": flag.action_type.value,
        "status": flag.status.value,
        "domain": flag.domain,
        "domain_id": flag.domain_id,
        "title": flag.title,
        "description": flag.description,
        "justification": flag.justification,
        "flagged_by": flag.flagged_by,
        "flagged_at": flag.flagged_at.isoformat(),
        "assigned_to": flag.assigned_to,
        "approved_by": flag.approved_by,
        "evidence_links": json.loads(flag.evidence_links) if flag.evidence_links else []
    }


@router.post("/flag/{flag_id}/approve")
async def approve_governance_flag(
    flag_id: str,
    approved_by: str,  # User ID of approver
    approval_notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Approve a governance flag (governance action)"""
    flag = db.query(GovernanceFlag).filter(GovernanceFlag.id == flag_id).first()

    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found")

    # Create approval record
    approval = GovernanceApproval(
        flag_id=flag_id,
        approved_by=approved_by,
        is_approved=True,
        approval_notes=approval_notes
    )

    # Update flag
    flag.status = GovernanceStatus.APPROVED
    flag.approved_by = approved_by
    flag.approved_at = datetime.utcnow()

    db.add(approval)
    db.commit()

    # Log to audit trail
    await log_governance_action(
        action="APPROVE_FLAG",
        action_type="governance_approval",
        actor_id=approved_by,
        domain="governance",
        domain_id=flag_id,
        change_summary=f"Approved flag: {flag.title}",
        justification=approval_notes or "Approved",
        db=db
    )

    return {
        "flag_id": flag_id,
        "status": flag.status.value,
        "approved_at": flag.approved_at.isoformat(),
        "message": f"Flag approved"
    }


# ============================================================================
# AUDIT LOG RETRIEVAL (IMMUTABLE)
# ============================================================================

@router.get("/log/search")
async def search_audit_log(
    action: Optional[str] = Query(None, description="Filter by action"),
    actor_id: Optional[str] = Query(None, description="Filter by who did it"),
    domain: Optional[str] = Query(None, description="Filter by domain (governance, source_management, investigation)"),
    domain_id: Optional[str] = Query(None, description="Filter by what record"),
    days_back: int = Query(30, description="How many days back to search"),
    limit: int = Query(100, description="Max results"),
    offset: int = Query(0, description="Pagination offset"),
    db: Session = Depends(get_db)
):
    """
    Search immutable governance audit log

    Returns WHO/WHAT/WHEN/WHY/APPROVED for every governance action
    """
    try:
        # Build query
        query = db.query(AuditLogEntry)

        # Time filter
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        query = query.filter(AuditLogEntry.timestamp >= cutoff_date)

        # Apply filters
        if action:
            query = query.filter(AuditLogEntry.action == action)
        if actor_id:
            query = query.filter(AuditLogEntry.actor_id == actor_id)
        if domain:
            query = query.filter(AuditLogEntry.domain == domain)
        if domain_id:
            query = query.filter(AuditLogEntry.domain_id == domain_id)

        # Count total
        total = query.count()

        # Pagination
        entries = query.order_by(AuditLogEntry.timestamp.desc()).offset(offset).limit(limit).all()

        return {
            "total": total,
            "returned": len(entries),
            "offset": offset,
            "limit": limit,
            "entries": [
                {
                    "id": entry.id,
                    "action": entry.action,
                    "actor_id": entry.actor_id,
                    "actor_role": entry.actor_role,
                    "domain": entry.domain,
                    "domain_id": entry.domain_id,
                    "change_summary": entry.change_summary,
                    "justification": entry.justification,
                    "timestamp": entry.timestamp.isoformat()
                }
                for entry in entries
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/log/{entry_id}")
async def get_audit_log_entry(
    entry_id: str,
    db: Session = Depends(get_db)
):
    """Get full immutable audit log entry (with all details)"""
    entry = db.query(AuditLogEntry).filter(AuditLogEntry.id == entry_id).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Audit log entry not found")

    return {
        "id": entry.id,
        "action": entry.action,
        "action_type": entry.action_type,
        "actor_id": entry.actor_id,
        "actor_role": entry.actor_role,
        "domain": entry.domain,
        "domain_id": entry.domain_id,
        "change_summary": entry.change_summary,
        "change_details": json.loads(entry.change_details) if entry.change_details else None,
        "justification": entry.justification,
        "evidence": json.loads(entry.evidence) if entry.evidence else [],
        "timestamp": entry.timestamp.isoformat(),
        "note": "This entry is immutable and cannot be modified"
    }


@router.get("/log/export")
async def export_audit_log(
    days_back: int = Query(365, description="How many days to export"),
    format: str = Query("json", description="Export format: json or csv"),
    db: Session = Depends(get_db)
):
    """
    Export governance audit log in HHS-compliant format

    For compliance reporting and archival
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days_back)
    entries = db.query(AuditLogEntry).filter(
        AuditLogEntry.timestamp >= cutoff_date
    ).order_by(AuditLogEntry.timestamp.asc()).all()

    if format == "json":
        return {
            "export_date": datetime.utcnow().isoformat(),
            "period_days": days_back,
            "total_entries": len(entries),
            "entries": [
                {
                    "id": entry.id,
                    "action": entry.action,
                    "actor_id": entry.actor_id,
                    "actor_role": entry.actor_role,
                    "domain": entry.domain,
                    "domain_id": entry.domain_id,
                    "change_summary": entry.change_summary,
                    "justification": entry.justification,
                    "timestamp": entry.timestamp.isoformat()
                }
                for entry in entries
            ]
        }
    else:
        # CSV export would be handled by frontend or separate export service
        raise HTTPException(status_code=501, detail="CSV export not yet implemented")


# ============================================================================
# INTERNAL: Log governance action to audit trail
# ============================================================================

async def log_governance_action(
    action: str,
    action_type: str,
    actor_id: str,
    domain: str,
    domain_id: str,
    change_summary: str,
    justification: str,
    evidence: Optional[List[str]] = None,
    change_details: Optional[dict] = None,
    actor_role: str = "SYSTEM",
    db: Session = Depends(get_db)
):
    """Internal: Create immutable audit log entry"""
    entry = AuditLogEntry(
        action=action,
        action_type=action_type,
        actor_id=actor_id,
        actor_role=actor_role,
        domain=domain,
        domain_id=domain_id,
        change_summary=change_summary,
        change_details=json.dumps(change_details or {}),
        justification=justification,
        evidence=json.dumps(evidence or []),
        timestamp=datetime.utcnow()
    )

    db.add(entry)
    db.commit()

    return entry
