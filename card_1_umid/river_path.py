"""
RIVER PATH ALGORITHM: Multi-Source Member Identification

Core logic:
  Attempt 1: STATE MEDICAID (authoritative)
  Attempt 2: SSA WAGE RECORDS (backup)
  Attempt 3: HOUSEHOLD ENROLLMENT (fallback)
  If all fail: Escalate with caveat
"""

import uuid
from typing import Dict, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from models import Member, DataSource, AuditLog
from config import settings
import httpx
import asyncio

class RiverPathResult:
    def __init__(self):
        self.member_data: Optional[Dict] = None
        self.umid: Optional[str] = None
        self.data_source: Optional[DataSource] = None
        self.confidence: float = 0.0
        self.flags: list = []
        self.error: Optional[str] = None
        self.attempts: Dict = {}

class RiverPathExecutor:
    """Implements River Path algorithm for member identification"""

    def __init__(self, db: Session, timeout_seconds: int = 30):
        self.db = db
        self.timeout = timeout_seconds
        self.result = RiverPathResult()

    async def execute(self, first_name: str, last_name: str, dob: str, ssn: str) -> RiverPathResult:
        """
        Execute River Path attempts in sequence:
        1. State Medicaid API
        2. SSA Wage Records
        3. Household Enrollment System
        """

        # Attempt 1: STATE MEDICAID API (Authoritative)
        state_result = await self._attempt_state_medicaid(first_name, last_name, dob, ssn)
        self.result.attempts["state_medicaid"] = state_result

        if state_result["success"]:
            self.result.member_data = state_result["data"]
            self.result.data_source = DataSource.STATE_MEDICAID
            self.result.confidence = 0.95
            self.result.umid = self._generate_umid(self.result.member_data)
            return self.result

        # Attempt 2: SSA WAGE RECORDS (Backup)
        ssa_result = await self._attempt_ssa_wage_records(ssn)
        self.result.attempts["ssa_wage_records"] = ssa_result

        if ssa_result["success"]:
            self.result.member_data = ssa_result["data"]
            self.result.data_source = DataSource.SSA_WAGE_RECORDS
            self.result.confidence = 0.85
            self.result.flags.append("SSA data only - needs state confirmation")
            self.result.umid = self._generate_umid(self.result.member_data)
            return self.result

        # Attempt 3: HOUSEHOLD ENROLLMENT SYSTEM (Fallback)
        household_result = await self._attempt_household_enrollment(last_name, dob)
        self.result.attempts["household_enrollment"] = household_result

        if household_result["success"]:
            self.result.member_data = household_result["data"]
            self.result.data_source = DataSource.HOUSEHOLD_ENROLLMENT
            self.result.confidence = 0.70
            self.result.flags.append("Household data only - needs individual confirmation")
            self.result.umid = self._generate_umid(self.result.member_data)
            return self.result

        # All attempts failed
        self.result.error = "Member not found in any data source"
        self.result.flags.append("Escalate to local Medicaid office")
        return self.result

    async def _attempt_state_medicaid(self, first_name: str, last_name: str, dob: str, ssn: str) -> Dict:
        """
        Attempt 1: Query State Medicaid API (most authoritative)
        In production, this would call: NY DOH Medicaid API
        For now, return simulated response
        """
        try:
            # Simulate API call with timeout
            timeout = httpx.Timeout(self.timeout)
            async with httpx.AsyncClient(timeout=timeout) as client:
                # Placeholder: In production, this would call the actual state API
                # response = await client.get(f"{settings.state_medicaid_api_url}?ssn={ssn}")

                # For development, return mock data if SSN matches pattern
                if ssn and len(ssn) == 9:
                    return {
                        "success": True,
                        "data": {
                            "first_name": first_name,
                            "last_name": last_name,
                            "date_of_birth": dob,
                            "ssn": ssn,
                            "state_case_number": f"NY{ssn[-4:]}",
                            "source": "STATE_MEDICAID"
                        }
                    }
                else:
                    return {"success": False, "error": "Invalid SSN format"}

        except asyncio.TimeoutError:
            return {"success": False, "error": "State Medicaid API timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _attempt_ssa_wage_records(self, ssn: str) -> Dict:
        """
        Attempt 2: Query SSA Wage Records (backup source)
        In production: SSA Supplemental Security Income (SSI) system
        """
        try:
            # Placeholder: In production, this would call SSA API
            if ssn and len(ssn) == 9:
                return {
                    "success": True,
                    "data": {
                        "ssn": ssn,
                        "wage_record_found": True,
                        "source": "SSA_WAGE_RECORDS"
                    }
                }
            else:
                return {"success": False, "error": "Invalid SSN"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _attempt_household_enrollment(self, last_name: str, dob: str) -> Dict:
        """
        Attempt 3: Query Household Enrollment System (fallback)
        Uses name + DOB to find household, then individual within household
        """
        try:
            # Placeholder: In production, this would query household enrollment records
            if last_name and dob:
                return {
                    "success": True,
                    "data": {
                        "last_name": last_name,
                        "date_of_birth": dob,
                        "household_found": True,
                        "source": "HOUSEHOLD_ENROLLMENT"
                    }
                }
            else:
                return {"success": False, "error": "Insufficient data"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _generate_umid(self, member_data: Dict) -> str:
        """
        Generate Unified Member ID (UMID)
        Format: UMID-[UUID]-[last4SSN]
        """
        ssn = member_data.get("ssn", "0000")
        last_4_ssn = ssn[-4:] if len(ssn) >= 4 else "0000"
        umid = f"UMID-{str(uuid.uuid4())[:8]}-{last_4_ssn}"
        return umid

    def save_member_to_db(self) -> Optional[Member]:
        """
        If River Path successful, save/update member in database
        """
        if not self.result.member_data or not self.result.umid:
            return None

        data = self.result.member_data

        # Check if member already exists
        existing_member = self.db.query(Member).filter(
            Member.umid == self.result.umid
        ).first()

        if existing_member:
            # Update existing
            existing_member.last_verified_date = datetime.utcnow()
            existing_member.primary_data_source = self.result.data_source
            self.db.commit()
            return existing_member

        else:
            # Create new
            new_member = Member(
                umid=self.result.umid,
                first_name=data.get("first_name", ""),
                last_name=data.get("last_name", ""),
                date_of_birth=data.get("date_of_birth", ""),
                ssn=data.get("ssn", ""),
                primary_data_source=self.result.data_source,
                last_verified_date=datetime.utcnow()
            )
            self.db.add(new_member)
            self.db.commit()
            return new_member

    def log_query(self, request_source: str, result_status: str) -> AuditLog:
        """Log this River Path query for audit trail"""
        audit = AuditLog(
            query_type="river_path_member_lookup",
            request_source=request_source,
            result_status=result_status,
            result_confidence=self.result.confidence
        )
        self.db.add(audit)
        self.db.commit()
        return audit
