"""
ELIGIBILITY DETERMINATION: Translate member data into YES/NO/PENDING
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from sqlalchemy.orm import Session
from models import Member, MemberEligibility, EligibilityStatus, MemberPlanAssignment, PlanType
from enum import Enum

class EligibilityGroup(str, Enum):
    """NY Medicaid eligibility categories"""
    PARENT_CARETAKER = "Parent/Caretaker"
    PREGNANT = "Pregnant"
    CHILD = "Child"
    DISABLED = "Disabled/SSI"
    SENIOR = "Senior/Medicare"
    BREAST_CERVICAL_CANCER = "Breast/Cervical Cancer"

class EligibilityDetermination:
    """
    Determines member's Medicaid eligibility status based on:
    - Income threshold
    - Asset limits
    - Category (parent, child, disabled, etc.)
    - Active application status
    """

    def __init__(self, db: Session, member: Member):
        self.db = db
        self.member = member

    def determine_status(self) -> Tuple[EligibilityStatus, MemberEligibility, float]:
        """
        Determine eligibility status and create/update eligibility record

        Returns:
            (status, eligibility_record, confidence_score)
        """

        # Check for existing eligibility record
        existing = self.db.query(MemberEligibility).filter(
            MemberEligibility.member_id == self.member.id
        ).order_by(MemberEligibility.created_at.desc()).first()

        if existing:
            return self._evaluate_existing_record(existing)
        else:
            return self._create_new_eligibility_record()

    def _evaluate_existing_record(self, eligibility: MemberEligibility) -> Tuple[EligibilityStatus, MemberEligibility, float]:
        """
        Evaluate existing eligibility record:
        - Is coverage still active?
        - Has recertification deadline passed?
        - Has coverage ended?
        """

        today = datetime.now().date()
        coverage_end = datetime.strptime(eligibility.coverage_end_date, "%Y-%m-%d").date() if eligibility.coverage_end_date else None

        # Status: Check if currently active
        if eligibility.status == EligibilityStatus.APPROVED:
            if coverage_end and today > coverage_end:
                # Coverage ended
                eligibility.status = EligibilityStatus.INACTIVE
                eligibility.needs_manual_review = False
                confidence = 0.95
                reason = "Coverage end date passed"

            elif today <= coverage_end:
                # Still active
                eligibility.status = EligibilityStatus.ACTIVE
                confidence = 0.95
                reason = "Coverage active and within period"

            else:
                confidence = 0.95
                reason = "Status unchanged"

        elif eligibility.status == EligibilityStatus.PENDING:
            # Check how long pending
            app_date = datetime.strptime(eligibility.application_date, "%Y-%m-%d").date()
            days_pending = (today - app_date).days

            if days_pending > 30:
                # Should have decision by now; escalate
                eligibility.needs_manual_review = True
                confidence = 0.60
                reason = f"Application pending {days_pending} days (>30 day target)"
            else:
                confidence = 0.70
                reason = f"Application pending {days_pending} days"

        elif eligibility.status == EligibilityStatus.DENIED:
            confidence = 0.95
            reason = f"Denied: {eligibility.denial_reason}"

        eligibility.confidence_score = confidence
        eligibility.confidence_reason = reason
        self.db.commit()

        return eligibility.status, eligibility, confidence

    def _create_new_eligibility_record(self) -> Tuple[EligibilityStatus, MemberEligibility, float]:
        """
        Create new eligibility record when member has no history
        (This is a fallback - in production, would query state system)
        """

        new_eligibility = MemberEligibility(
            member_id=self.member.id,
            status=EligibilityStatus.PENDING,
            eligibility_group=EligibilityGroup.PARENT_CARETAKER.value,
            confidence_score=0.40,
            confidence_reason="No prior eligibility record - needs state verification",
            needs_manual_review=True
        )

        self.db.add(new_eligibility)
        self.db.commit()

        return EligibilityStatus.PENDING, new_eligibility, 0.40

    def get_next_recertification_date(self, eligibility: MemberEligibility) -> Optional[str]:
        """
        Get the member's recertification date
        NY Medicaid: typically every 12 months
        """
        return eligibility.recertification_date

    def get_days_until_recertification(self, eligibility: MemberEligibility) -> Optional[int]:
        """
        Calculate days remaining until recertification deadline
        """
        if not eligibility.recertification_date:
            return None

        today = datetime.now().date()
        recert_date = datetime.strptime(eligibility.recertification_date, "%Y-%m-%d").date()
        days_remaining = (recert_date - today).days

        return days_remaining if days_remaining > 0 else 0

    def should_trigger_recertification_alert(self, eligibility: MemberEligibility) -> bool:
        """
        Check if member should receive recertification reminder (60 days before deadline)
        """
        days_until_recert = self.get_days_until_recertification(eligibility)

        if days_until_recert is None:
            return False

        # Alert if 60 days or less until deadline
        if days_until_recert <= 60 and not eligibility.recert_alert_sent:
            return True

        return False

    def check_income_impact(self, new_income: float, eligibility: MemberEligibility) -> Dict:
        """
        Check if reported income would affect eligibility

        Returns:
            {
                "current_income": float,
                "new_income": float,
                "income_limit": float,
                "impact": "ELIGIBLE" | "INELIGIBLE",
                "member_message": str,
                "confidence": float
            }
        """

        income_limit = eligibility.income_limit
        current_income = eligibility.reported_income

        if new_income > income_limit:
            impact = "INELIGIBLE"
            message = f"Reported income (${new_income}) exceeds limit (${income_limit}). You may lose coverage. Contact caseworker BEFORE making changes."

        elif new_income < income_limit:
            impact = "ELIGIBLE"
            message = f"Reported income (${new_income}) is within limit (${income_limit}). Remain eligible, but report change to caseworker."

        else:
            impact = "AT_LIMIT"
            message = f"Income exactly at limit. Report to caseworker for confirmation."

        return {
            "current_income": current_income,
            "new_income": new_income,
            "income_limit": income_limit,
            "impact": impact,
            "member_message": message,
            "confidence": 0.90,
            "recommendation": "REPORT_CHANGE" if new_income != current_income else "NO_ACTION"
        }

    def get_plan_assignment(self) -> Optional[MemberPlanAssignment]:
        """Get member's current plan assignment"""
        plan = self.db.query(MemberPlanAssignment).filter(
            MemberPlanAssignment.member_id == self.member.id,
            MemberPlanAssignment.active == True
        ).first()

        return plan

    def validate_plan_for_member_needs(self, plan: MemberPlanAssignment) -> Dict:
        """
        Verify that member's assigned plan is appropriate for their needs
        (e.g., SNP for special needs members)
        """

        if plan.is_snp:
            # Member should be in SNP
            if plan.plan_type == PlanType.SNP:
                validation = {
                    "plan_status": "CORRECT_ASSIGNMENT",
                    "message": f"Member correctly assigned to {plan.snp_specialty} Special Needs Plan",
                    "confidence": 0.95
                }
            else:
                validation = {
                    "plan_status": "WRONG_PLAN",
                    "message": f"Member needs SNP for {plan.snp_specialty}, but assigned to {plan.plan_type}",
                    "confidence": 0.90,
                    "escalation": "Plan optimizer should review"
                }
        else:
            # Regular member
            validation = {
                "plan_status": "ACTIVE",
                "message": f"Member assigned to {plan.plan_name}",
                "confidence": 0.90
            }

        return validation
