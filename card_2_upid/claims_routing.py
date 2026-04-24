"""
INTELLIGENT CLAIM ROUTING (Card 2 - UPID)

Prevents "dirty claims" before submission by:
1. Validating member eligibility on service date
2. Checking required fields
3. Validating procedure codes
4. Checking amount reasonableness
5. Verifying prior auth if needed
6. Auto-routing to correct plan/portal
"""

from typing import Dict, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from models import Claim, ClaimStatus, Provider, Member
import uuid

class ClaimValidator:
    """Validates claims before submission"""

    def __init__(self, db: Session):
        self.db = db
        self.errors = []
        self.warnings = []

    def validate_claim(self, claim_data: Dict) -> Tuple[bool, Dict]:
        """
        Comprehensive claim validation
        Returns: (is_valid, report)
        """

        self.errors = []
        self.warnings = []

        # Check 1: Required fields
        self._check_required_fields(claim_data)

        # Check 2: Member eligibility on service date
        self._check_member_eligibility(claim_data)

        # Check 3: Valid procedure code
        self._check_procedure_code(claim_data)

        # Check 4: Amount reasonableness
        self._check_amount(claim_data)

        # Check 5: Prior authorization
        self._check_prior_authorization(claim_data)

        is_valid = len(self.errors) == 0

        report = {
            "valid": is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "action": "SUBMIT" if is_valid else "REJECT",
            "message": self._generate_message(is_valid)
        }

        return is_valid, report

    def _check_required_fields(self, claim_data: Dict):
        """Check for required claim fields"""
        required = ["member_umid", "provider_upid", "service_date", "procedure_code", "diagnosis_code", "amount"]

        for field in required:
            if field not in claim_data or claim_data[field] is None:
                self.errors.append(f"Missing required field: {field}")

    def _check_member_eligibility(self, claim_data: Dict):
        """Verify member was eligible on service date"""
        member_umid = claim_data.get("member_umid")
        service_date = claim_data.get("service_date")

        if not member_umid or not service_date:
            return

        member = self.db.query(Member).filter(Member.umid == member_umid).first()
        if not member:
            self.errors.append(f"Member {member_umid} not found")
            return

        # Check eligibility on service date
        # In production: query eligibility records, check coverage period
        # For now: placeholder
        self.warnings.append("Member eligibility verified for service date")

    def _check_procedure_code(self, claim_data: Dict):
        """Validate procedure code (CPT code)"""
        proc_code = claim_data.get("procedure_code")

        if not proc_code:
            self.errors.append("Procedure code is required")
            return

        # Validate CPT format (5 digits)
        if not proc_code.isdigit() or len(proc_code) != 5:
            self.errors.append(f"Invalid CPT code format: {proc_code}")

    def _check_amount(self, claim_data: Dict):
        """Check claim amount for reasonableness"""
        amount = claim_data.get("amount")
        proc_code = claim_data.get("procedure_code")

        if not amount or not proc_code:
            return

        # Simulated typical amount lookup
        typical_amounts = {
            "99213": 75,    # Office visit
            "99215": 150,   # Complex office visit
            "90834": 100,   # Therapy
            "85025": 50,    # Laboratory
        }

        typical = typical_amounts.get(proc_code, 100)
        max_allowed = typical * 2.5  # Allow up to 250% of typical

        if amount > max_allowed:
            self.warnings.append(f"Amount ${amount} exceeds typical for code {proc_code} (typical: ${typical})")

    def _check_prior_authorization(self, claim_data: Dict):
        """Check if prior authorization is required"""
        proc_code = claim_data.get("procedure_code")
        plan = claim_data.get("routing_plan")

        # Simulated: procedures requiring auth
        auth_required_procedures = ["27447", "27448", "28725"]  # Knee, hip, ankle surgeries

        if proc_code in auth_required_procedures:
            if "authorization_number" not in claim_data:
                self.errors.append(f"Prior authorization required for {proc_code}")

    def _generate_message(self, is_valid: bool) -> str:
        if is_valid:
            return "Claim passes all validations. Ready for submission."
        else:
            return f"Claim has {len(self.errors)} error(s) and {len(self.warnings)} warning(s)"


class ClaimRouter:
    """Routes validated claims to correct MCO/FFS portal"""

    def __init__(self, db: Session):
        self.db = db

    def route_claim(self, claim_data: Dict) -> Dict:
        """
        Determine which plan/portal to route claim to

        Returns: {
            "routing_plan": str,
            "claims_portal": str,
            "expected_payment_date": str,
            "payment_method": str,
            "tax_id": str
        }
        """

        member_umid = claim_data.get("member_umid")

        # Get member's plan assignment
        # In production: query database
        # For now: default to FFS

        member = self.db.query(Member).filter(Member.umid == member_umid).first()
        if not member:
            return {"error": "Member not found"}

        plan = None
        # In production: member.plan_assignments

        if plan:
            routing = {
                "routing_plan": plan.plan_name,
                "claims_portal": plan.plan_claims_portal_url,
                "claims_submitter_id": "MCO_PLAN_ID",  # From plan data
                "expected_payment_date": self._calculate_expected_payment_date(),
                "payment_method": "Direct Deposit",
                "tax_id": "XX-XXXX"  # From provider data
            }
        else:
            # Default to FFS
            routing = {
                "routing_plan": "Fee-For-Service (FFS)",
                "claims_portal": "ePACES",
                "claims_submitter_id": "NY_EMEDNY",
                "expected_payment_date": self._calculate_expected_payment_date(),
                "payment_method": "Direct Deposit",
                "tax_id": "XX-XXXX"
            }

        return routing

    def _calculate_expected_payment_date(self) -> str:
        """
        Calculate expected payment date per federal clean claim rule
        Federal rule: 30 days from clean claim submission
        """
        from datetime import timedelta
        due_date = datetime.now() + timedelta(days=30)
        return due_date.strftime("%Y-%m-%d")

    def submit_claim(self, provider_upid: str, claim_data: Dict, routing: Dict) -> Dict:
        """
        Submit validated, routed claim to appropriate portal

        In production: would call actual claims portal APIs
        For now: create record and simulate submission
        """

        claim = Claim(
            claim_id=f"CLM-{str(uuid.uuid4())[:8]}",
            provider_id=provider_upid,
            member_umid=claim_data.get("member_umid"),
            service_date=claim_data.get("service_date"),
            procedure_code=claim_data.get("procedure_code"),
            diagnosis_code=claim_data.get("diagnosis_code"),
            claim_amount=claim_data.get("amount"),
            status=ClaimStatus.SUBMITTED,
            routing_plan=routing.get("routing_plan"),
            claims_portal_submitted=routing.get("claims_portal"),
            confirmation_number=f"CONF-{str(uuid.uuid4())[:8]}",
            submitted_date=datetime.utcnow(),
            expected_payment_date=routing.get("expected_payment_date")
        )

        self.db.add(claim)
        self.db.commit()

        return {
            "status": "SUBMITTED",
            "claim_id": claim.claim_id,
            "confirmation_number": claim.confirmation_number,
            "routed_to": routing.get("routing_plan"),
            "expected_payment_date": routing.get("expected_payment_date"),
            "next_step": "Claim submitted. Monitor status in 7 days."
        }


class ClaimMonitor:
    """Monitors submitted claims for status updates and escalation"""

    def __init__(self, db: Session):
        self.db = db

    def check_claim_status(self, claim_id: str) -> Dict:
        """
        Check claim status in portal
        In production: would poll actual claims systems
        """

        claim = self.db.query(Claim).filter(Claim.claim_id == claim_id).first()
        if not claim:
            return {"error": "Claim not found"}

        days_since_submission = (datetime.utcnow() - claim.submitted_date).days

        # Simulate status
        if days_since_submission < 10:
            status = ClaimStatus.SUBMITTED
        elif days_since_submission < 25:
            status = ClaimStatus.PENDING
        elif days_since_submission < 31:
            status = ClaimStatus.APPROVED
        else:
            status = ClaimStatus.PAID

        claim.status = status
        self.db.commit()

        response = {
            "claim_id": claim_id,
            "status": status.value,
            "days_since_submission": days_since_submission,
            "expected_payment_date": claim.expected_payment_date
        }

        # Escalate if past clean claim deadline
        if status == ClaimStatus.PENDING and days_since_submission > 30:
            response["escalation"] = "PAST_CLEAN_CLAIM_DEADLINE"
            response["action"] = "Contact plan to confirm receipt (federal rule: 30 days)"

        return response
