# TORQ-E Card 4: Government Stakeholder Governance Architecture
## Internal Design Repository (DR)

**Status:** ✅ IMPLEMENTED (LIVE on Railway)
**Version:** 1.0.0  
**Last Updated:** 2026-04-25

---

## Overview

**Card 4 (USHI)** is the government oversight layer serving three distinct stakeholders with different needs, workflows, and information requirements—all from the same unified backend.

**Stakeholders:**
- **Bob Pollock** (Enterprise Data Governance): System stability, compliance, audit integrity, overnight incident summaries
- **OMIG Investigator** (Fraud Investigation): Fraud signals, case management, evidence chains, pattern analysis
- **User 3** (eMedNY Operations): Claims processing health, operational metrics, budget tracking, enrollment trends

**Core Principle:** One system, three voices. Same data. Different dimensions. Same spectrum analyzer engine, different bar configurations.

**QD:** The system is executing right now, proving itself continuously. Bob watches it work in real-time via conversational governance interface.

**Deployment:** Railway (https://torq-e-production.up.railway.app/api/card4)

---

## Data Model

### Unified Signal Foundation

All Card 4 functionality is built on **signal strength**—a measurement of system stability across multiple dimensions.

```
SystemSignal {
  id: string
  timestamp: datetime (immutable)
  dimension: enum (
    SYSTEM_STABILITY,
    COMPLIANCE_STATUS,
    AUDIT_TRAIL_INTEGRITY,
    DATA_FRESHNESS,
    FRAUD_RISK,
    NETWORK_ANOMALY,
    PATTERN_STRENGTH,
    EVIDENCE_CONFIDENCE,
    PROCESSING_VOLUME,
    ERROR_RATE,
    PAYMENT_STATUS,
    BUDGET_HEALTH
  )
  value: number (0-100, where 100=perfect, 0=critical failure)
  confidence_score: number (0-100, statistical confidence in this measurement)
  color: enum (GREEN=75-100, YELLOW=25-74, RED=0-24)
  source_claim_ids: string[] (which claims triggered this signal?)
  source_details: {
    metric_name: string
    baseline_value: number
    current_value: number
    deviation_percentage: number
    standard_deviations: number
  }
  audit_trail: {
    calculated_by: string (system component)
    calculation_method: string
    verified_by: string (if human-verified)
    timestamp: datetime
  }
}

SpectrogramFrame {
  id: string
  timestamp: datetime
  user_role: enum (GOVERNANCE_AUTHORITY, FRAUD_INVESTIGATOR, OPERATIONS_DIRECTOR)
  signal_dimensions: [SystemSignal] (configurable per role)
  summary_status: enum (STABLE, CAUTION, CRITICAL)
  alert_flags: string[] (things that need attention)
  visualization_preference: enum (TRAFFIC_LIGHTS, SPECTRUM_ANALYZER)
}
```

### Bob Pollock's Data Model (Governance)

```
GovernanceSignal {
  id: string
  timestamp: datetime
  bob_dimensions: {
    system_stability: SystemSignal (are claims flowing normally?)
    compliance_status: SystemSignal (are we audit-ready?)
    audit_trail_integrity: SystemSignal (are records immutable?)
    data_freshness: SystemSignal (how current is our data?)
  }
  overnight_incident_summary: {
    incidents_count: number
    critical_count: number
    resolved_count: number
    pending_count: number
    impact_claims_affected: number
    impact_members_affected: number
  }
  compliance_readiness: {
    audit_trail_completeness: percent (0-100)
    data_quality_score: number (0-100)
    access_control_violations: number
    policy_violations: number
    cms_readiness_percent: number (0-100)
  }
  fraud_flag_summary: {
    high_risk_cases: number
    medium_risk_cases: number
    low_risk_cases: number
    cases_needing_escalation: number
    recommended_actions: string[]
  }
  critical_alerts: [
    {
      timestamp: datetime
      severity: enum (CRITICAL, HIGH, MEDIUM)
      title: string
      description: string
      affected_claims: number
      recommended_action: string
      escalation_path: string
    }
  ]
  audit_trail: immutable log
}
```

### OMIG Investigator's Data Model (Fraud)

```
FraudSignal {
  id: string
  timestamp: datetime
  omig_dimensions: {
    fraud_risk: SystemSignal (probability of fraud?)
    network_anomaly: SystemSignal (suspicious relationships?)
    pattern_strength: SystemSignal (how strong is the pattern?)
    evidence_confidence: SystemSignal (can we prove this?)
  }
  flagged_claim: {
    claim_id: string
    member_id: string (hashed)
    provider_id: string
    claim_amount: number
    service_date: date
    diagnosis_codes: string[]
    procedure_codes: string[]
    why_flagged: string (human-readable explanation)
  }
  fraud_dimensions: {
    billing_anomaly: {
      baseline_member_cost: number
      current_claim_cost: number
      deviation_percent: number
      severity: enum (NORMAL, UNUSUAL, EXTREME)
    }
    provider_deviation: {
      peer_average_billing: number
      this_provider_billing: number
      deviation_std_dev: number
      severity: enum (NORMAL, OUTLIER, EXTREME_OUTLIER)
    }
    member_cycling: {
      services_last_30_days: number
      typical_frequency: number
      frequency_anomaly_percent: number
      severity: enum (NORMAL, ELEVATED, EXCESSIVE)
    }
    network_clustering: {
      related_providers: [string] (other providers billing same member)
      related_members: [string] (other members with same provider combo)
      network_strength: number (0-100)
      known_kickback_pattern: boolean
    }
    temporal_spike: {
      normal_daily_volume: number
      current_daily_volume: number
      spike_percent: number
      spike_confidence: number (0-100)
    }
  }
  historical_pattern: {
    how_long_occurring: duration
    claim_count_in_pattern: number
    total_amount_involved: number
    trend: enum (INCREASING, STABLE, DECREASING)
  }
  cross_state_coordination: {
    same_provider_flagged_in_states: [string]
    same_member_in_states: [string]
    potential_multi_state_ring: boolean
  }
  case_status: enum (FLAGGED, UNDER_INVESTIGATION, REFERRED_TO_PROSECUTION, RESOLVED)
  audit_trail: immutable log
}
```

### User 3's Data Model (Operations)

```
OperationsSignal {
  id: string
  timestamp: datetime
  user3_dimensions: {
    processing_volume: SystemSignal (how many claims processed?)
    error_rate: SystemSignal (what % failed?)
    payment_status: SystemSignal (are payments on time?)
    budget_health: SystemSignal (are we within budget?)
  }
  processing_metrics: {
    claims_processed_today: number
    claims_processed_this_month: number
    success_rate_percent: number
    error_rate_percent: number
    pending_claims: number
    processing_time_avg_minutes: number
    sla_compliance_percent: number (are we hitting our targets?)
  }
  error_breakdown: {
    eligibility_errors: number
    format_errors: number
    duplicate_detection: number
    amount_errors: number
    other_errors: number
    error_trend: enum (IMPROVING, STABLE, WORSENING)
    most_common_error: {
      error_type: string
      count: number
      impact_claims: number
      recommended_fix: string
    }
  }
  payment_processing: {
    payments_authorized_today: number
    payments_processed_today: number
    payment_turnaround_hours_avg: number
    providers_waiting_for_payment: number
    outstanding_amount: number
    payment_sla_days: number
    on_time_percent: number
  }
  budget_metrics: {
    ytd_spend: number
    budget_allocated: number
    budget_remaining: number
    budget_percent_used: number
    cost_per_claim_avg: number
    cost_trend: enum (UP, STABLE, DOWN)
    forecast_end_of_year: number
    forecast_vs_budget: enum (OVER, ON_TRACK, UNDER)
  }
  critical_issues: [
    {
      timestamp: datetime
      issue: string
      impact_claims: number
      root_cause: string (if known)
      resolution_eta: datetime
      escalation_level: enum (RESOLVED, MONITORING, ESCALATED)
    }
  ]
  audit_trail: immutable log
}
```

---

## User Workflows: "A Day in the Life"

### Bob Pollock (Governance) - Tuesday Morning

**6:00 AM:** Wakes up. Checks phone for overnight system alerts.

**7:30 AM:** Arrives at office. Opens Card 4 dashboard.

**Sees (Dashboard View):**

**Top Section - System Health (Spectrum or Traffic Light):**
```
[ GREEN ]  System Stability
  ├─ Claims flowing normally
  ├─ 14.2M claims processed overnight (normal)
  ├─ Success rate: 99.2% (target: 99%+)
  └─ No critical incidents

[ YELLOW ] Compliance Status
  ├─ Audit trail complete: 99.9% (target: 100%)
  ├─ One provider had data format issue (being fixed)
  ├─ Data quality score: 98% (target: 99%+)
  └─ CMS readiness: 99%

[ GREEN ]  Audit Trail Integrity
  ├─ All records immutable: ✓
  ├─ Zero deletions detected: ✓
  ├─ Access log completeness: 100%
  └─ Last verification: 2 hours ago

[ GREEN ]  Data Freshness
  ├─ Current as of: 2 minutes ago
  ├─ Real-time sync: working
  └─ No data staleness issues
```

**Middle Section - Overnight Summary:**
```
INCIDENTS OVERNIGHT:
• Provider network outage, 2:15 AM - 2:47 AM (RESOLVED)
  ├─ Impact: 50K claims queued
  ├─ Resolution: All 50K reprocessed successfully
  ├─ Audit trail: Complete
  └─ Status: RESOLVED

• Data quality alert, 4:30 AM (MONITORING)
  ├─ One provider format error detected
  ├─ Affected claims: 200
  ├─ Action taken: Provider contacted, fix deployed
  └─ Status: MONITORING (will resolve by 8 AM)
```

**Bottom Section - Critical Alerts:**
```
No critical alerts. System stable. ✓
```

**Click to Expand:**
- Detailed compliance metrics
- Full incident log (citations, who responded, when)
- Audit trail export (for external auditors)
- Provider performance breakdown
- Geographic health breakdown

**What Bob does:**
- 30 seconds: Scans dashboard → "System is stable"
- 2 minutes: Reviews overnight incidents → "One provider issue, being fixed, nothing critical"
- 3 minutes: Checks CMS readiness → "99%, we're compliant"
- Done. Confident. Ready to answer questions.

---

### OMIG Investigator - Wednesday Afternoon

**9:00 AM:** Arrives, opens Card 4 dashboard in "Fraud Investigator" mode.

**Sees (Dashboard View):**

**Top Section - Fraud Signal Spectrum (or Traffic Light):**
```
[ RED ]    Fraud Risk Score (Current)
  ├─ 47 claims flagged overnight (high-risk)
  ├─ 8 medium-risk clusters detected
  ├─ 2 potential multi-state rings
  └─ Action needed on 5 cases

[ YELLOW ] Network Anomaly Detection
  ├─ Provider + Lab + Member clusters: 12
  ├─ Known kickback pattern matches: 0 (good)
  ├─ Cross-state duplicates: 3 cases
  └─ Network strength average: 68%

[ YELLOW ] Pattern Strength
  ├─ Billing anomaly: strong (90% confidence)
  ├─ Provider deviation: strong (87% confidence)
  ├─ Member cycling: medium (65% confidence)
  ├─ Temporal spike: strong (92% confidence)
  └─ Overall pattern strength: STRONG

[ GREEN ]  Evidence Confidence
  ├─ Claims with legal-admissible evidence: 12
  ├─ Claims needing more investigation: 23
  ├─ Claims lacking sufficient evidence: 12
  └─ Evidence documentation complete: 95%
```

**Middle Section - Today's High-Risk Flagged Claims:**
```
CLAIMS FLAGGED TODAY (Highest Priority):

Case #1: Potential Kickback Network
├─ Claim ID: CLM-2026-045782
├─ Member: [hashed]
├─ Provider: Dr. Sarah Johnson
├─ Lab: PathLabs Inc.
├─ Fraud Risk: RED (94% confidence)
├─ Pattern: Member referred to lab 23 times in 30 days (normal: 2-3)
│  └─ Dr. Johnson refers 340% more to PathLabs than peers
│  └─ PathLabs billing 240% higher than peers for same tests
├─ Evidence: 
│  ├─ Claim history: [VIEW]
│  ├─ Provider network analysis: [VIEW]
│  ├─ Member access pattern: [VIEW]
│  └─ Audit trail: [VIEW (immutable)]
├─ Cross-state: Same pattern in CA, TX
├─ Recommendation: ESCALATE TO PROSECUTION
└─ Case Status: [CREATE INVESTIGATION CASE]

Case #2: Upcoding Pattern
├─ Claim ID: CLM-2026-045789
├─ Provider: Community Clinic #34
├─ Fraud Risk: YELLOW (78% confidence)
├─ Pattern: Office visits coded as specialist (99% of time)
├─ Impact: Member overage charges, Medicaid overbilled
├─ Status: UNDER INVESTIGATION
└─ Action: Need 2 more months of claims to reach legal threshold

Case #3: Duplicate Billing
├─ Claim ID: CLM-2026-045801
├─ Member: [hashed]
├─ Same service billed twice (2 days apart, same provider)
├─ Fraud Risk: RED (99% confidence)
├─ Amount: $3,200
├─ Status: REFERRED TO PROSECUTION
└─ Expected resolution: [DATE]
```

**Click to Expand:**
- Full claim evidence package (for prosecution)
- Member access history (timeline)
- Provider network visualization (show relationships)
- Cross-state coordination data
- Investigation case creation form
- Multi-case pattern analysis

**What OMIG does:**
- 5 minutes: Scan fraud alerts → "3 cases need prosecution, 5 need more evidence, rest monitoring"
- 30 minutes: Deep dive into top 3 cases → evidence review, cross-state coordination
- 1 hour: Refer 3 cases to DOJ, update investigation statuses
- Done. Moving investigation forward.

---

### User 3 (eMedNY Operations Director) - Thursday Morning

**6:30 AM:** Arrives early, opens Card 4 in "Operations Director" mode.

**Sees (Dashboard View):**

**Top Section - Operations Spectrum (or Traffic Light):**
```
[ GREEN ]  Processing Volume
  ├─ Yesterday: 14.2M claims processed
  ├─ Week average: 14.5M claims/day
  ├─ Trend: Stable
  ├─ Capacity utilization: 67% (we can handle 85%)
  └─ Status: NORMAL

[ GREEN ]  Error Rate
  ├─ Yesterday: 0.8% error rate (target <1%)
  ├─ Error breakdown:
  │  ├─ Eligibility errors: 45K (most common)
  │  ├─ Format errors: 28K
  │  ├─ Duplicate detection: 15K
  │  ├─ Amount errors: 8K
  │  └─ Other: 4K
  ├─ Trend: Improving (was 1.2% last week)
  ├─ Most common error: Provider sent eligibility file in wrong format
  │  └─ Root cause: New provider software (being updated)
  │  └─ Fix ETA: Today at 3 PM
  └─ Status: MONITORING

[ GREEN ]  Payment Status
  ├─ Payments authorized: 14M yesterday
  ├─ Payments processed: 13.9M yesterday
  ├─ Turnaround time: 4.2 hours (target: <6 hours)
  ├─ Providers waiting for payment: 1,200 (normal)
  ├─ Outstanding amount: $120M (normal)
  ├─ On-time payment rate: 98.7% (target: 99%+)
  ├─ SLA compliance: On track
  └─ Status: NORMAL

[ GREEN ]  Budget Health
  ├─ YTD spend: $450M
  ├─ Budget allocated: $650M (state fiscal year)
  ├─ Budget remaining: $200M
  ├─ Budget % used: 69%
  ├─ Cost per claim: $31.69 (target: $32)
  ├─ Trend: Under budget (good)
  ├─ Year-end forecast: $580M (within budget)
  └─ Status: ON TRACK
```

**Middle Section - Critical Issues:**
```
ISSUES TODAY:

Issue #1: Provider Format Error (MONITORING)
├─ Affected claims: ~100K
├─ Impact: 1-2 hour processing delay for affected provider
├─ Root cause: New software at Community Clinic Network
├─ Action taken: Software vendor engaged, fix deployed
├─ Resolution ETA: 3 PM today
├─ Workaround: Manual format conversion (temporary)
└─ Status: BEING RESOLVED

Issue #2: Payment Approval Backlog (RESOLVED)
├─ Yesterday 9 AM: 50K claims in payment queue (unusual)
├─ Cause: High volume of special authorizations needed
├─ Peak time: 9-11 AM
├─ Action: Added payment staff for morning shift
├─ Resolution: Queue cleared by noon
└─ Status: RESOLVED, monitoring continues
```

**Bottom Section - Trending Metrics:**
```
Last 7 Days:
• Processing volume: Stable (14-15M/day)
• Error rate: Improving (1.2% → 0.8%)
• Payment turnaround: Stable (4-5 hours)
• Budget spend: On track ($50-70M/day)
```

**Click to Expand:**
- Detailed error breakdown (which providers, which errors)
- Payment processing timeline (where do bottlenecks exist?)
- Provider performance scoreboard
- Budget detail (spend by category, by quarter)
- Capacity planning forecast (do we need more servers?)
- Cost per claim trend analysis

**What User 3 does:**
- 2 minutes: Check operations status → "Good. Error rate improving. One provider issue being fixed."
- 5 minutes: Review budget → "On track, under budget, looking good"
- 10 minutes: Coordinate with technical team on provider format issue → "Fix deployed, monitoring"
- Done. Operations running smoothly. No escalations needed.

---

## Spectrum Analyzer Engine

### Core Algorithm

The spectrum analyzer is NOT a fraud detection algorithm. It's a **multi-dimensional signal measurement system**.

```python
class SpectrumAnalyzer:
    """
    Measures system health across multiple dimensions simultaneously.
    Returns which dimensions are strong (green), caution (yellow), or critical (red).
    """
    
    def calculate_signal(self, dimension: str, user_role: str) -> SystemSignal:
        """
        For a given dimension and user role, calculate the signal strength.
        
        Dimensions are flexible and role-specific:
        - GOVERNANCE: stability, compliance, audit, freshness
        - FRAUD: fraud_risk, network_anomaly, pattern_strength, evidence
        - OPERATIONS: volume, error_rate, payment_status, budget
        """
        
        if dimension == "SYSTEM_STABILITY":
            # Measure: Are claims flowing normally?
            baseline = historical_average_claims_per_hour
            current = claims_processed_last_hour
            deviation_percent = (current - baseline) / baseline * 100
            
            if deviation_percent > -10 and deviation_percent < 10:
                signal_value = 95  # GREEN (stable)
            elif deviation_percent > -20 or deviation_percent < 20:
                signal_value = 60  # YELLOW (caution)
            else:
                signal_value = 20  # RED (critical)
            
            return SystemSignal(
                dimension=dimension,
                value=signal_value,
                color=self.value_to_color(signal_value),
                source_details={
                    "baseline": baseline,
                    "current": current,
                    "deviation_percent": deviation_percent
                }
            )
        
        elif dimension == "FRAUD_RISK":
            # Measure: How likely is this claim fraudulent?
            billing_anomaly_score = self.calculate_billing_anomaly(claim)
            provider_deviation_score = self.calculate_provider_deviation(claim)
            member_cycling_score = self.calculate_member_cycling(claim)
            network_anomaly_score = self.calculate_network_anomaly(claim)
            temporal_spike_score = self.calculate_temporal_spike(claim)
            
            # Weighted combination
            fraud_risk = (
                0.25 * billing_anomaly_score +
                0.25 * provider_deviation_score +
                0.20 * member_cycling_score +
                0.20 * network_anomaly_score +
                0.10 * temporal_spike_score
            )
            
            return SystemSignal(
                dimension=dimension,
                value=fraud_risk,
                color=self.value_to_color(fraud_risk),
                confidence_score=self.calculate_confidence(fraud_risk),
                source_claim_ids=[claim.id]
            )
        
        # Similar for other dimensions...
    
    def generate_spectrum(self, user_role: str, visualization_preference: str) -> SpectrogramFrame:
        """
        Generate the full spectrum for a user.
        Returns bars to display (and colors) based on role and preference.
        """
        
        if user_role == "GOVERNANCE_AUTHORITY":
            dimensions = [
                "SYSTEM_STABILITY",
                "COMPLIANCE_STATUS",
                "AUDIT_TRAIL_INTEGRITY",
                "DATA_FRESHNESS"
            ]
        elif user_role == "FRAUD_INVESTIGATOR":
            dimensions = [
                "FRAUD_RISK",
                "NETWORK_ANOMALY",
                "PATTERN_STRENGTH",
                "EVIDENCE_CONFIDENCE"
            ]
        elif user_role == "OPERATIONS_DIRECTOR":
            dimensions = [
                "PROCESSING_VOLUME",
                "ERROR_RATE",
                "PAYMENT_STATUS",
                "BUDGET_HEALTH"
            ]
        
        signals = [
            self.calculate_signal(dim, user_role)
            for dim in dimensions
        ]
        
        if visualization_preference == "TRAFFIC_LIGHTS":
            return {
                "visualization": "traffic_lights",
                "status": self.derive_overall_status(signals),
                "signals": signals  # Each rendered as RED/YELLOW/GREEN
            }
        elif visualization_preference == "SPECTRUM_ANALYZER":
            return {
                "visualization": "spectrum",
                "bars": [
                    {
                        "dimension": sig.dimension,
                        "value": sig.value,
                        "color": sig.color,
                        "height": sig.value  # 0-100 pixel height
                    }
                    for sig in signals
                ]
            }
    
    def value_to_color(self, value: float) -> str:
        """Convert signal value (0-100) to color."""
        if value >= 75:
            return "GREEN"
        elif value >= 25:
            return "YELLOW"
        else:
            return "RED"
```

### Key Principles

1. **One dimension = one bar** (in spectrum) or one light (in traffic lights)
2. **Each dimension is independent** (fraud risk doesn't affect audit integrity)
3. **All dimensions update in real-time** (as new claims arrive)
4. **Dimensions are role-specific** (Bob doesn't see fraud dimensions, OMIG doesn't see budget dimensions)
5. **Confidence is measured** (fraud signal at 94% confidence is different from 55% confidence)
6. **Sources are cited** (which claims triggered this signal?)

---

## API Specification

### Authentication & Authorization

```
Header: Authorization: Bearer {token}
{token} contains:
- user_id (Bob Pollock, OMIG analyst, Operations director, etc.)
- user_role (GOVERNANCE_AUTHORITY, FRAUD_INVESTIGATOR, OPERATIONS_DIRECTOR)
- state (NY, CA, etc.)
- permissions (what data can this user see?)
```

### Core Endpoints

```
GET /api/card4/spectrum
  Query params:
    - user_role (GOVERNANCE_AUTHORITY | FRAUD_INVESTIGATOR | OPERATIONS_DIRECTOR)
    - visualization (TRAFFIC_LIGHTS | SPECTRUM_ANALYZER)
    - time_range (1h | 24h | 7d | 30d)
  Returns:
    {
      "timestamp": "2026-04-25T10:15:00Z",
      "overall_status": "STABLE" | "CAUTION" | "CRITICAL",
      "alerts": ["alert1", "alert2"],
      "visualization": {
        "type": "traffic_lights" | "spectrum",
        "bars": [...]  // or "lights": [...]
      },
      "audit_trail": "immutable"
    }

GET /api/card4/incidents
  Query params:
    - time_range (24h)
    - severity (CRITICAL | HIGH | MEDIUM | ALL)
  Returns:
    {
      "incidents": [
        {
          "id": "incident-001",
          "timestamp": "2026-04-25T02:15:00Z",
          "title": "Provider network outage",
          "severity": "HIGH",
          "impact_claims": 50000,
          "status": "RESOLVED",
          "resolution_time_minutes": 32,
          "audit_trail": {...}
        }
      ]
    }

GET /api/card4/compliance-readiness
  Query params:
    - user_role (GOVERNANCE_AUTHORITY)
  Returns:
    {
      "audit_trail_completeness": 99.9,
      "data_quality_score": 98,
      "access_control_violations": 0,
      "cms_readiness_percent": 99,
      "last_audit": "2026-04-25T08:00:00Z",
      "audit_trail": {...}
    }

GET /api/card4/fraud-flags
  Query params:
    - user_role (FRAUD_INVESTIGATOR)
    - risk_level (HIGH | MEDIUM | ALL)
    - limit (10, 50, 100)
  Returns:
    {
      "flags": [
        {
          "claim_id": "CLM-2026-045782",
          "fraud_risk_score": 94,
          "confidence": 94,
          "reason_primary": "kickback pattern detected",
          "reason_secondary": ["network clustering", "provider deviation"],
          "cross_state_match": ["CA", "TX"],
          "case_status": "OPEN",
          "audit_trail": {...}
        }
      ]
    }

GET /api/card4/operations-metrics
  Query params:
    - user_role (OPERATIONS_DIRECTOR)
    - time_range (24h | 7d)
  Returns:
    {
      "processing": {
        "claims_today": 14200000,
        "success_rate": 99.2,
        "error_rate": 0.8,
        "pending": 12000
      },
      "payment": {
        "authorized_today": 14000000,
        "processed_today": 13900000,
        "turnaround_hours": 4.2,
        "on_time_percent": 98.7
      },
      "budget": {
        "ytd_spend": 450000000,
        "budget_remaining": 200000000,
        "forecast_eoy": 580000000
      },
      "audit_trail": {...}
    }

POST /api/card4/investigation-case
  Payload:
    {
      "fraud_flag_id": "CLM-2026-045782",
      "case_name": "Potential Kickback: Dr. Johnson + PathLabs",
      "allegation_type": "KICKBACK_SUSPECTED",
      "initial_findings": "Provider refers 340% more to single lab than peers"
    }
  Returns:
    {
      "case_id": "CASE-2026-001234",
      "status": "CREATED",
      "assigned_to": "OMIG Investigator Name",
      "audit_trail": {...}
    }
```

---

## Role-Based Access Control

```
User Role: GOVERNANCE_AUTHORITY (Bob)
├─ Can view: System stability, compliance, audit, freshness
├─ Can see: Fraud summaries (not details)
├─ Can see: Operations summaries (not budget details)
├─ Can NOT: Create investigation cases, drill into individual claims
├─ Data access: Aggregate only, no member PII

User Role: FRAUD_INVESTIGATOR (OMIG)
├─ Can view: All fraud dimensions and flagged claims
├─ Can see: Member ID (hashed), provider ID, claim details
├─ Can see: Network visualizations, cross-state coordination
├─ Can NOT: Modify system settings, change compliance thresholds
├─ Can: Create and track investigation cases
├─ Data access: Individual claims, member cycling, provider patterns

User Role: OPERATIONS_DIRECTOR (User 3)
├─ Can view: Processing volume, error rate, payment status, budget
├─ Can see: Detailed error breakdown, provider performance
├─ Can NOT: View fraud details, view member PII
├─ Can see: Operational metrics and forecasts
├─ Data access: Aggregate operations data, no member/claim PII
```

---

## Security & Immutability

### Immutable Audit Trail

Every action in Card 4 is logged and never modifiable:

```json
{
  "id": "audit-log-001",
  "timestamp": "2026-04-25T10:15:00Z",
  "user": "bob.pollock@ny.gov",
  "user_role": "GOVERNANCE_AUTHORITY",
  "action": "VIEWED_SPECTRUM",
  "resource": "system_spectrum",
  "parameters": {
    "visualization": "spectrum_analyzer",
    "time_range": "24h"
  },
  "ip_address": "hashed",
  "session_id": "sess-001",
  "outcome": "SUCCESS",
  "audit_trail_status": "IMMUTABLE"
}
```

This record:
- Cannot be deleted
- Cannot be modified
- Is accessible to auditors
- Is queryable by Card 5 (fraud) if needed

### Data Protection

- Member IDs: Hashed in all logs
- Provider IDs: Actual ID (needed for operations)
- Claim amounts: Full precision (needed for fraud detection)
- Audit trails: Encrypted in transit, encrypted at rest

---

## Metrics & Monitoring

**What we measure for each user:**

**Bob:**
- System uptime (%)
- Compliance score
- Audit trail completeness (%)
- Data freshness (minutes behind real-time)
- Critical incidents per week
- Time to resolve incidents

**OMIG:**
- Fraud flags per day
- Fraud detection rate (% of actual fraud caught)
- False positive rate (% of flags that aren't fraud)
- Investigation case completion rate
- Time from flag to prosecution referral
- Recovery amount

**User 3:**
- Claims processed per day
- Error rate (%)
- Payment turnaround time (hours)
- Provider satisfaction (% on-time payment)
- Budget variance (% vs. forecast)
- Cost per claim

---

## Visualization Examples

### Traffic Lights (Simple)

```
┌─────────────────────┐
│  SYSTEM STATUS      │
├─────────────────────┤
│ ● Stability        │  GREEN ✓
│ ● Compliance       │  YELLOW ⚠
│ ● Audit Trail      │  GREEN ✓
│ ● Data Freshness   │  GREEN ✓
└─────────────────────┘
```

### Spectrum Analyzer (Detailed)

```
┌──────────────────────────────────┐
│  GOVERNANCE SPECTRUM             │
├──────────────────────────────────┤
│ Stability    ████████████░░░░  95 │
│ Compliance   ███████████░░░░░░ 84 │
│ Audit Trail  ████████████████  98 │
│ Freshness    ███████████████░░ 91 │
└──────────────────────────────────┘
      0                         100
```

Each bar clickable to expand details, citations, evidence.

---

## "Know Your Audience" Application

**Bob's perspective:** "Is the system stable and compliant? What do I need to worry about?"

**Card 4 shows him:** Traffic light status + overnight incident summary + compliance readiness. That's it. He doesn't need to understand fraud detection algorithms or claims processing bottlenecks.

**OMIG's perspective:** "Which claims are fraudulent? Can I prove it in court?"

**Card 4 shows her:** Fraud signals + evidence confidence + cross-state coordination. She doesn't need system stability metrics or budget forecasts.

---

## Implementation Details

### Frontend (chat-card4.html)

**Deployment:** https://torq-e-production.up.railway.app/chat-card4.html

**Interface:** Conversational chat with intelligent intent routing

**Intent Handlers:**
1. **Metrics Query** → `/api/card4/metrics` 
   - User: "Show me system health" → Returns stability%, audit integrity, active members
   
2. **Trend Query** → `/api/card4/metrics?metric_type=enrollment_rate`
   - User: "What are enrollment trends?" → Returns growth patterns, transfers, disenrollments
   
3. **Quality Query** → `/api/card4/data-quality`
   - User: "Is our data audit-ready?" → Returns completeness%, accuracy%, CMS readiness
   
4. **Governance Query** → `/api/card4/governance-log`
   - User: "Any alerts or flags?" → Returns active governance flags and issues

5. **Help/Default** → Returns guidance on available queries

**Response Format:** HTML-formatted with:
- Color-coded status boxes (GREEN=stable, YELLOW=caution, RED=critical)
- Key metrics with contextual information
- Confidence scores from backend
- Data freshness indicators

### Backend API (card_4_ushi/)

**Location:** `/card_4_ushi/routes.py` and `/card_4_ushi/query_engine.py`

**5 Primary Endpoints:**

```
POST /api/card4/metrics
  Params: metric_type, date_range_days, filter_by
  Returns: {
    metric: string,
    value: number,
    confidence_score: 0.0-1.0,
    sources: string[],
    trend: string,
    freshness: string,
    caveat: string
  }

POST /api/card4/fraud-signals
  Params: entity_type (provider|member|claim_pattern), threshold_sigma
  Returns: {
    data: FraudSignal[],
    confidence_score: number,
    recommendation: "Escalate to Card 5 (UBADA)"
  }

POST /api/card4/data-quality
  Params: domain (enrollment|claims|provider_data)
  Returns: {
    data: {
      completeness: percent,
      accuracy: percent,
      timeliness: percent,
      audit_valid: boolean,
      cms_ready: boolean
    },
    quality_score: number
  }

GET /api/card4/governance-log
  Params: filter_by, days_back, limit
  Returns: [
    {
      timestamp: datetime,
      action: string,
      entry_json: JSONB,
      hash: string (immutable)
    }
  ]

POST /api/card4/flag-issue
  Params: issue_type, domain, title, description, justification, evidence, flagged_by
  Returns: {
    flag_id: string,
    note: "Flag created and logged to immutable audit trail"
  }

GET /api/card4/health
  Returns: {
    status: "healthy",
    card: "4 (USHI)",
    tools: 5,
    tools_available: string[]
  }
```

### Spectrum Analyzer Component (✅ IMPLEMENTED & LIVE)

**Architecture:** 3-Tier Collapsible Spectrum System

#### **Tier 1: Coherence Level**
- Single large traffic light (red/yellow/green)
- Overall system coherence percentage
- Status: COHERENT / WAVERING / FRAGMENTED
- **On click:** Shows traffic light visual (3 stacked circles, active light glows)

#### **Tier 2: Stability Strength (Equalizer)**
- 6 full-width vertical rectangles, stacked
- Layout: [Traffic Light] | [Metric Label + %] | [Progress Bar]
- Each rectangle shows one dimension:
  1. Enrollment Rate
  2. Claims Processing
  3. Data Quality
  4. Audit Trail
  5. Compliance
  6. System Stability

**On click of any rectangle:**
1. **Equalizer visual appears** (5 bars representing metric strength)
2. **URL citations displayed** with clickable links:
   - Real government sources (eMedNY, CMS, SSA, NYS DOH)
   - 42 CFR regulations
   - NIST standards
   - Each opens in new tab
3. **Calculation logic** (exact formula)
4. **Detailed breakdown** (specific numbers)

#### **Tier 3: Combined View**
- Large coherence % at top
- All 6 metrics below (same clickable rectangles)
- **On click:** Shows BOTH traffic light AND equalizer visuals
- Plain text sources (no URLs in this view)

**Visual Design:**
```
COHERENCE LEVEL
[Expand/Collapse ▶]

STABILITY STRENGTH (EQUALIZER)
[Expand/Collapse ▶]
[🟡] ENROLLMENT RATE         87.3%
    ▄▄▄▄▄▄░░ (progress bar)
[✓] CLAIMS PROCESSING         95%
    ▄▄▄▄▄▄▄░ (progress bar)
[✓] DATA QUALITY              99%
    ▄▄▄▄▄▄▄░ (progress bar)
[✓] AUDIT TRAIL              100%
    ▄▄▄▄▄▄▄░ (progress bar)
[✓] COMPLIANCE                98%
    ▄▄▄▄▄▄▄░ (progress bar)
[✓] SYSTEM STABILITY          96%
    ▄▄▄▄▄▄▄░ (progress bar)

COMBINED VIEW
[Expand/Collapse ▼]
96% Coherence
System is COHERENT across all dimensions
+ All 6 metrics
```

**Color Coding:**
- 🟢 GREEN (90-100%) - Healthy
- 🟡 YELLOW (70-89%) - Caution
- 🔴 RED (0-69%) - Critical

**Interaction Model:**
- All three sections start **collapsed (▶ icon)**
- User expands by clicking section header
- Chevron rotates to indicate expanded state (▼)

**Data Source Citations:**
- **Section 1 (Coherence Level):** Plain text source only
  - Fine print (italicized): "For detailed data sources and removable citations, go to Stability Strength (Equalizer)"
  - No URLs in this view (keeps Coherence clean)

- **Section 2 (Stability Strength):** Full URL citations with session removal
  - Each URL displayed on separate line (not pipe-separated)
  - X button next to each URL for session removal
  - Click X → "Are you sure?" confirmation modal
  - Confirmed removal → Source removed from session (sessionStorage)
  - Real government sources: eMedNY, CMS Data, State DOH, 42 CFR, NIST, OMB

- **Section 3 (Combined View):** Full URL citations with session removal
  - Same layout as Section 2 (includes Spectrum function)
  - URLs one per line with X removal buttons
  - Session removal available

**Session-Level Removal Implementation:**
- Removed sources stored in `sessionStorage.removedSources` (array of URLs)
- Removed sources filtered from display on breakdown expansion
- Removal is temporary (cleared when session ends/tab closes)
- No server calls, no permanent changes
- Each removal requires user confirmation ("Are you sure?")
- If all sources removed from a metric, shows: "*All sources removed from session*"

**Status:** ✅ LIVE on Railway with interactive Spectrum Analyzer + session source governance

### Database Integration

**Tables Used:**
- `data_ingestion_audit_log` - Immutable governance audit trail
- `programs` - Medicaid plan data (for enrollment metrics)
- `beneficiary_selections` - Enrollment decisions
- `claims` - Claims data (for processing metrics)
- `providers` - Provider data (for fraud signals)

**Immutability Enforcement:**
- All governance actions logged with hash verification
- Database triggers prevent modification/deletion of audit logs
- Timestamp immutable on creation

---

## Testing Protocol

**Query Set for QA (Carol & Selam):**

1. "What's the overall system health?" → Test metrics handler
2. "What are enrollment trends for the last 7 days?" → Test trend handler
3. "Is our data audit-ready?" → Test quality handler
4. "Any governance flags or alerts?" → Test governance handler
5. "How many members enrolled and what's the denial rate?" → Test compound query
6. "Give me a complete status report" → Test aggregation

**Expected Results:**
- ✅ Responses show real data from Railway backend
- ✅ Confidence scores included
- ✅ Data freshness indicators present
- ✅ Color-coded status boxes render correctly
- ✅ No "Offline Mode" fallbacks

**Success Criteria:**
- All 6 queries return live API data (not cached fallback)
- Response times < 2 seconds
- Confidence scores realistic (0.8-0.99 range)
- No CORS errors in browser console

**User 3's perspective:** "Are operations running smoothly? Are we within budget?"

**Card 4 shows him:** Processing volume + error rate + payment status + budget health. He doesn't need fraud data or compliance metrics.

**One system. Three voices. Each sees only what they need.**

---

End of Card 4 Architecture (DR)