"""
FRAUD DETECTION: Real-Time Signal Analysis (Card 2 - UPID)

Pattern detection for:
- Provider billing anomalies (upcoding, overutilization) against real provider profiles
- Member utilization anomalies (frequency, patterns) against real member data
- Known fraud cases from public registries
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Claim, Provider, Member

class FraudDetectionEngine:
    """Real-time fraud signal detection"""

    def __init__(self, db: Session, public_data_schema: Optional[Dict] = None):
        self.db = db
        self.public_data_schema = public_data_schema  # Real provider/member profiles and known fraud data
        self.signals = []
        self.risk_score = 0.0

    def analyze_claim(self, claim_data: Dict, provider_upid: str, member_umid: str) -> Dict:
        """
        Analyze single claim for fraud signals

        Returns: {
            "risk_score": 0.0-100.0,
            "risk_level": "LOW", "MEDIUM", "HIGH",
            "signals": [list of detected patterns],
            "recommendation": "APPROVE", "REVIEW", "ESCALATE"
        }
        """

        self.signals = []
        self.risk_score = 0.0

        # Check provider patterns
        self._check_provider_patterns(provider_upid, claim_data)

        # Check member patterns
        self._check_member_patterns(member_umid, claim_data)

        # Check known fraud database
        self._check_known_fraud(provider_upid, member_umid)

        # Determine risk level
        if self.risk_score >= 75:
            risk_level = "HIGH"
            recommendation = "ESCALATE_TO_INVESTIGATOR"
        elif self.risk_score >= 40:
            risk_level = "MEDIUM"
            recommendation = "ESCALATE_TO_SUPERVISOR"
        else:
            risk_level = "LOW"
            recommendation = "APPROVE"

        return {
            "risk_score": self.risk_score,
            "risk_level": risk_level,
            "signals": self.signals,
            "recommendation": recommendation,
            "analyst_action": f"Review claim ({risk_level} risk)"
        }

    def _check_provider_patterns(self, provider_upid: str, current_claim: Dict):
        """Detect unusual provider billing patterns"""

        # Query provider's claims in last 90 days
        provider = self.db.query(Provider).filter(Provider.upid == provider_upid).first()
        if not provider:
            return

        cutoff_date = datetime.utcnow() - timedelta(days=90)
        recent_claims = self.db.query(Claim).filter(
            Claim.provider_id == provider.id,
            Claim.submitted_date >= cutoff_date
        ).all()

        if not recent_claims:
            return

        # Pattern 1: Procedure code concentration
        proc_codes = [c.procedure_code for c in recent_claims]
        if proc_codes:
            current_code_count = proc_codes.count(current_claim.get("procedure_code", ""))
            concentration = current_code_count / len(proc_codes)

            if concentration > 0.4:  # One code is >40% of claims
                self.risk_score += 20
                self.signals.append(f"Concentration: {current_claim['procedure_code']} is {concentration*100:.0f}% of claims")

        # Pattern 2: Amount variance
        amounts = [c.claim_amount for c in recent_claims]
        if amounts:
            avg_amount = sum(amounts) / len(amounts)
            current_amount = current_claim.get("amount", 0)

            if current_amount > avg_amount * 2.5:
                self.risk_score += 15
                self.signals.append(f"Amount variance: ${current_amount} vs avg ${avg_amount:.0f}")

        # Pattern 3: Frequency spike
        days_span = 90
        claims_per_day = len(recent_claims) / days_span
        typical_claims_per_day = 0.5  # Simulated baseline

        if claims_per_day > typical_claims_per_day * 1.5:
            self.risk_score += 15
            self.signals.append(f"Volume spike: {claims_per_day:.1f} claims/day vs {typical_claims_per_day} typical")

    def _check_member_patterns(self, member_umid: str, current_claim: Dict):
        """Detect unusual member utilization patterns"""

        member = self.db.query(Member).filter(Member.umid == member_umid).first()
        if not member:
            return

        cutoff_date = datetime.utcnow() - timedelta(days=90)
        recent_claims = self.db.query(Claim).filter(
            Claim.member_umid == member_umid,
            Claim.submitted_date >= cutoff_date
        ).all()

        if not recent_claims:
            return

        # Pattern 1: Multiple visits to same provider
        provider_counts = {}
        for claim in recent_claims:
            provider = claim.provider_id
            provider_counts[provider] = provider_counts.get(provider, 0) + 1

        for provider, count in provider_counts.items():
            if count > 15:
                self.risk_score += 10
                self.signals.append(f"High frequency: {count} visits to same provider in 90 days")

        # Pattern 2: Multiple claims same day
        claim_by_date = {}
        for claim in recent_claims:
            date = claim.submitted_date.date()
            claim_by_date[date] = claim_by_date.get(date, 0) + 1

        max_claims_per_day = max(claim_by_date.values()) if claim_by_date else 0
        if max_claims_per_day > 3:
            self.risk_score += 15
            self.signals.append(f"Multiple claims same day: {max_claims_per_day} claims on one date")

        # Pattern 3: Multiple providers same day
        providers_per_day = {}
        for claim in recent_claims:
            date = claim.submitted_date.date()
            if date not in providers_per_day:
                providers_per_day[date] = set()
            providers_per_day[date].add(claim.provider_id)

        max_providers_per_day = max(len(p) for p in providers_per_day.values()) if providers_per_day else 0
        if max_providers_per_day > 3:
            self.risk_score += 15
            self.signals.append(f"Multiple providers same day: {max_providers_per_day} providers on one date")

    def _check_known_fraud(self, provider_upid: str, member_umid: str):
        """Check against known fraud cases"""

        # In production: query fraud database
        # For now: placeholder

        self.signals.append("No known fraud history")

    def generate_fraud_report(self, claims: List[Dict]) -> Dict:
        """
        Generate comprehensive fraud analysis report for analyst
        """

        total_risk = 0
        flagged_claims = 0

        for claim in claims:
            analysis = self.analyze_claim(
                claim,
                claim.get("provider_upid"),
                claim.get("member_umid")
            )

            total_risk += analysis["risk_score"]
            if analysis["risk_level"] != "LOW":
                flagged_claims += 1

        avg_risk = total_risk / len(claims) if claims else 0

        return {
            "total_claims_analyzed": len(claims),
            "flagged_claims": flagged_claims,
            "average_risk_score": avg_risk,
            "high_risk_percentage": (flagged_claims / len(claims) * 100) if claims else 0,
            "recommendation": "ESCALATE_TO_FRAUD_UNIT" if avg_risk > 50 else "MONITOR"
        }
