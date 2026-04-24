# ClaudeShannon++ Confidence Scoring Framework
## How TORQ-e Weights Data Sources, Signals, and Determines Clarity

**For:** Engineers, Data Analysts, State Decision-Makers  
**Based on:** Code in `card_1_umid/confidence.py` and `card_2_upid/fraud_detection.py`  
**Version:** 1.0  
**Date:** April 24, 2026

---

## Executive Summary

TORQ-e uses a signal-processing framework called **ClaudeShannon++** to determine how much we should trust any given piece of information. This framework answers a critical question:

> **"How confident are we in this eligibility determination / fraud assessment?"**

The answer is never binary (yes/no). It's probabilistic (0.0 to 1.0), with clear reasoning for every score.

---

## Part 1: The Core Formula

### ClaudeShannon++ Base Equation

```
CONFIDENCE(source) = [Quality/Quantity] × [(Understanding - Dependence - Misunderstanding - Unknown) / Time]
```

Breaking it down:

| Component | Meaning | Range |
|-----------|---------|-------|
| **Quality** | How authoritative is this source? (inherent credibility) | 0.10–0.98 |
| **Quantity** | How complete is the data? (do we have all needed fields?) | 0.0–1.0 |
| **Understanding** | Do we comprehend what the data means? | 0.0–1.0 |
| **Dependence** | How much do we depend on external/fragile systems? | 0.0–1.0 |
| **Misunderstanding** | Room for interpretation error? | 0.0–1.0 |
| **Unknown** | What critical information is missing? | 0.0–1.0 |
| **Time** | How old is the data? (freshness factor) | 0.5–1.0 |

### Simplified Form for Medicaid

For practical implementation in TORQ-e, we simplify to:

```
CONFIDENCE = Source Quality × Data Completeness × Freshness Factor
```

Example:
```
State Medicaid Database (real-time, complete)
= 0.98 (source quality) × 1.0 (complete) × 1.0 (fresh)
= 0.98 confidence
```

---

## Part 2: Data Source Quality Hierarchy

TORQ-e ranks all data sources from most to least authoritative:

```
┌─────────────────────────────────────────────────────────┐
│  OFFICIAL_STATE_SYSTEM        0.98                      │
│  Direct query to state Medicaid database                │
│  ✓ Authoritative | ✓ Verified | ✓ Current               │
├─────────────────────────────────────────────────────────┤
│  FEDERAL_DATABASE             0.95                      │
│  SSA, IRS official databases                            │
│  ✓ Government verified | ~ May be delayed 1-2 weeks    │
├─────────────────────────────────────────────────────────┤
│  STATE_PUBLISHED              0.90                      │
│  State-published documents/public data                  │
│  ✓ Official | ~ Published frequency varies              │
├─────────────────────────────────────────────────────────┤
│  PLAN_OFFICIAL                0.85                      │
│  MCO (insurance company) official member services       │
│  ✓ Direct source | ~ Depends on MCO accuracy            │
├─────────────────────────────────────────────────────────┤
│  PROVIDER_REPORTED            0.75                      │
│  Healthcare provider reports (doctors, hospitals)       │
│  ~ Self-reported | ~ Subject to coding errors           │
├─────────────────────────────────────────────────────────┤
│  HOUSEHOLD_ENROLLMENT         0.70                      │
│  Household-level data (needs individual confirmation)   │
│  ~ Proxy information | ⚠ Needs verification             │
├─────────────────────────────────────────────────────────┤
│  THIRD_PARTY                  0.60                      │
│  Clearinghouse, intermediary, aggregated data           │
│  ⚠ Secondhand | ⚠ Latency and translation              │
├─────────────────────────────────────────────────────────┤
│  MEMBER_REPORTED              0.50                      │
│  Member self-reported (unverified)                      │
│  ⚠ Unverified | ⚠ Subject to memory/intent             │
├─────────────────────────────────────────────────────────┤
│  SOCIAL_MEDIA / RUMOR         0.10                      │
│  Social media, rumors, unverified claims                │
│  ✗ Unreliable | ✗ Not a legitimate source               │
└─────────────────────────────────────────────────────────┘
```

**Key Principle:** Quality score reflects **epistemic authority**, not judgment of the person reporting. A doctor's credentials matter; a member's honesty doesn't determine their quality score (though it affects whether we believe *this particular member*).

---

## Part 3: Completeness Factor

**Question:** "Do we have all the information we need?"

### For Member Eligibility:

Required fields:
- Name ✓
- Date of Birth ✓
- Social Security Number (or alternative identifier) ✓
- Household size ✓
- Monthly household income ✓
- Citizenship/immigration status ✓

| Completeness | Score | Meaning |
|--------------|-------|---------|
| All 6 fields present | 1.0 | Complete |
| 5 fields present, 1 missing non-critical | 0.8 | Mostly complete |
| 4 fields present, 2 missing (some critical) | 0.5 | Significantly incomplete |
| 3 or fewer fields | 0.2 | Critical data gaps |
| Empty/null response | 0.0 | No data |

**Example:**
```
State Medicaid system returns: name, DOB, SSN, household size, income
Missing: Citizenship status
Completeness = 0.8 (5 of 6 fields)
```

### For Provider Enrollment:

Required fields:
- NPI (National Provider Identifier) ✓
- Legal name ✓
- License type & state ✓
- Office address ✓
- Specialty/taxonomy ✓

| Completeness | Score |
|--------------|-------|
| All 5 fields | 1.0 |
| 4 fields (1 minor missing) | 0.85 |
| 3 fields (2 missing) | 0.5 |
| <3 fields | 0.0 |

---

## Part 4: Freshness Factor

**Question:** "How old is this data?"

Data degrades in value over time. Income from 2 years ago isn't useful; eligibility from yesterday is gold.

```
Age of Data        | Freshness Factor | Use Case
─────────────────────────────────────────────────────────
Real-time (0 min)  | 1.0              | Claim submission, eligibility check
< 24 hours         | 0.95             | Recent enrollment, billing
< 7 days           | 0.85             | Routine member check
< 30 days          | 0.70             | Recertification checking
< 6 months         | 0.50             | Historical analysis
> 6 months         | 0.30             | Fraud pattern detection only
> 1 year           | 0.10             | Historical research only
> 2 years          | 0.0              | Unusable for current decisions
```

**Why this matters:**

- Member asks: "Am I eligible?" 
  - If we use 6-month-old data: confidence drops 50%
  - They might have had job change, income shift, life event
  - Freshness is critical for real-time eligibility

- Analyst asks: "Is this provider's pattern normal?"
  - 30-day-old claims data is fine for pattern detection
  - Freshness matters less; we're looking for trends, not exact values

---

## Part 5: Example Scoring — Member Eligibility

### Scenario: John queries "Am I eligible?"

**Step 1: Query all sources**
- State Medicaid database: John found, current enrollment, all fields ✓
- SSA Wage records: John found, employed, matches state income ✓
- Household enrollment: John found as family head, 4-person household ✓

**Step 2: Score each source**

**Source 1: State Medicaid**
- Quality: 0.98 (official government system)
- Completeness: 1.0 (all fields present, recent updates)
- Freshness: 1.0 (updated this week)
- **Confidence = 0.98 × 1.0 × 1.0 = 0.98**

**Source 2: SSA Wage Records**
- Quality: 0.95 (federal database)
- Completeness: 0.8 (employment verified, but limited detail)
- Freshness: 0.85 (SSA data 10 days old, normal reporting lag)
- **Confidence = 0.95 × 0.8 × 0.85 = 0.646**

**Source 3: Household Enrollment**
- Quality: 0.70 (household-level, needs individual confirmation)
- Completeness: 0.9 (household info complete)
- Freshness: 0.95 (recent household update)
- **Confidence = 0.70 × 0.9 × 0.95 = 0.598**

**Step 3: Calculate consensus across all sources**

Three sources agree: John is eligible.
- Average confidence: (0.98 + 0.646 + 0.598) / 3 = 0.741
- Agreement: All three say "eligible" = perfect agreement (agreement score = 1.0)
- **Consensus = (0.741 × 0.6) + (1.0 × 0.4) = 0.444 + 0.4 = 0.844**

**Step 4: Determine confidence level**

0.844 = **HIGH CONFIDENCE**

**Step 5: Generate user-facing response**

| Audience | Response |
|----------|----------|
| **Member John** | "You should be covered. Check your plan for specific details." |
| **Provider** | "Member is eligible (confidence: 0.84). Claim will be processed." |
| **Analyst** | [Full breakdown with all source scores and reasoning] |

---

## Part 6: Example Scoring — Fraud Detection

### Scenario: Provider Dr. Smith shows suspicious pattern

**Signals Observed:**
1. Billing volume is 3x peer average
2. All patients from single nursing home
3. Nursing home staff say services didn't occur
4. Prior OIG exclusion in different state
5. Medical records don't support claims

**Step 1: Score each signal**

**Signal 1: Billing Volume (3x average)**
- Quality of data: 0.95 (audited claims database)
- Completeness: 1.0 (full volume captured)
- Freshness: 0.95 (current month billing)
- Confidence in signal strength: 0.95 × 1.0 × 0.95 = **0.903**
- Interpretation: "High confidence this billing pattern is real"

**Signal 2: Single nursing home source**
- Quality: 0.85 (plan network data, MCO reporting)
- Completeness: 0.9 (patient list mostly complete)
- Freshness: 0.90 (quarterly updates)
- Confidence: 0.85 × 0.9 × 0.90 = **0.688**
- Interpretation: "Medium confidence in patient concentration"

**Signal 3: Nursing home denial**
- Quality: 0.90 (direct source, but need verification)
- Completeness: 0.8 (nursing home staff reports specific dates)
- Freshness: 1.0 (reported same day)
- Confidence: 0.90 × 0.8 × 1.0 = **0.72**
- Interpretation: "Medium-high confidence in denial"

**Signal 4: OIG history**
- Quality: 0.98 (federal OIG database)
- Completeness: 1.0 (clear prior exclusion)
- Freshness: 1.0 (permanent exclusion record)
- Confidence: 0.98 × 1.0 × 1.0 = **0.98**
- Interpretation: "Very high confidence in prior fraud history"

**Signal 5: Medical records don't match**
- Quality: 0.90 (medical record documentation)
- Completeness: 0.7 (some records missing, but sample shows pattern)
- Freshness: 0.95 (recent visits)
- Confidence: 0.90 × 0.7 × 0.95 = **0.598**
- Interpretation: "Medium confidence in lack of documentation"

**Step 2: Calculate coherence**

| Signal | Points to Fraud? |
|--------|------------------|
| 1. High volume | ✓ Yes |
| 2. Single nursing home | ✓ Yes |
| 3. Nursing home denial | ✓✓ YES (strongest) |
| 4. OIG history | ✓✓ YES (strongest) |
| 5. Medical records mismatch | ✓ Yes |

**Coherence = 5/5 signals support fraud conclusion = 100%**

**Step 3: Calculate overall fraud risk**

```
Fraud Risk Score = Average Signal Confidence × Coherence
                 = (0.903 + 0.688 + 0.72 + 0.98 + 0.598) / 5 × 1.0
                 = 0.778 × 1.0
                 = 0.778 (rounded to 78/100)
```

**Step 4: Risk categorization**

78/100 = **HIGH RISK (investigate within 1 week)**

**Action Taken:**
- ⚠ Flag provider for investigation
- ✓ Continue processing existing claims (normal pipeline)
- 📋 Assign to analyst for detailed review
- ⏸ If fraud confirmed, halt future claims and recover overpayment

---

## Part 7: Tiered Reporting (Different Audiences See Different Detail)

### For Members

```
┌─────────────────────────────────────┐
│      ELIGIBILITY STATUS             │
├─────────────────────────────────────┤
│  ✓ ELIGIBLE                         │
│                                     │
│  You should be covered. Check your  │
│  plan for specific details.         │
└─────────────────────────────────────┘
```

**What members DON'T see:** Detailed confidence scores, source breakdowns, methodology.

**Why:** Plain language builds trust. Technical detail confuses. Confidence score might suggest false precision ("84% eligible" sounds weird).

---

### For Providers

```
┌───────────────────────────────────────────────────┐
│    MEMBER ELIGIBILITY CHECK                       │
├───────────────────────────────────────────────────┤
│  Confidence Level: HIGH (0.84)                    │
│                                                   │
│  Key Factors:                                     │
│  • Recent state enrollment verification ✓        │
│  • Income matches federal records ✓              │
│  • No gaps in coverage ✓                         │
│                                                   │
│  Action: Proceed with claim submission           │
│  No action required from provider                │
└───────────────────────────────────────────────────┘
```

**What providers see:** Summary + key factors influencing decision. Actionable info.

**Why:** Providers need to know WHY the system made a decision, enough to troubleshoot if there's a problem.

---

### For Data Analysts

```json
{
  "score": 0.84,
  "level": "HIGH",
  "components": {
    "source_quality": 0.98,
    "completeness": 1.0,
    "freshness": 1.0
  },
  "signals": [
    {
      "type": "source_agreement",
      "sources": 3,
      "average": 0.741,
      "agreement": 1.0,
      "consensus": 0.844
    },
    {
      "source": "STATE_MEDICAID",
      "quality": 0.98,
      "completeness": 1.0,
      "freshness": 1.0,
      "confidence": 0.98
    },
    // ... (full breakdown)
  ]
}
```

**What analysts see:** Everything. Full transparency. Code-level detail.

**Why:** Analysts need to audit the system, catch errors, understand edge cases.

---

## Part 8: When Confidence is Low: Escalation & Caveats

### Low Confidence (<0.60)

When confidence is below 0.60, TORQ-e DOES NOT GUESS. Instead:

**For Members:**
```
⚠️ We cannot confirm your coverage. 
Contact your caseworker or the Medicaid office.

Phone: 1-800-541-2831
Hours: Monday–Friday, 8 AM–5 PM

Why can't we confirm?
• Your income information is older than 6 months
• Your household size changed recently
• Your citizenship status requires manual review
```

**For Providers:**
```
⚠️ Cannot verify member eligibility
Action required: Do NOT submit claim automatically
Next steps:
1. Call member to confirm coverage
2. Contact MCO directly
3. Member can verify at TORQ-e portal
```

**For Analysts:**
```json
{
  "confidence": 0.38,
  "level": "LOW",
  "caveats": [
    "CRITICAL: Review with caseworker before approval",
    "Application status is PENDING (not approved)",
    "Income not recently verified",
    "No supporting documents provided"
  ]
}
```

### Critical Confidence (<0.40)

Automatic escalation to human review. No claim processing, no eligibility determination. Period.

---

## Part 9: Common Pitfalls & How ClaudeShannon++ Prevents Them

### Pitfall 1: Overconfidence in Single Source

**Wrong approach:**
```
"State Medicaid says John is eligible → John is eligible (confidence 1.0)"
```

**Why it fails:** One source can be wrong, outdated, or compromised.

**ClaudeShannon++ approach:**
```
State Medicaid (0.98) + SSA check (0.95) + Household (0.70)
→ Consensus (0.844)
→ Medium-high confidence, not absolute
→ If SSA contradicts state, confidence drops
```

---

### Pitfall 2: Trusting Old Data

**Wrong approach:**
```
"We verified this 2 years ago → Still valid today"
```

**Why it fails:** People's circumstances change. Income, address, family status, eligibility.

**ClaudeShannon++ approach:**
```
Source quality = 0.95
Data age = 2 years
Freshness factor = 0.0 (unusable)
Confidence = 0.95 × 1.0 × 0.0 = 0.0

Result: "Data is too old. Re-verify required."
```

---

### Pitfall 3: Fraud Detection False Positives

**Wrong approach:**
```
"One weird billing pattern → Fraud alert"
```

**Why it fails:** Doctors have legitimate variation. Oncologists bill differently than internists. Rural providers have different patterns.

**ClaudeShannon++ approach:**
```
Signal 1: High billing volume
  BUT: Oncology specialty = higher volume normal
  Signal clarity = MEDIUM (not clear it's fraud)

Signal 2: Unusual service mix
  BUT: Peer review approves all procedures
  Signal clarity = LOW (contradicted by approval)

Result: No fraud conclusion unless multiple independent 
signals coherently point to fraud
```

---

### Pitfall 4: Invisible Dependence on Fragile Systems

**Wrong approach:**
```
"Our fraud detection AI says this is fraud → It must be fraud"
```

**Why it fails:** AI systems inherit biases from training data. They fail on edge cases. They're trained on past fraud, not future fraud.

**ClaudeShannon++ approach:**
```
Signal: "AI flagged unusual pattern"
Quality of signal: 0.60 (AI systems are useful but not authoritative)
Completeness: 0.5 (AI doesn't explain why, black box)
Freshness: 0.9 (pattern detection is recent)

Confidence = 0.60 × 0.5 × 0.9 = 0.27 (LOW)

Result: "AI finding is weak signal. Requires human + 
additional corroborating evidence to escalate."
```

---

## Part 10: Special Cases & Edge Conditions

### Case 1: Sources Disagree

**Example:** State says eligible, SSA says not enough income

```
State Medicaid: 0.98 confidence → "Eligible"
SSA Wage Records: 0.95 confidence → "Insufficient income"

Agreement score = 0.0 (maximum disagreement)
Consensus = (average × 0.6) + (agreement × 0.4)
          = (0.96 × 0.6) + (0.0 × 0.4)
          = 0.576

Result: MEDIUM confidence, but unclear direction
Action: Escalate for manual review
Reason: "Systems provide conflicting information"
```

**What to do:**
1. Trust the higher-quality source (State > SSA)
2. Get original documentation from member
3. Have caseworker make final determination

---

### Case 2: All Sources Are Old

**Example:** All eligibility data is 6+ months old

```
State Medicaid: 0.98 quality, 0.5 freshness → 0.49 confidence
SSA Wage: 0.95 quality, 0.3 freshness → 0.285 confidence
Household: 0.70 quality, 0.3 freshness → 0.21 confidence

Consensus = 0.328 (LOW)
```

**Action:** "Eligibility data requires refresh. Member should recertify."

---

### Case 3: Perfect Sources, Impossible Data

**Example:** State says someone was born in 1850

```
Source quality: 0.98 (official state)
Completeness: 1.0 (all fields)
Freshness: 1.0 (real-time)

But: Date of birth = 1850 (person would be 176 years old)

Confidence score = 0.98 (calculation is pure)
BUT: Sanity check fails

Action: Flag data entry error. Escalate for manual correction.
Rule: "System confidence score is valid, but output is impossible.
       Trust the calculation, not the data."
```

---

## Part 11: Summary Table: When to Trust, When to Escalate

| Confidence Score | Guidance | Action |
|------------------|----------|--------|
| **0.85–1.0** | Fully trust | Proceed with determination |
| **0.60–0.84** | Trust with review | Proceed, but verify key factors |
| **0.40–0.59** | Questionable | Manual review required |
| **0.20–0.39** | Don't trust | Escalate to human immediately |
| **0.0–0.19** | Invalid | Reject, request new data |

---

## Part 12: Implementation Checklist

When building a feature that scores confidence:

- [ ] Identify all data sources (State, Federal, Plan, Member)
- [ ] Assign quality score to each (0.1–0.98)
- [ ] Measure data completeness (% of required fields)
- [ ] Calculate freshness (time since last update)
- [ ] Run confidence calculation: Quality × Completeness × Freshness
- [ ] Calculate consensus if multiple sources exist
- [ ] Determine confidence level (HIGH/MEDIUM/LOW/CRITICAL)
- [ ] Generate appropriate caveat if confidence < 0.85
- [ ] Tier the response (member/provider/analyst gets different detail)
- [ ] Document any edge cases or overrides
- [ ] Test with contradictory data (sources disagree)
- [ ] Test with old data (> 6 months)
- [ ] Test with incomplete data (missing critical fields)

---

## Appendix: The Name "ClaudeShannon++"

This framework combines:

1. **Shannon Entropy** — Information theory concept (how much uncertainty is in a message?)
2. **Signal Processing** — Distinguishing signal from noise in data
3. **Claude** — Honesty principle: be clear about what you don't know

The "++" suggests: evolved from classical information theory, adapted for Medicaid realities.

---

**Last Updated:** April 24, 2026  
**Framework Status:** LIVE IN TORQ-e PRODUCTION  
**Repository:** card_1_umid/confidence.py, card_2_upid/fraud_detection.py

This document is the official specification. Code implements it. Deviations from this framework require architectural review.
