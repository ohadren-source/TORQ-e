# TORQ-E Card 5: Fraud Detection & Investigation Architecture
## Internal Design Repository (DR)

---

## Overview

**Card 5** is the analytical and investigative layer that detects fraud patterns, flags suspicious claims, and supports investigators in building prosecution-ready cases.

Card 5 operates in two modes:
1. **Automated Detection** - Real-time flagging of suspicious claims based on multi-dimensional fraud signals
2. **Investigation Support** - Tools for investigators to explore networks, gather evidence, document cases

**Core Principle:** Actionable intelligence, not raw data. A flagged claim should include: What happened, why it's suspicious, what evidence exists, what the next step is.

**QD:** The system is constantly detecting and investigating. Fraud signals flow in real-time. Investigators act on evidence continuously.

---

## Data Model

### Fraud Signal (Primary Detection Unit)

```
ClaimFraudSignal {
  id: string (unique fraud flag)
  timestamp: datetime (immutable)
  claim_id: string (which claim is suspicious?)
  
  // Dimensional Analysis
  fraud_dimensions: {
    billing_anomaly: {
      baseline_cost_member: number
      current_claim_cost: number
      deviation_percent: number (how far from normal?)
      severity: enum (NORMAL, UNUSUAL, EXTREME)
      confidence: percent (0-100)
    }
    
    provider_deviation: {
      peer_average_billing: number
      this_provider_billing: number
      deviation_std_dev: number (how many standard deviations?)
      severity: enum (NORMAL, OUTLIER, EXTREME_OUTLIER)
      confidence: percent
    }
    
    member_cycling: {
      services_last_30_days: number
      typical_frequency_for_diagnosis: number
      frequency_anomaly_percent: number
      severity: enum (NORMAL, ELEVATED, EXCESSIVE)
      confidence: percent
    }
    
    network_clustering: {
      related_providers: [string] (other providers billing this member)
      related_members: [string] (other members with this provider combo)
      cluster_strength: number (0-100, how tight is this relationship?)
      known_kickback_pattern: boolean
      confidence: percent
    }
    
    temporal_spike: {
      normal_daily_volume_time: number (claims at this time of day)
      current_volume: number
      spike_percent: number
      is_during_weekend: boolean (claims on weekends: unusual)
      is_after_hours: boolean
      confidence: percent
    }
  }
  
  overall_fraud_risk: number (0-100)
  
  // Why This is Flagged
  primary_reason: string ("billing anomaly detected")
  secondary_reasons: [string] (["provider deviation", "member cycling"])
  human_readable_explanation: string (
    "This claim is 340% higher than this member's typical cost. The provider is "
    "an outlier (top 5% billing). The member cycled to this provider very frequently. "
    "Network analysis shows this provider + lab combination bills together "
    "90% of the time (vs peer average 15%)."
  )
  
  // Cross-State & Historical
  historical_pattern: {
    same_provider_flagged_in_states: [string] (CA, TX, FL)
    same_member_in_states: [string]
    similar_pattern_claims: [string] (claim IDs with same signature)
    days_occurring: number (how long has this been happening?)
    claim_count_in_pattern: number
    total_amount: number
  }
  
  // Investigation Status
  case_status: enum (
    FLAGGED,           // Just detected, awaiting triage
    UNDER_INVESTIGATION, // Assigned to investigator
    REFERRED_TO_PROSECUTION, // Evidence sufficient
    RESOLVED,          // Case closed (resolved or no fraud)
    DISMISSED          // False positive
  )
  case_id: string (reference to investigation case if applicable)
  
  // Evidence Package
  evidence: {
    claim_history: [Claim] (last 12 months for this member)
    provider_history: [Claim] (last 12 months for this provider)
    network_connections: [Provider] (other providers in network)
    member_access_timeline: [Event] (member's visit history)
  }
  
  audit_trail: {
    created_at: timestamp
    detected_by: string (algorithm name)
    reviewed_by: string (analyst, if reviewed)
    last_updated: timestamp
    all_actions: immutable log
  }
}
```

### Investigation Case

```
InvestigationCase {
  id: string
  case_name: string ("Potential Kickback: Dr. Johnson + PathLabs")
  allegation_type: enum (
    KICKBACK_SUSPECTED,
    UPCODING,
    DUPLICATE_BILLING,
    UNBUNDLING,
    BILLING_FOR_SERVICES_NOT_PROVIDED,
    BENEFICIARY_FRAUD,
    OTHER
  )
  
  // Scope
  initial_findings: string
  hypothesis: string ("Dr. Johnson receives undisclosed payments from PathLabs")
  
  // Evidence Collection
  claims_involved: [ClaimFraudSignal] (all flagged claims in this case)
  total_amount_involved: number
  
  // Investigation Timeline
  created_at: timestamp
  assigned_to: string (investigator name)
  stage: enum (
    INTAKE,           // Just created
    EVIDENCE_GATHERING, // Collecting evidence
    ANALYSIS,         // Analyzing patterns
    LEGAL_REVIEW,     // Prosecutor reviewing
    REFERRED,         // Referred to DOJ
    PROSECUTION,      // In prosecution
    RESOLVED          // Case closed
  )
  
  // Multi-State Coordination
  same_pattern_in_states: [string] (CA, TX detected same network)
  federal_coordination: boolean (is this a federal case?)
  mfcu_coordinating: [string] (which state MFCUs?)
  
  // Evidence Status
  evidence_confidence: percent (0-100, how strong is the case?)
  ready_for_prosecution: boolean
  prosecution_package: {
    summary: string
    exhibits: [string] (claim logs, provider comparisons, etc.)
    legal_analysis: string (prepared by prosecutor)
  }
  
  // Audit Trail
  audit_trail: {
    case_events: immutable log of all case activity
    who_accessed_when: immutable
  }
}
```

### Network Graph (Relationship Detection)

```
NetworkNode {
  id: string
  type: enum (PROVIDER, MEMBER, LAB, PHARMACY)
  entity_id: string
  
  connections: [
    {
      to_node_id: string
      relationship_type: enum (
        BILLS_TOGETHER,     // provider + lab on same claims
        REFERS_TO,          // provider refers to lab
        DUPLICATE_CLAIM,    // same claim billed twice
        TIMING_CORRELATED   // patterns happen at same time
      )
      strength: percent (how many claims? how consistent?)
      frequency: number
      first_seen: date
      last_seen: date
    }
  ]
  
  fraud_risk_score: number (0-100, based on connections)
  is_known_fraud_indicator: boolean
}

NetworkGraph {
  nodes: [NetworkNode]
  edges: [NetworkNodeConnection]
  
  // Detected Clusters
  clusters: [
    {
      cluster_id: string
      nodes_in_cluster: [string] (provider IDs, member IDs, lab IDs)
      cluster_type: enum (KICKBACK_RING, UPCODING_NETWORK, DUPLICATE_BILLING_SCHEME)
      strength: percent (how suspicious?)
      claims_involved: number
      total_amount: number
    }
  ]
}
```

---

## User Workflows: "A Day in the Life"

### OMIG Investigator - Wednesday

**9:00 AM:** Logs into Card 5 dashboard.

**Sees (Dashboard View):**

**High-Risk Claims Flagged Overnight:**
```
CLAIM #1 - Potential Kickback Network
├─ Claim ID: CLM-2026-045782
├─ Fraud Risk: 94% (RED)
├─ Reason: Member referred to same lab 23 times in 30 days
│  ├─ Typical frequency: 2-3 times/month
│  ├─ Provider deviation: Top 5% of providers (billing outlier)
│  └─ Lab deviation: This lab receives 340% more referrals from this provider than peer average
├─ Network: Provider + Lab + Member cluster detected
│  ├─ Same pattern in CA: 45 claims
│  ├─ Same pattern in TX: 28 claims
│  └─ Potential multi-state ring
├─ Evidence Package: [VIEW]
│  ├─ Claim history (12 months)
│  ├─ Provider billing comparison
│  ├─ Network visualization
│  ├─ Timeline of member visits
│  └─ Audit trail (immutable)
├─ Recommendation: CREATE INVESTIGATION CASE
└─ Action: [CREATE CASE]

CLAIM #2 - Upcoding Pattern
├─ Claim ID: CLM-2026-045789
├─ Fraud Risk: 78% (YELLOW)
├─ Reason: Office visits consistently billed as specialist visits
│  ├─ Provider office visit rate: 99% specialist codes (vs peer avg 15%)
│  ├─ Member impact: Charges higher copays for specialist (conspiracy?)
│  └─ Cost difference: $150/visit overcharge
├─ Duration: 3 months (consistent pattern)
├─ Case Status: UNDER INVESTIGATION
│  ├─ Investigator: Jane Smith
│  ├─ Created: 2026-04-10
│  ├─ Evidence confidence: 78%
│  └─ Need 2 more months to reach prosecution threshold
└─ Action: [MONITOR] or [ADD TO EXISTING CASE]

CLAIM #3 - Duplicate Billing
├─ Claim ID: CLM-2026-045801
├─ Fraud Risk: 99% (RED)
├─ Reason: Same service billed twice (2 days apart, same provider)
│  ├─ Service: Office visit
│  ├─ Amount: $1,600 per claim (total $3,200 overcharged)
│  ├─ Confidence: 99% (duplicate detection is very certain)
├─ Case Status: REFERRED TO PROSECUTION
│  ├─ Amount recoverable: $3,200
│  ├─ Prosecution stage: Legal review
│  └─ Expected resolution: 30 days
└─ Action: [MONITOR PROSECUTION]
```

**9:30 AM:** Creates investigation case for Claim #1

```
CREATING CASE:
├─ Case Name: "Potential Kickback Network: Dr. Johnson + PathLabs"
├─ Allegation Type: KICKBACK_SUSPECTED
├─ Initial Findings: "Provider refers 340% more to specific lab; member cycles unusually"
├─ Multi-State: CA (45 claims), TX (28 claims) detected
├─ Hypothesis: "Provider receives undisclosed payments from lab for referrals"
├─ Claims to Include: [CLM-2026-045782, CLM-2026-045750, CLM-2026-045701, ...]
├─ Total Amount: $487,000
├─ Evidence Confidence: 87%
├─ Ready for Prosecution: No (need additional evidence)
└─ Created: CASE-2026-001234
```

**10:00 AM:** Deep dive into Claim #1 evidence

```
EVIDENCE PACKAGE - Claim CLM-2026-045782:

1. CLAIM HISTORY (Member's last 12 months):
   ├─ Total visits to Dr. Johnson: 23 (Jan-Mar: heavy clustering)
   ├─ Total lab tests from PathLabs: 23 (exact 1:1 correlation)
   ├─ No other providers visited: 0 other specialist visits
   ├─ No other labs used: 0 other lab providers
   └─ Pattern: Every single Dr. Johnson visit → immediate PathLabs test
   
2. PROVIDER BILLING COMPARISON:
   ├─ Dr. Johnson vs. peer group (cardiology):
   │  ├─ Dr. Johnson PathLabs referrals: 340 per 1000 patients
   │  ├─ Peer average PathLabs referrals: 100 per 1000 patients
   │  ├─ Deviation: 240% above peers (extreme outlier)
   │  └─ Confidence: 92%
   │
   ├─ Dr. Johnson vs. peer group (test quantity):
   │  ├─ Dr. Johnson avg tests per visit: 3.4
   │  ├─ Peer average: 1.2 tests per visit
   │  └─ Deviation: 183% above peers
   
3. NETWORK VISUALIZATION:
   ```
        Dr. Johnson (Provider)
              ↓ refers to
        PathLabs (Lab)
              ↓ results to
        Members A, B, C, D, E... (23 members, same pattern)
   
   Relationship strength: VERY HIGH (100% correlation)
   Known kickback indicator: SUSPECTED (highly unusual exclusive relationship)
   ```
   
4. MEMBER ACCESS TIMELINE:
   ├─ 2026-01-05: Member visits Dr. Johnson → same day PathLabs referral
   ├─ 2026-01-12: Member visits Dr. Johnson → same day PathLabs referral
   ├─ 2026-01-19: Member visits Dr. Johnson → same day PathLabs referral
   ├─ ... (pattern continues without exception)
   └─ Probability of coincidence: <0.1% (not random)
   
5. CROSS-STATE ANALYSIS:
   ├─ Same Dr. Johnson in CA: 45 claims with same pattern
   ├─ Same Dr. Johnson in TX: 28 claims with same pattern
   ├─ Total ring size: 96+ claims, $487K+
   ├─ Coordination required: YES (multi-state task force)
   └─ Federal involvement: LIKELY (interstate fraud ring)

6. AUDIT TRAIL (Who Saw This, When):
   ├─ 2026-04-25 09:00 - Fraud detection algorithm flagged
   ├─ 2026-04-25 09:05 - OMIG analyst Jane Smith reviewed
   ├─ 2026-04-25 09:15 - Case created (CASE-2026-001234)
   ├─ 2026-04-25 09:30 - Evidence package accessed
   └─ All accesses immutable and documented
```

**11:00 AM:** Coordinates with other states

```
MULTI-STATE COORDINATION:

Task: Notify CA and TX MFCUs about related pattern

├─ CA MFCU:
│  ├─ Same provider: Dr. Johnson (NPI: 1234567890)
│  ├─ Same lab: PathLabs (ID: PATH-001)
│  ├─ Claims found: 45
│  ├─ Total amount: $156,000
│  └─ Status: Information shared, waiting for CA to open case
│
├─ TX MFCU:
│  ├─ Same provider: Dr. Johnson (NPI: 1234567890)
│  ├─ Same lab: PathLabs (ID: PATH-001)
│  ├─ Claims found: 28
│  ├─ Total amount: $98,000
│  └─ Status: Information shared, waiting for TX to open case

Task: Federal Coordination
├─ Potential federal case (multi-state, >$200K)
├─ Should contact: FBI Health Care Fraud Task Force
├─ Documentation required: [Ready for transmission]
└─ Recommendation: Escalate to DOJ for federal prosecution
```

**2:00 PM:** Monitors existing investigation cases

```
ACTIVE CASES:

CASE-2026-001232 (Upcoding Network):
├─ Duration: 2 weeks
├─ Status: UNDER INVESTIGATION
├─ Claims: 47
├─ Amount: $89,000
├─ Progress: Evidence gathering (need 2 more weeks)
├─ Next action: Subpoena provider billing records
└─ Assigned to: Me (Jane Smith)

CASE-2026-001233 (Duplicate Billing):
├─ Duration: 3 weeks
├─ Status: REFERRED TO PROSECUTION
├─ Claims: 12
├─ Amount: $87,000
├─ Progress: Prosecutor reviewing evidence (70% confident)
├─ Next action: Legal review meeting (tomorrow)
└─ Expected resolution: 30 days

CASE-2026-001234 (Kickback Ring - NEW):
├─ Duration: <1 hour (just created)
├─ Status: INTAKE
├─ Claims: 96+ (multi-state)
├─ Amount: $487,000
├─ Progress: Evidence package complete, network analysis complete
├─ Next action: Multi-state coordination (in progress)
└─ Assigned to: Me (Jane Smith) + Task force (CA, TX, federal)
```

**5:00 PM:** Prepares prosecution package for Case #1233

```
PROSECUTION PACKAGE - CASE-2026-001233:

Case: Duplicate Billing Fraud
Amount: $87,000 (12 claims, same pattern)

EVIDENCE SUMMARY:
• 12 claims with identical structure
  ├─ Same provider
  ├─ Same member
  ├─ Same service code
  ├─ Same amount
  ├─ Different claim IDs
  ├─ Billed 2-5 days apart
  └─ Confidence: 99% (this is fraud, not coincidence)

EXHIBITS:
├─ Claim details (claim IDs, amounts, dates)
├─ Provider comparison (is this provider an outlier?)
├─ Timeline (did member actually receive service twice?)
├─ Member access records (was member at provider twice in 2-day window? NO)
├─ Audit trail (immutable proof of submission)
└─ Legal analysis (prosecutor's assessment)

RECOMMENDATION:
├─ Fraud classification: CONFIRMED
├─ Prosecution readiness: READY
├─ Recommended action: Refer to DOJ for criminal prosecution
├─ Recovery amount: $87,000 (fully recoverable)
└─ Confidence level: 99%

STATUS: READY FOR PROSECUTION ✓
```

---

## Technical Architecture

### Real-Time Detection Pipeline

```
Claim arrives
    ↓
[1] Validate & Normalize
    - Check format
    - Verify eligibility
    - Standard codes
    ↓
[2] Immediate Red Flags
    - Duplicate detection
    - Format errors
    - Obvious errors
    ↓
[3] Multi-Dimensional Analysis
    - Billing anomaly (vs member history)
    - Provider deviation (vs peer group)
    - Member cycling (vs diagnosis)
    - Network clustering (new connections?)
    - Temporal spike (unusual timing?)
    ↓
[4] Score Combination
    - Fraud Risk = weighted combination of all dimensions
    - Confidence = statistical confidence in measurement
    - Color = RED (>75) | YELLOW (25-74) | GREEN (<25)
    ↓
[5] Threshold Decision
    - If fraud_risk > 75 AND confidence > 70: FLAG
    - If fraud_risk > 50 AND confidence > 85: FLAG
    - Otherwise: MONITOR (add to trending analysis)
    ↓
[6] Output
    - Create ClaimFraudSignal
    - Send to Card 4 (governance sees summary)
    - Alert investigator if high-risk
    - Log immutably
    - Return to claims processing (claim still pays, but flagged)
```

### Investigation Support Tools

**Network Visualization:**
```
- Interactive graph showing provider → lab → member relationships
- Color coded by fraud risk (red/yellow/green)
- Clickable nodes to drill into details
- Timeline animation (show relationships appearing over time)
- Cross-state overlay (show same network in other states)
```

**Evidence Compilation:**
```
- Automated package generation from flagged claims
- One-click export to prosecution format
- Signature matching (find similar patterns)
- Timeline reconstruction (when did each action happen?)
- Legal admissibility checking (is this evidence usable in court?)
```

**Case Management:**
```
- Case creation from fraud flags
- Evidence tracking (what's been collected?)
- Investigator assignment
- Progress stage management
- Multi-state coordination
- Prosecution referral
- Federal escalation
- Case resolution tracking
```

---

## API Specification

```
GET /api/card5/flagged-claims
  Query:
    - risk_level (HIGH | MEDIUM | ALL)
    - time_range (24h | 7d | 30d)
    - state (optional)
    - limit (10, 50, 100)
  Returns: [ClaimFraudSignal]

POST /api/card5/investigation-case
  Payload: {
    fraud_signal_id: string,
    case_name: string,
    allegation_type: string,
    initial_findings: string
  }
  Returns: InvestigationCase

GET /api/card5/case/{case_id}
  Returns: InvestigationCase (full details with evidence package)

GET /api/card5/network-graph
  Query:
    - entity_id: string (provider or member)
    - entity_type: enum (PROVIDER | MEMBER)
  Returns: NetworkGraph (visualization data)

POST /api/card5/case/{case_id}/evidence-package
  Query:
    - format: enum (INVESTIGATION | PROSECUTION)
  Returns: Evidence package suitable for investigators or prosecutors

GET /api/card5/cases
  Query:
    - status (INTAKE | EVIDENCE_GATHERING | REFERRED | RESOLVED)
    - assigned_to: string
  Returns: [InvestigationCase]

POST /api/card5/case/{case_id}/referral
  Payload: {
    referral_type: enum (DOJ | FEDERAL_TASK_FORCE | MFCU_OTHER_STATE),
    prosecutor_notes: string
  }
  Returns: Referral confirmation
```

---

## Fraud Detection Formulas

### Billing Anomaly Score

```
baseline_cost = member's average claim cost (last 12 months)
current_cost = this claim's cost
deviation_percent = abs((current_cost - baseline_cost) / baseline_cost) * 100

if deviation_percent > 300:
    score = 95  (extreme anomaly)
elif deviation_percent > 150:
    score = 70  (high anomaly)
elif deviation_percent > 50:
    score = 40  (moderate anomaly)
else:
    score = 10  (normal)
```

### Provider Deviation Score

```
peer_average = median billing for same specialty, same region
this_provider = provider's average billing
std_dev = standard deviation of peer group

z_score = (this_provider - peer_average) / std_dev

if z_score > 3:
    score = 95  (extreme outlier, top 0.1%)
elif z_score > 2:
    score = 70  (major outlier, top 5%)
elif z_score > 1:
    score = 40  (moderate outlier, top 15%)
else:
    score = 10  (normal range)
```

### Member Cycling Score

```
expected_frequency = frequency for this diagnosis (e.g., 2-3 visits/month)
actual_frequency = this member's frequency in past 30 days
cycle_ratio = actual_frequency / expected_frequency

if cycle_ratio > 10:
    score = 95  (10x normal frequency)
elif cycle_ratio > 5:
    score = 70  (5x normal)
elif cycle_ratio > 2:
    score = 40  (2x normal)
else:
    score = 10  (normal)
```

### Network Anomaly Score

```
cluster_strength = (claims_in_cluster / total_claims_by_provider) * 100

if cluster_strength > 80:  // provider sends 80%+ to same lab
    score = 90  (extreme concentration)
elif cluster_strength > 50:
    score = 60  (high concentration)
elif cluster_strength > 20:
    score = 30  (moderate concentration)
else:
    score = 10  (normal distribution)

known_fraud_pattern = lookup_known_patterns(provider, lab, member)
if known_fraud_pattern exists:
    score += 20  (boost if matches known scheme)
```

### Temporal Spike Score

```
normal_daily_volume = average claims at this time of day
current_volume = claims in this time window
spike_ratio = current_volume / normal_daily_volume

if spike_ratio > 5:
    score = 90  (5x spike)
elif spike_ratio > 2:
    score = 60  (2x spike)
elif spike_ratio > 1.5:
    score = 30  (1.5x spike)
else:
    score = 10  (normal)

if is_weekend or is_afterhours:
    score += 20  (boost for unusual timing)
```

### Overall Fraud Risk

```
fraud_risk = (
    0.25 * billing_anomaly_score +
    0.25 * provider_deviation_score +
    0.20 * member_cycling_score +
    0.20 * network_anomaly_score +
    0.10 * temporal_spike_score
)

confidence = min(individual_confidence_scores)
// Use lowest confidence (weakest link)

if fraud_risk > 75 AND confidence > 70:
    FLAG as HIGH-RISK
elif fraud_risk > 50 AND confidence > 85:
    FLAG as MEDIUM-RISK
else:
    MONITOR (track in trending analysis)
```

---

## "Know Your Audience" Application

**OMIG Investigator's perspective:** "Which claims are actually fraudulent? What's my evidence? Can I win in court?"

**Card 5 shows her:** Fraud-flagged claims with fraud dimensions + evidence confidence + network analysis + prosecution-ready documentation.

She doesn't need system stability metrics, budget forecasts, or governance compliance data.

**One system. Different user sees only fraud analysis.**

---

## Metrics & Monitoring

**What we measure:**

- Fraud detection rate: How many actual frauds are we catching?
- False positive rate: How many flags are incorrectly flagged?
- Time-to-prosecution: How long from flag to prosecution referral?
- Recovery amount: How much fraud are we preventing/recovering?
- Multi-state coordination: How many cases span multiple states?
- Federal escalations: How many cases go federal?
- Case resolution rate: What % of cases are successfully prosecuted?

---

End of Card 5 Architecture (DR)
