"""
CONFIDENCE SCORING: Signal Processing Framework

Based on: ClaudeShannon++ signal transmission model
Formula: CONFIDENCE(source) = [Quality/Quantity] × [(Understanding - Dependence - Misunderstanding - Unknown) / Time]

Simplified for Medicaid:
  - Quality: How authoritative is the source?
  - Quantity: How complete is the data?
  - Understanding: Do we comprehend what the data means?
  - Dependence: How much do we depend on external systems?
  - Misunderstanding: How much room for error?
  - Unknown: What's missing?
"""

from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class DataSourceQuality(float, Enum):
    """Authoritative ranking of data sources"""
    OFFICIAL_STATE_SYSTEM = 0.98  # Direct query to state Medicaid database
    FEDERAL_DATABASE = 0.95        # SSA, IRS official databases
    STATE_PUBLISHED = 0.90         # State-published documents/data
    PLAN_OFFICIAL = 0.85           # MCO official member services
    PROVIDER_REPORTED = 0.75       # Healthcare provider reports
    HOUSEHOLD_ENROLLMENT = 0.70    # Household-level data (needs individual confirmation)
    THIRD_PARTY = 0.60             # Clearinghouse, intermediary data
    MEMBER_REPORTED = 0.50         # Member self-reported (unverified)
    SOCIAL_MEDIA = 0.10            # Social media, rumors, unverified claims

class ConfidenceScorer:
    """
    Score confidence in member eligibility determination
    Returns: 0.0 (no confidence) to 1.0 (absolute certainty)
    """

    def __init__(self):
        self.score = 0.0
        self.components = {}
        self.signals = []

    def score_river_path_result(self, data_source: str, data_completeness: float, age_minutes: int) -> float:
        """
        Score a River Path result

        Args:
            data_source: Which source provided the data (STATE_MEDICAID, SSA, HOUSEHOLD, etc.)
            data_completeness: How complete is the data? (0.0 to 1.0)
                - 1.0 = all required fields present
                - 0.8 = missing non-critical fields
                - 0.5 = missing critical fields
            age_minutes: How old is the data? (minutes)
                - 0 = real-time
                - 1440 = 24 hours old
                - 10080 = 7 days old

        Returns:
            Confidence score (0.0 to 1.0)
        """

        # Quality of source
        source_quality_map = {
            "STATE_MEDICAID": DataSourceQuality.OFFICIAL_STATE_SYSTEM.value,
            "SSA_WAGE_RECORDS": DataSourceQuality.FEDERAL_DATABASE.value,
            "HOUSEHOLD_ENROLLMENT": DataSourceQuality.HOUSEHOLD_ENROLLMENT.value,
            "PLAN_OFFICIAL": DataSourceQuality.PLAN_OFFICIAL.value,
            "MEMBER_REPORTED": DataSourceQuality.MEMBER_REPORTED.value,
        }

        source_quality = source_quality_map.get(data_source, 0.5)

        # Data completeness factor
        completeness_factor = data_completeness

        # Age factor (data freshness)
        if age_minutes == 0:
            age_factor = 1.0  # Real-time is best
        elif age_minutes <= 1440:  # 24 hours
            age_factor = 0.95
        elif age_minutes <= 10080:  # 7 days
            age_factor = 0.85
        elif age_minutes <= 43200:  # 30 days
            age_factor = 0.70
        else:  # >30 days
            age_factor = 0.50

        # Combined confidence
        confidence = source_quality * completeness_factor * age_factor

        self.components["source_quality"] = source_quality
        self.components["completeness"] = completeness_factor
        self.components["freshness"] = age_factor
        self.score = confidence

        return confidence

    def score_eligibility_determination(self, factors: Dict) -> float:
        """
        Score confidence in eligibility determination

        Args:
            factors: {
                "application_status": str,  # "APPROVED", "PENDING", "DENIED"
                "income_verified": bool,    # Is income verified and recent?
                "documents_provided": int,  # How many supporting documents?
                "days_since_verification": int,
                "is_at_deadline": bool,     # Is member at recert deadline?
                "prior_history_consistent": bool,  # Does this match prior records?
            }
        """

        base_confidence = 0.5

        # Application status (biggest factor)
        app_status = factors.get("application_status", "UNKNOWN")
        if app_status == "APPROVED":
            base_confidence = 0.90
        elif app_status == "PENDING":
            base_confidence = 0.60
        elif app_status == "DENIED":
            base_confidence = 0.85  # High confidence in denial

        # Income verification
        if factors.get("income_verified"):
            base_confidence += 0.05
        else:
            base_confidence -= 0.10

        # Supporting documents
        docs_count = factors.get("documents_provided", 0)
        if docs_count >= 3:
            base_confidence += 0.05
        elif docs_count < 1:
            base_confidence -= 0.15

        # Data freshness
        days_since_verified = factors.get("days_since_verification", 0)
        if days_since_verified <= 30:
            base_confidence += 0.05
        elif days_since_verified > 180:
            base_confidence -= 0.10

        # At deadline escalation
        if factors.get("is_at_deadline"):
            base_confidence -= 0.10  # Less confident near recert deadline

        # Historical consistency
        if factors.get("prior_history_consistent"):
            base_confidence += 0.05

        # Clamp to 0.0-1.0
        self.score = max(0.0, min(1.0, base_confidence))
        self.components = factors
        return self.score

    def score_consensus(self, source_scores: List[Dict]) -> float:
        """
        Score consensus when multiple sources agree/disagree

        Args:
            source_scores: [
                {"source": "STATE_MEDICAID", "score": 0.95},
                {"source": "SSA", "score": 0.85},
                {"source": "HOUSEHOLD", "score": 0.70},
            ]

        Returns:
            Consensus confidence score
        """

        if not source_scores:
            return 0.0

        scores = [s["score"] for s in source_scores]
        avg_score = sum(scores) / len(scores)

        # Agreement metric: how much do sources agree?
        max_score = max(scores)
        min_score = min(scores)
        agreement = 1.0 - ((max_score - min_score) / 1.0)

        # Consensus = average agreement weighted by individual confidence
        consensus = (avg_score * 0.6) + (agreement * 0.4)

        self.signals.append({
            "type": "consensus",
            "sources": len(source_scores),
            "average": avg_score,
            "agreement": agreement,
            "consensus": consensus
        })

        return consensus

    def get_confidence_level_label(self, score: float) -> str:
        """Convert numeric score to human-readable label"""
        if score >= 0.85:
            return "HIGH"
        elif score >= 0.60:
            return "MEDIUM"
        elif score >= 0.40:
            return "LOW"
        else:
            return "CRITICAL - ESCALATE"

    def generate_caveat(self, score: float, factors: Dict) -> Optional[str]:
        """
        Generate a caveat/warning if confidence is below threshold

        This is the "honest transparency" principle:
        - Don't hedge ("maybe", "possibly")
        - Do state clearly what's uncertain and why
        """

        if score >= 0.85:
            return None  # High confidence, no caveat needed

        caveat_parts = []

        if score < 0.40:
            caveat_parts.append("⚠️ CRITICAL: This determination should be verified by a caseworker")

        app_status = factors.get("application_status")
        if app_status == "PENDING":
            caveat_parts.append("• Application is pending and not yet approved")

        if not factors.get("income_verified"):
            caveat_parts.append("• Income has not been recently verified")

        if factors.get("days_since_verification", 0) > 180:
            caveat_parts.append("• Data is older than 6 months")

        if factors.get("documents_provided", 0) < 1:
            caveat_parts.append("• No supporting documents provided")

        if caveat_parts:
            return "\n".join(caveat_parts)

        return None

    def to_dict(self) -> Dict:
        """Export confidence score details"""
        return {
            "score": round(self.score, 2),
            "level": self.get_confidence_level_label(self.score),
            "components": self.components,
            "signals": self.signals
        }


class TieredConfidenceReporting:
    """
    Different stakeholders see different detail levels of confidence
    """

    @staticmethod
    def for_member(confidence_dict: Dict) -> Dict:
        """
        Member sees: Simple yes/no with clear language
        """
        return {
            "eligibility": confidence_dict["level"],
            "message": TieredConfidenceReporting._get_member_message(confidence_dict["score"])
        }

    @staticmethod
    def for_provider(confidence_dict: Dict) -> Dict:
        """
        Provider sees: Confidence level with key factors
        """
        return {
            "confidence_level": confidence_dict["level"],
            "confidence_score": confidence_dict["score"],
            "key_factors": confidence_dict.get("components", {}),
            "action_required": confidence_dict["score"] < 0.65
        }

    @staticmethod
    def for_analyst(confidence_dict: Dict) -> Dict:
        """
        Analyst sees: Full breakdown with all signals
        """
        return confidence_dict  # Full detail

    @staticmethod
    def _get_member_message(score: float) -> str:
        """Generate plain-language message for member"""
        if score >= 0.85:
            return "You should be covered. Check your plan for specific details."
        elif score >= 0.60:
            return "You appear eligible, but we recommend confirming with your plan."
        elif score >= 0.40:
            return "We cannot confirm your coverage. Contact your caseworker or the Medicaid office."
        else:
            return "You may not be covered. Please contact the Medicaid office immediately."
