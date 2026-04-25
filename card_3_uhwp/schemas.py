"""
Pydantic schemas for Card 3 (UHWP) API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class ProgramsQueryRequest(BaseModel):
    """Request to get programs/plans by state"""
    state: Optional[str] = Field(None, description="State abbreviation (e.g., 'NY')")
    requested_count: Optional[int] = Field(5, description="Number of plans to return")


class EligibleProgramsRequest(BaseModel):
    """Request to get programs eligible for a specific member"""
    umid: Optional[str] = Field(None, description="Unified Member ID")
    state: Optional[str] = Field(None, description="State abbreviation")


class PlanComparisonRequest(BaseModel):
    """Request to compare selected plans"""
    plans: List[str] = Field(..., description="List of plan names to compare")
    state: str = Field(..., description="State abbreviation")


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class ProgramBasic(BaseModel):
    """Basic program/plan information"""
    name: str
    type: str  # HMO, PPO, POS, HDHP, etc.
    network: str  # Managed, Open Network, Tiered, etc.
    state: Optional[str]
    enrollment_count: Optional[int]
    network_adequacy_score: Optional[float]  # 0-100, used for Clarity light


class ProgramsQueryResponse(BaseModel):
    """Response with programs by state"""
    state: Optional[str]
    programs: List[ProgramBasic]
    count: int
    clarity: str  # "green" (adequate network), "yellow" (concerns), "red" (critical)
    network_adequacy_score: Optional[float]  # Overall score for this state
    sources: List[Dict]  # Source citations
    timestamp: datetime


class EligibleProgramsResponse(BaseModel):
    """Response with eligible programs for a member"""
    umid: Optional[str]
    eligible_programs: List[ProgramBasic]
    count: int
    clarity: str  # Traffic light status
    member_status: str  # "ELIGIBLE", "NOT_ELIGIBLE", "PENDING"
    message: str
    sources: List[Dict]
    timestamp: datetime


class PlanComparisonDetail(BaseModel):
    """Detailed comparison of a single plan"""
    name: str
    type: str
    network: str
    premium_cost: Optional[float]
    copay: Optional[float]
    coinsurance: Optional[float]
    deductible: Optional[float]
    out_of_pocket_max: Optional[float]
    specialty_network: Optional[bool]
    drug_formulary: Optional[bool]
    ratings: Optional[Dict]  # Quality ratings from CMS


class PlanComparisonResponse(BaseModel):
    """Response with plan comparison"""
    state: str
    plans_compared: List[PlanComparisonDetail]
    clarity: str  # Network adequacy light
    best_for_affordability: Optional[str]  # Plan name
    best_for_coverage: Optional[str]
    best_for_specialty: Optional[str]
    sources: List[Dict]
    timestamp: datetime


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    database: str
    timestamp: datetime
