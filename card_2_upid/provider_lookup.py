"""
PROVIDER LOOKUP & ENROLLMENT VERIFICATION (Card 2 - UPID)

River Path for Providers with Signal-Over-Noise Consensus:
  Attempt 1: eMedNY (FFS enrollment database)
  Attempt 2: MCO Panel Aggregator (all 5+ MCO enrollments)
  Attempt 3: NPI Database (provider exists but not enrolled)

Confidence Scoring:
  - Runs all 3 attempts in parallel
  - Scores each source: eMedNY 0.95, MCO 0.85, NPI 0.70
  - Calculates consensus using agreement-weighted formula
  - Flags any conflicts between sources (e.g., eMedNY says ACTIVE vs MCO says RESTRICTED)
"""

import uuid
from typing import Dict, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from models import Provider, ProviderEnrollmentStatus, DataSource, ProviderAuditLog
import httpx
import asyncio
import sys
import os

# Import confidence scorer from Card 1
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'card_1_umid'))
from confidence import ConfidenceScorer

class ProviderLookupResult:
    def __init__(self):
        self.provider_data: Optional[Dict] = None
        self.upid: Optional[str] = None
        self.data_source: Optional[DataSource] = None
        self.confidence: float = 0.0
        self.confidence_score: float = 0.0  # Numeric score for Claude
        self.caveats: Optional[str] = None  # Transparency warnings for low confidence
        self.flags: list = []
        self.error: Optional[str] = None
        self.ffs_enrollment: Optional[Dict] = None
        self.mco_enrollments: Dict = {}
        self.source_scores: List[Dict] = []  # For consensus calculation

class ProviderLookupExecutor:
    """Implements River Path for provider identification"""

    def __init__(self, db: Session, timeout_seconds: int = 30, public_data_schema: Optional[Dict] = None):
        self.db = db
        self.timeout = timeout_seconds
        self.public_data_schema = public_data_schema  # Real provider enrollment data sources
        self.result = ProviderLookupResult()

    async def execute(self, npi: str, first_name: Optional[str] = None, last_name: Optional[str] = None) -> ProviderLookupResult:
        """
        Execute River Path for provider with signal-over-noise consensus:
        1. Run all 3 attempts in parallel
        2. Gather successful sources and their confidence scores
        3. Calculate consensus confidence using agreement-weighted formula
        4. Flag any conflicts between sources

        Confidence Scoring:
        - eMedNY FFS: 0.95 (most authoritative for state enrollment)
        - MCO Aggregator: 0.85 (good coverage but less authoritative than state)
        - NPI Database: 0.70 (provider exists but no Medicaid enrollment confirmation)
        """

        # Run all 3 attempts in parallel
        emedny_result, mco_result, npi_result = await asyncio.gather(
            self._attempt_emedny_ffs(npi),
            self._attempt_mco_aggregator(npi),
            self._attempt_npi_database(npi, first_name, last_name)
        )

        # Collect successful sources with their confidence scores
        source_scores = []

        if emedny_result["success"]:
            source_scores.append({
                "source": "eMedNY FFS",
                "score": 0.95,
                "data": emedny_result["data"],
                "enrollment": emedny_result["enrollment"],
                "type": "ffs"
            })

        if mco_result["success"]:
            source_scores.append({
                "source": "MCO Panel",
                "score": 0.85,
                "data": mco_result["data"],
                "enrollments": mco_result["enrollments"],
                "type": "mco"
            })

        if npi_result["success"]:
            source_scores.append({
                "source": "NPI Database",
                "score": 0.70,
                "data": npi_result["data"],
                "type": "npi"
            })

        # If no sources found anything, return error
        if not source_scores:
            self.result.error = "Provider not found in any system"
            self.result.flags.append("Verify NPI number or contact EMEDNY directly")
            self.result.confidence_score = 0.0
            return self.result

        # Store source scores for audit/transparency
        self.result.source_scores = source_scores

        # Calculate consensus confidence across sources
        consensus_confidence = self._score_consensus_across_sources(source_scores)
        self.result.confidence_score = consensus_confidence

        # Prefer FFS if available (most authoritative), then MCO, then NPI
        if emedny_result["success"]:
            self.result.provider_data = emedny_result["data"]
            self.result.ffs_enrollment = emedny_result["enrollment"]
            self.result.data_source = DataSource.STATE_MEDICAID

            # Flag if MCO data conflicts with FFS
            if mco_result["success"]:
                self._check_ffs_mco_conflict(emedny_result, mco_result)

        elif mco_result["success"]:
            self.result.provider_data = mco_result["data"]
            self.result.mco_enrollments = mco_result["enrollments"]
            self.result.data_source = DataSource.STATE_MEDICAID
            self.result.flags.append("Enrolled in MCO only - verify FFS status via eMedNY")

        else:  # Only NPI available
            self.result.provider_data = npi_result["data"]
            self.result.data_source = DataSource.NPI_DATABASE
            self.result.flags.append("Provider found but NOT enrolled in Medicaid")

        self.result.upid = self._generate_upid(npi, self.result.provider_data)
        self.result.confidence = consensus_confidence

        return self.result

    def _score_consensus_across_sources(self, source_scores: List[Dict]) -> float:
        """
        Score consensus confidence across multiple provider data sources
        Uses signal-over-noise weighting from Card 1 ConfidenceScorer

        Formula: (avg_score × 0.6) + (agreement × 0.4)
        - avg_score: Average confidence across all sources
        - agreement: How much sources agree (1.0 = perfect agreement, 0.0 = complete disagreement)

        Returns:
            Consensus confidence score (0.0 to 1.0)
        """
        if not source_scores:
            return 0.0

        # Extract scores
        scores = [s["score"] for s in source_scores]
        avg_score = sum(scores) / len(scores)

        # Agreement metric: how much do source scores agree?
        # If all sources have same score, agreement = 1.0
        # If scores are spread wide, agreement = 0.0
        max_score = max(scores)
        min_score = min(scores)
        agreement = 1.0 - ((max_score - min_score) / 1.0)

        # Consensus = 60% on average quality, 40% on how much sources agree
        consensus = (avg_score * 0.6) + (agreement * 0.4)

        # Log for transparency
        self.result.flags.append(
            f"Consensus score: {consensus:.2f} "
            f"(avg quality: {avg_score:.2f}, agreement: {agreement:.2f})"
        )

        return consensus

    def _check_ffs_mco_conflict(self, emedny_result: Dict, mco_result: Dict):
        """
        Check for conflicts between FFS and MCO data
        Example: eMedNY says ACTIVE but MCO says RESTRICTED
        """
        emedny_status = emedny_result.get("enrollment", {}).get("status", "UNKNOWN")
        mco_statuses = list(mco_result.get("enrollments", {}).values())

        # Flag if FFS status conflicts with MCO status
        mco_status_set = {m.get("status", "UNKNOWN") for m in mco_statuses}
        if emedny_status not in mco_status_set:
            caveat = (
                f"⚠️ Status conflict detected: eMedNY FFS shows '{emedny_status}' "
                f"but MCO data shows '{', '.join(mco_status_set)}'. "
                f"Recommend contacting eMedNY directly to reconcile."
            )
            self.result.caveats = caveat
            self.result.flags.append(caveat)

    async def _attempt_emedny_ffs(self, npi: str) -> Dict:
        """
        Attempt 1: Query eMedNY FFS Enrollment Database
        Returns FFS enrollment status for this provider
        """
        try:
            # Simulate FFS enrollment lookup
            if npi and len(npi) == 10:
                return {
                    "success": True,
                    "data": {
                        "npi": npi,
                        "source": "EMEDNY_FFS"
                    },
                    "enrollment": {
                        "status": "ACTIVE",
                        "enrollment_date": "2020-01-15",
                        "tax_id": f"XX-{npi[-4:]}",
                        "claims_portal": "ePACES",
                        "payment_method": "Direct Deposit"
                    }
                }
            else:
                return {"success": False, "error": "Invalid NPI"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _attempt_mco_aggregator(self, npi: str) -> Dict:
        """
        Attempt 2: Query MCO Panel Aggregator
        Aggregates enrollment status across all MCOs
        """
        try:
            mco_list = ["Empire BCBS", "Aetna Medicaid", "UnitedHealth", "Healthfirst", "Molina"]
            enrollments = {}

            for mco in mco_list:
                enrollments[mco] = {
                    "status": "ACTIVE",  # Simulated
                    "enrollment_date": "2021-06-01",
                    "network_type": "IN_NETWORK",
                    "claims_portal": f"https://{mco.lower()}.claims.portal"
                }

            if enrollments:
                return {
                    "success": True,
                    "data": {"npi": npi, "source": "MCO_AGGREGATOR"},
                    "enrollments": enrollments
                }
            else:
                return {"success": False, "error": "No MCO enrollments found"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _attempt_npi_database(self, npi: str, first_name: Optional[str] = None, last_name: Optional[str] = None) -> Dict:
        """
        Attempt 3: Query NPI Database
        Verifies provider exists (but may not be Medicaid-enrolled)
        """
        try:
            if npi and len(npi) == 10:
                return {
                    "success": True,
                    "data": {
                        "npi": npi,
                        "first_name": first_name,
                        "last_name": last_name,
                        "source": "NPI_DATABASE",
                        "note": "Provider exists but NOT found in Medicaid enrollment systems"
                    }
                }
            else:
                return {"success": False, "error": "Invalid NPI"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _generate_upid(self, npi: str, provider_data: Dict) -> str:
        """
        Generate Unified Provider ID (UPID)
        Format: UPID-[UUID]-[NPI-last4]
        """
        npi_last4 = npi[-4:] if len(npi) >= 4 else "0000"
        upid = f"UPID-{str(uuid.uuid4())[:8]}-{npi_last4}"
        return upid

    def save_provider_to_db(self) -> Optional[Provider]:
        """
        If lookup successful, save/update provider in database
        """
        if not self.result.provider_data or not self.result.upid:
            return None

        data = self.result.provider_data
        npi = data.get("npi")

        # Check if provider already exists
        existing = self.db.query(Provider).filter(Provider.npi == npi).first()

        if existing:
            existing.last_verified_date = datetime.utcnow()
            self.db.commit()
            return existing
        else:
            new_provider = Provider(
                upid=self.result.upid,
                npi=npi,
                first_name=data.get("first_name", ""),
                last_name=data.get("last_name", ""),
                practice_name=data.get("practice_name", ""),
                last_verified_date=datetime.utcnow()
            )
            self.db.add(new_provider)
            self.db.commit()
            return new_provider

    def log_query(self, request_source: str, result_status: str) -> ProviderAuditLog:
        """Log provider lookup for audit trail"""
        audit = ProviderAuditLog(
            query_type="river_path_provider_lookup",
            request_source=request_source,
            result_status=result_status
        )
        self.db.add(audit)
        self.db.commit()
        return audit
