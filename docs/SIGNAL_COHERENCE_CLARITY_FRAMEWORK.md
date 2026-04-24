# Signal, Coherence & Clarity: Data Analyst's Framework for Fraud Detection

**For:** Data Analysts (UBADA), Fraud Investigators, State Oversight  
**Version:** 1.0  
**Date:** April 24, 2026

---

## Executive Summary

In TORQ-e, we distinguish between three critical concepts when analyzing Medicaid data:

1. **SIGNAL** — Observable patterns in data (what we see)
2. **COHERENCE** — Internal consistency of patterns (do the pieces fit together?)
3. **CLARITY** — Confidence that a signal is real vs. noise (can we trust it?)

This framework prevents two deadly errors:
- **False Positives**: Flagging honest providers as fraudsters (wrong accusation)
- **False Negatives**: Missing actual fraud because signal was too weak (fraud escapes)

---

## Part 1: What is Signal?

### Definition
**Signal** = Observable pattern in provider behavior, claims data, or enrollment patterns that deviates from expected baseline.

### Examples of Signals

**Billing Signal:**
- Provider submits 5x more claims than average provider in their specialty
- Provider bills for service at 2 AM (office is closed)
- Provider bills identical service code 50 times in single day

**Enrollment Signal:**
- Provider enrolled at PO Box address (not real office)
- Provider's office address matches 50 other providers (shell network)
- Provider listed as both MD and Dentist (impossible)

**Temporal Signal:**
- Provider's billing volume increases 300% over 2 months
- Provider's billing volume drops to zero after investigation starts
- Provider bills retroactively for services 6 months ago

**Network Signal:**
- Provider bills only to members who are also patients of other flagged providers
- Provider's claims cluster in one geographic area despite statewide license
- Provider shares office address with 10 other providers all billing similar codes

### Signal Strength vs. Frequency

| Signal | Strength | Example |
|--------|----------|---------|
| Single large claim | Weak | One $50,000 claim for routine visit |
| Repeated small claims | Medium | 20 claims of $500 each for same service |
| Pattern across months | Strong | Systematic overbilling every single day for 90 days |
| Pattern across members | Very Strong | Same unnecessary service billed to 200 different members |

---

## Part 2: What is Coherence?

### Definition
**Coherence** = How well pieces of evidence align. Do multiple independent signals tell the same story? Or do they contradict?

### Example: High Coherence (All pieces fit)

**Provider: Dr. Suspicious**
- ✅ Signal 1: Bills 3x more than peers
- ✅ Signal 2: All patients from single nursing home
- ✅ Signal 3: Billed for services nursing home staff says didn't happen
- ✅ Signal 4: Has history of fraud in another state (OIG record)
- ✅ Signal 5: Office address is same as 8 other providers with same pattern

**Coherence Score: 95/100** → All signals point to same conclusion: FRAUD

### Example: Low Coherence (Pieces contradict)

**Provider: Dr. Legitimate**
- ⚠ Signal 1: Bills slightly more than average
- ✅ Signal 2: But has large specialty practice (more patients = more claims)
- ✅ Signal 3: All claims documented in medical records
- ✅ Signal 4: No OIG history
- ✅ Signal 5: Legitimate office address, licensed properly
- ✅ Signal 6: Peer review committee confirms care was appropriate

**Coherence Score: 15/100** → Signals contradict. Overbilling likely due to specialty, not fraud.

### How to Calculate Coherence

1. **List all signals** (positive and negative)
2. **Score alignment** for each signal pair:
   - Do they point to same conclusion? +1
   - Do they point to different conclusions? -1
   - Are they unrelated? 0
3. **Calculate ratio**: (Supporting signals) / (Total signals) × 100

**Formula:**
```
Coherence = (Signals supporting fraud conclusion) / (Total signals) × 100
```

---

## Part 3: What is Clarity?

### Definition
**Clarity** = Confidence that we can trust a signal. How certain are we that this pattern is real vs. noise/error?

### Sources of Uncertainty (Low Clarity)

| Source | Impact | Example |
|--------|--------|---------|
| Data quality | Moderate | Claims database has duplicate records (claimed twice by accident) |
| Seasonal variation | Low | Providers bill more in winter; appears as signal but is normal |
| System changes | Moderate | New billing code introduced; appears as spike but is administrative |
| Small sample size | High | Provider submitted only 10 claims (one outlier changes average 10%) |
| Reporting lag | Moderate | Billing data is 2 months old; fraud happened earlier, data is stale |
| Attribution error | High | Service coded as "office visit" but patient never visited (coder error) |

### Clarity Score Calculation

For each signal, assign:
- **+20** if data source is government-verified (state license, CMS registration)
- **+15** if data source is audited healthcare database (claims, medical records)
- **+10** if data source is provider self-report
- **-10** if data comes from single source only (no corroboration)
- **-15** if data is outdated (older than 30 days)
- **-20** if sample size is very small (<10 instances)

**Example Clarity Calculation:**

```
Signal: "Provider bills 5x more than peers"

Data sources:
  + Government claims database (audited):        +20
  + Verified against 50 peer providers:          +15
  + Pattern consistent for 6 months:            +10
  - Is billing legitimate (specialty)?:         -10
  - Possible system coding change?:             -5

Total Clarity Score: 20 + 15 + 10 - 10 - 5 = 30/100
Interpretation: MODERATE clarity — signal exists but has alternative explanations
```

### Clarity Ranges

| Score | Interpretation | Action |
|-------|------------------|--------|
| 80-100 | Very High Clarity | Trust the signal; escalate if coherence is high |
| 60-79 | High Clarity | Likely trustworthy; investigate further |
| 40-59 | Moderate Clarity | Could be real; requires human review |
| 20-39 | Low Clarity | Questionable; need more data before action |
| 0-19 | Very Low Clarity | Ignore; likely noise or error |

---

## Part 4: The Three-Part Judgment Framework

Use all three concepts together to make fraud determinations:

### Step 1: Identify Signals
- What patterns do we observe in the data?
- How strong is each signal?
- Are there contradicting signals?

### Step 2: Calculate Coherence
- Do multiple signals point to same conclusion?
- How many support fraud? How many contradict it?
- Coherence Score: X/100

### Step 3: Assess Clarity
- How certain are we in the data sources?
- Are there alternative explanations?
- Clarity Score: X/100

### Step 4: Make Judgment

```
Fraud Risk = (Coherence × Clarity) / 100

Risk Level:
  80-100 = CRITICAL (immediate investigation, halt payments)
  60-79  = HIGH (investigate within 1 week, monitor payments)
  40-59  = MEDIUM (investigate, but normal processing continues)
  20-39  = LOW (monitor, no immediate action)
  0-19   = MINIMAL (document and move on)
```

---

## Part 5: Real-World Examples

### Case 1: Dr. Smith (FRAUD DETECTED)

**Signals Observed:**
1. ✅ Billing volume 4x peers (specialty: radiology)
2. ✅ All claims from single nursing home
3. ✅ Services never confirmed by nursing home staff
4. ✅ Prior OIG exclusion in California (2018)
5. ❌ Medical records support all claims

**Coherence Calculation:**
- Signals 1-4 point to fraud: 4
- Signal 5 contradicts fraud: 1
- Coherence = 4/5 = **80/100**

**Clarity Calculation:**
- Government OIG database:           +20
- Audited claims data (6 months):    +20
- Nursing home confirmation:         +15
- Only radiology claims (specialty): +10
- Data is current (within 30 days):  +10
- Clarity = **75/100**

**Fraud Risk = (80 × 75) / 100 = 60/100 = HIGH**

**Decision:** Investigate within 1 week. Monitor claims but allow processing to continue until investigation concludes. If overbilling confirmed, halt future claims and recover overpayment.

---

### Case 2: Dr. Jones (LEGITIMATE PROVIDER)

**Signals Observed:**
1. ✅ Billing volume 3x peers
2. ✅ Only treats complex patients (sicker population)
3. ✅ All claims documented in medical records
4. ✅ No OIG history
5. ✅ Peer review committee approves all claims
6. ✅ Specialty: Oncology (high-cost, high-volume specialty)

**Coherence Calculation:**
- Signals 2-6 contradict fraud: 5
- Signal 1 requires context: 0
- Coherence = 5/6 = **83/100** (but points to LEGITIMATE, not fraud)

**Clarity Calculation:**
- Medical records verification:      +20
- Peer review committee (audited):   +20
- Government OIG database:           +20
- Specialty-appropriate billing:     +15
- Data current (within 30 days):     +10
- Large patient sample (300+):       +10
- Clarity = **95/100**

**Fraud Risk = (17 × 95) / 100 = 16/100 = MINIMAL**

*Note: Coherence score is inverted here—signals are coherent but point to legitimacy, not fraud.*

**Decision:** No action. Document approval. Continue normal payment processing.

---

### Case 3: Dr. Unknown (UNCLEAR - NEEDS MORE DATA)

**Signals Observed:**
1. ✅ Billing volume 2x peers
2. ❓ Small sample size (only 10 claims)
3. ❓ Specialty not verified (new provider)
4. ✅ No OIG history
5. ❓ Claims match documented medical records (but provider is new, records not yet verified)

**Coherence Calculation:**
- Supporting fraud: 1
- Contradicting fraud: 1
- Uncertain: 3
- Coherence = 1/5 = **20/100** (incoherent - need more data)

**Clarity Calculation:**
- New provider (no history):        -20
- Small claims volume (n=10):       -20
- Medical records not yet verified: -10
- No OIG disqualification:          +10
- Claims data is current:           +10
- Clarity = **-30/100** → Floor at 0

**Fraud Risk = (20 × 0) / 100 = 0/100 = MINIMAL (but UNCERTAIN)**

**Decision:** No fraud action yet, but DO NOT ESCALATE. Monitor provider for next 30-60 days. Collect more claims data. Re-assess when sample size reaches 50+ claims. Verify specialty and credentials.

---

## Part 6: Special Cases

### When Clarity is Very Low But Coherence is High

**Example:** Provider A and Provider B both bill unusually, but data is 90 days old and system was updated 60 days ago.

**Recommendation:** Do NOT escalate. Wait for cleaner data. Request current data (within 30 days) before fraud determination.

### When Clarity is Very High But Coherence is Low

**Example:** All signals point in different directions, but data is very trustworthy.

**Recommendation:** Provider is likely legitimate. The apparent pattern is noise or specialty-related. Close case with documentation.

### When New Evidence Emerges

**Example:** Provider passes initial review (low risk), but 2 months later, new evidence shows OIG history.

**Recommendation:** Recalculate scores with new evidence. Update Clarity and Coherence. May jump from LOW risk to CRITICAL. Escalate immediately if pattern supports fraud.

---

## Part 7: Data Analyst Workflow

### Step 1: Set Baseline (Monthly)
For each provider specialty, calculate:
- Average claims volume
- Average claim amount
- Average member count
- Average diagnosis codes
- Store as baseline for comparison

### Step 2: Monitor Signals (Daily/Weekly)
Run automated checks:
- Billing volume vs. baseline
- New OIG exclusions
- Claims denied by member verification
- Address/credential changes

### Step 3: Alert on Medium+ Signals
When signal strength exceeds baseline by 2+ standard deviations:
- Generate alert
- Calculate Coherence and Clarity
- Route to appropriate analyst

### Step 4: Investigate (Human)
Analyst reviews:
- All signals together
- Alternative explanations
- Similar patterns in peer group
- Historical pattern for provider

### Step 5: Judgment & Action
- Assign Fraud Risk score
- Document reasoning
- Escalate if CRITICAL or HIGH
- Monitor if MEDIUM
- Close if LOW/MINIMAL

### Step 6: Document & Learn
Store case outcome:
- What signals were correct?
- What signals were noise?
- Update baseline if systematic error found
- Share learnings with team

---

## Part 8: Common Mistakes to Avoid

### ❌ Mistake 1: High Signal = High Fraud
**Wrong:** "Provider bills 5x more than average, must be fraud"

**Right:** "Provider bills 5x more. But specialty is oncology (high-cost). Medical records support claims. No OIG history. Coherence is high but signals support legitimacy. Assess as MINIMAL risk."

**Lesson:** Signal strength ≠ fraud certainty. Context matters.

### ❌ Mistake 2: Ignoring Coherence
**Wrong:** "One signal is strong, so fraud must be happening"

**Right:** "One signal is strong, but 5 other signals contradict it. Coherence is low. Need more data before escalation."

**Lesson:** Single signals are unreliable. Multiple signals provide robustness.

### ❌ Mistake 3: Trusting Unclear Data
**Wrong:** "Data shows fraud, so it must be real"

**Right:** "Data shows fraud, but source is unverified, outdated, and comes from single provider self-report. Clarity is very low. Need government-verified data before action."

**Lesson:** Data quality matters as much as pattern.

### ❌ Mistake 4: Over-Investigating
**Wrong:** Treating all signals as urgent, investigating every anomaly

**Right:** Prioritize by Fraud Risk score. Investigate CRITICAL/HIGH first. Monitor MEDIUM. Ignore LOW/MINIMAL.

**Lesson:** Limited resources. Triage by risk.

### ❌ Mistake 5: Confirmation Bias
**Wrong:** "I think this provider is fraudulent, so I'll only look for evidence supporting that"

**Right:** "I've identified signals. Let me actively look for contradictory evidence. If coherence is low, I'll close the case."

**Lesson:** Actively seek disconfirming evidence.

---

## Part 9: Coherence vs. Confusion (For Members & Layperson Explanation)

When explaining fraud detection to non-analysts, use simple language:

### What is Coherence?

> "Coherence is when multiple pieces of evidence all point to the same answer. Like a detective movie: one clue could be wrong, but when 5 clues all point to the same criminal, you know you're on to something."

### What is Confusion?

> "Confusion is when pieces of evidence contradict each other. Like: one clue says the criminal went north, but another says they went west. When evidence is confused, it usually means we don't have the full picture yet."

### Example for Members:

**Confusing Situation:**
- Provider's billing looks unusual
- But medical records match
- But provider is new
- But peer review says it's fine
- But they bill from strange hours

**What to say:** "We found some confusing signals about this provider. It's not clear yet if something is wrong. We're gathering more information before we make a decision."

**Clear Situation:**
- Provider bills way more than everyone
- Medical records don't support it
- Nursing home says services never happened
- Provider had fraud charges before
- Office is fake (PO Box)

**What to say:** "We found clear evidence of fraud. We're stopping payments and investigating."

---

## Summary: The Three Pillars

| Concept | Definition | How to Calculate |
|---------|-----------|-------------------|
| **SIGNAL** | Observable pattern in data | Deviation from baseline; compare to peers |
| **COHERENCE** | Multiple signals align | % of signals supporting same conclusion |
| **CLARITY** | Trust in the data | Source verification + data quality + recency |

**Fraud Risk = (Coherence × Clarity) / 100**

Use this framework to distinguish real fraud from noise, prevent false accusations, and protect honest providers while catching real criminals.

---

**Last Updated:** April 24, 2026  
**Framework Version:** 1.0  
**Status:** LIVE FOR TORQ-e DATA ANALYSTS
