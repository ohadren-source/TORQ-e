"""
PROVIDER LOOKUP & ENROLLMENT VERIFICATION (Card 2 - UPID)

River Path for Providers:
  Attempt 1: eMedNY (FFS enrollment database)
  Attempt 2: MCO Panel Aggregator (all 5+ MCO enrollments)
  Attempt 3: NPI Database (provider exists but not enrolled)
"""

import uuid
from typing import Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models import Provider, ProviderEnrollmentStatus, DataSource, ProviderAuditLog
import httpx
import asyncio

class ProviderLookupResult:
    def __init__(self):
        self.provider_data: Optional[Dict] = None
        self.upid: Optional[str] = None
        self.data_source: Optional[DataSource] = None
        self.confidence: float = 0.0
        self.flags: list = []
        self.error: Optional[str] = None
        self.ffs_enrollment: Optional[Dict] = None
        self.mco_enrollments: Dict = {}

class ProviderLookupExecutor:
    """Implements River Path for provider identification"""

    def __init__(self, db: Session, timeout_seconds: int = 30):
        self.db = db
        self.timeout = timeout_seconds
        self.result = ProviderLookupResult()

    async def execute(self, npi: str, first_name: Optional[str] = None, last_name: Optional[str] = None) -> ProviderLookupResult:
        """
        Execute River Path for provider:
        1. eMedNY FFS Enrollment
        2. MCO Panel Aggregator
        3. NPI Database
        """

        # Attempt 1: eMedNY FFS ENROLLMENT (Authoritative for FFS)
        emedny_result = await self._attempt_emedny_ffs(npi)
        if emedny_result["success"]:
            self.result.provider_data = emedny_result["data"]
            self.result.data_source = DataSource.STATE_MEDICAID
            self.result.confidence = 0.95
            self.result.ffs_enrollment = emedny_result["enrollment"]
            self.result.upid = self._generate_upid(npi, self.result.provider_data)

            # Also check MCO enrollments in parallel
            await self._check_mco_enrollments(npi)
            return self.result

        # Attempt 2: MCO PANEL AGGREGATOR (Check all MCOs)
        mco_result = await self._attempt_mco_aggregator(npi)
        if mco_result["success"]:
            self.result.provider_data = mco_result["data"]
            self.result.data_source = DataSource.STATE_MEDICAID
            self.result.confidence = 0.85
            self.result.mco_enrollments = mco_result["enrollments"]
            self.result.upid = self._generate_upid(npi, self.result.provider_data)
            self.result.flags.append("Enrolled in MCO only - check FFS status separately")
            return self.result

        # Attempt 3: NPI DATABASE (Provider exists but may not be Medicaid-enrolled)
        npi_result = await self._attempt_npi_database(npi, first_name, last_name)
        if npi_result["success"]:
            self.result.provider_data = npi_result["data"]
            self.result.data_source = DataSource.NPI_DATABASE
            self.result.confidence = 0.70
            self.result.flags.append("Provider found but NOT enrolled in Medicaid")
            self.result.upid = self._generate_upid(npi, self.result.provider_data)
            return self.result

        # All attempts failed
        self.result.error = "Provider not found in any system"
        self.result.flags.append("Verify NPI number or contact EMEDNY directly")
        return self.result

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

    async def _check_mco_enrollments(self, npi: str):
        """
        Background check: Query all MCO enrollments even if FFS was found
        """
        mco_result = await self._attempt_mco_aggregator(npi)
        if mco_result["success"]:
            self.result.mco_enrollments = mco_result["enrollments"]

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
