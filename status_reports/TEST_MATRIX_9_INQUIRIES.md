# TORQ-e Cards 1-5: 9-Inquiry Test Matrix
**Purpose:** Generate auditable receipts post-deployment  
**Date Deployed:** [To be filled in after Railway deployment]  
**Test Execution Date:** [To be filled in by tester]

---

## PRE-TEST SETUP

### Test Environment Verification
- [ ] All 5 card URLs loading without errors:
  - [ ] https://torq-e-production.up.railway.app/static/cards/chat-card1.html
  - [ ] https://torq-e-production.up.railway.app/static/cards/chat-card2.html
  - [ ] https://torq-e-production.up.railway.app/static/cards/chat-card4.html
  - [ ] https://torq-e-production.up.railway.app/static/cards/chat-card5.html
- [ ] Railway services all green in dashboard
- [ ] No console errors when loading each card

### Browser Setup
- Open each card in a new browser tab
- Keep developer console open (F12) to capture any errors
- Take screenshots of each successful test result

---

## CARD 1 (UMID) - MEMBER ELIGIBILITY SYSTEM

### Test 1a: Member Lookup with Confidence Score
**Objective:** Verify member lookup returns confidence_score field and Claude displays traffic light

**Inquiry:**
```
What member ID does John Doe born 1990-01-15 with SSN 123-45-6789 have?
```

**Expected Results:**
1. ✅ Card 1 processes lookup query
2. ✅ Backend returns MemberIdentityResponse with fields:
   - `umid: "UMID######"`
   - `confidence_score: 0.85` (or similar 0-1.0 value)
   - `data_source: "NYS_Medicaid_DB"` (or similar)
3. ✅ Claude response includes:
   - Member's UMID
   - Traffic light indicator (🟢 if confidence ≥0.85, 🟡 if ≥0.60, 🔴 if <0.60)
   - Text: "Data from external source: NYS Medicaid Database"

**Test Result:**
- [ ] PASS
- [ ] FAIL
- Notes: _______________

**Screenshot:** [Capture console output showing confidence_score field]

---

### Test 1b: Check Member Eligibility with Confidence Score
**Objective:** Verify eligibility check returns confidence_score and Claude displays traffic light

**Inquiry:**
```
Is member UMID123456 currently covered under Medicaid?
```

**Expected Results:**
1. ✅ Card 1 processes eligibility check
2. ✅ Backend returns EligibilityStatusResponse with fields:
   - `are_you_covered: "YES"` (or "NO"/"PENDING")
   - `confidence_score: 0.92` (or similar)
   - `coverage_until: "2026-12-31"` (or similar)
3. ✅ Claude response includes:
   - Clear answer: "YES, you are covered until [date]"
   - Traffic light: 🟢 if confidence ≥0.85, 🟡 if ≥0.60, 🔴 if <0.60
   - Note about data source

**Test Result:**
- [ ] PASS
- [ ] FAIL
- Notes: _______________

**Screenshot:** [Capture console output showing confidence_score]

---

### Test 1c: Check Recertification Status with Confidence Score
**Objective:** Verify recertification check returns confidence_score and Claude displays traffic light

**Inquiry:**
```
When do I need to recertify my Medicaid eligibility?
```

**Inquiry (Alternative if need member context):**
```
Check recertification status for UMID123456
```

**Expected Results:**
1. ✅ Card 1 processes recertification query
2. ✅ Backend returns RecertificationStatusResponse with fields:
   - `days_until_due: 45` (or similar)
   - `status: "ALERT_60_DAYS"` (or "ON_TRACK"/"ALERT_URGENT"/"OVERDUE")
   - `confidence_score: 0.85` (if >30 days), `0.65` (if 0-30 days), `0.45` (if overdue)
3. ✅ Claude response includes:
   - Days until recertification
   - Status assessment
   - Traffic light: 🟢 if confidence ≥0.85, 🟡 if ≥0.60, 🔴 if <0.60
   - Next steps for upload

**Test Result:**
- [ ] PASS
- [ ] FAIL
- Notes: _______________

**Screenshot:** [Capture console output showing confidence_score]

---

## CARD 2 (UPID) - PROVIDER SYSTEM

### Test 2a: Provider Lookup with Confidence Score
**Objective:** Verify provider lookup returns confidence_score and Claude displays traffic light

**Inquiry:**
```
What provider ID does Dr. Jane Smith with NPI 1234567890 have?
```

**Expected Results:**
1. ✅ Card 2 processes provider lookup
2. ✅ Backend returns ProviderIdentityResponse with fields:
   - `upid: "UPID######"`
   - `confidence_score: 0.88` (or similar 0-1.0 value)
   - `specialty: "Internal Medicine"` (or similar)
   - `data_source: "NPI_Database"` (or "eMedNY"/"MCO_Panel")
3. ✅ Claude response includes:
   - Provider's UPID
   - Specialty and practice info
   - Traffic light: 🟢 if confidence ≥0.85, 🟡 if ≥0.60, 🔴 if <0.60
   - Data source attribution

**Test Result:**
- [ ] PASS
- [ ] FAIL
- Notes: _______________

**Screenshot:** [Capture console output showing confidence_score]

---

### Test 2b: Check Provider Enrollment Status with Confidence Score
**Objective:** Verify enrollment check returns confidence_score and Claude displays traffic light

**Inquiry:**
```
What plans is provider UPID123456 enrolled in?
```

**Expected Results:**
1. ✅ Card 2 processes enrollment check
2. ✅ Backend returns ProviderEnrollmentStatusResponse with fields:
   - `ffs_status: "ACTIVE"` (or "SUSPENDED"/"TERMINATED")
   - `mco_enrollments: {"MCO_A": "ACTIVE", "MCO_B": "ACTIVE"}` (or similar)
   - `confidence_score: 0.90` (if valid creds + FFS + MCOs), `0.75` (if partial), `0.50` (if none)
   - `credentials_valid: true` (or false)
3. ✅ Claude response includes:
   - FFS status
   - MCO plans and statuses
   - Total active plans count
   - Traffic light: 🟢 if confidence ≥0.85, 🟡 if ≥0.60, 🔴 if <0.60
   - Next steps (contact MCO or enroll)

**Test Result:**
- [ ] PASS
- [ ] FAIL
- Notes: _______________

**Screenshot:** [Capture console output showing confidence_score]

---

### Test 2c: Validate Claim with Confidence Score
**Objective:** Verify claim validation returns confidence_score and Claude displays traffic light

**Inquiry:**
```
Is this claim valid? [claim details: member UMID123456, provider UPID654321, CPT 99213, diagnosis M79.3, amount $150, service date 2026-04-20]
```

**Expected Results:**
1. ✅ Card 2 processes claim validation
2. ✅ Backend returns ClaimValidationResponse with fields:
   - `valid: true` (or false)
   - `errors: []` (or list of error messages)
   - `warnings: []` (or list of warning messages)
   - `confidence_score: 0.95` (no errors/warnings), `0.75` (no errors), `0.40` (has errors)
   - `action: "SUBMIT"` (or "REJECT")
3. ✅ Claude response includes:
   - Claim validity assessment
   - Any errors or warnings to fix
   - Traffic light: 🟢 if confidence ≥0.85, 🟡 if ≥0.60, 🔴 if <0.60
   - Recommendation (submit or reject)

**Test Result:**
- [ ] PASS
- [ ] FAIL
- Notes: _______________

**Screenshot:** [Capture console output showing confidence_score]

---

## CARDS 4 & 5 - GOVERNANCE & authenticity investigation

### Test 4: Card 4 - Query Governance Metrics
**Objective:** Verify Card 4 Spectrum Analyzer displays and is fully interactive

**Inquiry:**
```
What is the current system coherence and health status?
```

**OR (Alternative)**
```
Show me the Clarity Spectrum for all governance metrics
```

**Expected Results:**
1. ✅ Card 4 processes governance metrics query
2. ✅ Browser displays Spectrum Analyzer with:
   - Large coherence traffic light (80x80px) with color (🟢/🟡/🔴) and percentage
   - 3 collapsible sections visible (headers with ▶ icon when collapsed)
   - Section 1: "Coherence Level" - shows single large traffic light
   - Section 2: "Clarity Spectrum Equalizer" - shows 6 metric cards in grid:
     * Enrollment Rate, Claims Processing, Data Quality, Audit Trail, Compliance, System Stability
     * Each with 32x32px traffic light + metric name + percentage + progress bar
   - Section 3: "Combined View" - shows both coherence + spectrum
3. ✅ Interactive Features Work:
   - [ ] Click section header → section collapses, icon rotates ▶ → ▼
   - [ ] Click metric card → breakdown panel expands below showing:
     * Traffic light visual (3 stacked circles: red, yellow, green)
     * Equalizer visual (5 bars of varying heights)
     * Data sources list with clickable [Name](URL) links
     * Calculation logic explanation
     * Detailed breakdown statistics
   - [ ] Click source remove button (✕) → confirmation modal appears
   - [ ] Confirm removal → source disappears from list temporarily

**Test Result:**
- [ ] PASS
- [ ] FAIL
- Notes: _______________

**Screenshots:**
- [ ] Spectrum Analyzer fully expanded
- [ ] One section collapsed to show toggle behavior
- [ ] One metric breakdown panel expanded
- [ ] Source removal confirmation modal

---

### Test 5a: Card 5 - Query Investigation Metrics
**Objective:** Verify Card 5 displays correct dimensions and breakdown data

**Inquiry:**
```
What is our claims data quality and outlier detection status?
```

**OR (Alternative)**
```
Show me the investigation metrics dashboard
```

**Expected Results:**
1. ✅ Card 5 processes investigation query
2. ✅ Browser displays Spectrum Analyzer with Card 5-specific dimensions:
   - **NOT** "Enrollment Rate" but "Claims Data Quality"
   - **NOT** "Claims Processing" but "Outlier Detection"
   - **NOT** "Data Quality" but "Network Analysis"
   - **NOT** "Audit Trail" but "Investigation Cases"
   - **NOT** "Compliance" but "Data Correction Status"
   - **NOT** "System Stability" but "Analysis Tool Status"
3. ✅ 6 metric cards display with Card 5-specific sources:
   - Claims Data Quality → CMS, Validation Engine sources
   - Outlier Detection → NIST Statistical Methods, authenticity verification sources
   - Network Analysis → Provider/Member Network, Co-billing sources
   - Investigation Cases → Investigation Case Management sources
   - Data Correction Status → Correction Workflow, Approval sources
   - Analysis Tool Status → Infrastructure, System Performance sources
4. ✅ All interactive features work (collapse/expand, breakdown panels)

**Test Result:**
- [ ] PASS
- [ ] FAIL
- Notes: _______________

**Screenshots:**
- [ ] Card 5 dimensions visible (should show "Claims Data Quality", not "Enrollment Rate")
- [ ] One breakdown panel expanded showing Card 5-specific sources
- [ ] Compare dimension names to Card 4 (should be different)

---

### Test 5b: Card 5 - Elaborate on Investigation Case with Sources
**Objective:** Verify Card 5 breakdown data and elaborate buttons work

**Inquiry:**
```
Tell me more about investigation cases - how many are active?
```

**OR (Alternative after querying metrics)**
```
 📖 Elaborate on Investigation Cases
```

**Expected Results:**
1. ✅ Card 5 processes elaboration query
2. ✅ Breakdown panel for "Investigation Cases" displays:
   - Value: Approximately 80-100% (governance compliance metric)
   - Logic: "Active investigations + evidence collected + resolution rate"
   - Breakdown statistics:
     * "Active: 47 | Under review: 23 | Closed (6mo): 156 | Resolved: 141 | Pending: 15"
   - Source URLs (should be Card 5 specific):
     * [Investigation Workflows](https://www.cms.gov/Medicaid-inauthenticity-Control)
     * [Case Management Standards](https://www.cms.gov/inauthenticity-prevention)
     * [Audit Trail Requirements](https://www.ecfr.gov/current/title-42/part-455)
3. ✅ Sources are clickable links (can test in browser)
4. ✅ Remove button (✕) works on each source with confirmation modal

**Test Result:**
- [ ] PASS
- [ ] FAIL
- Notes: _______________

**Screenshots:**
- [ ] Investigation Cases breakdown panel fully expanded
- [ ] Source links visible and clickable
- [ ] Source removal button with confirmation modal

---

## SUMMARY OF RESULTS

### Card 1 Results
| Test | Result | Confidence Score | Traffic Light | Notes |
|------|--------|------------------|----------------|-------|
| 1a: Member Lookup | [ ] PASS / [ ] FAIL | ______ | 🟢/🟡/🔴 | |
| 1b: Eligibility Check | [ ] PASS / [ ] FAIL | ______ | 🟢/🟡/🔴 | |
| 1c: Recertification | [ ] PASS / [ ] FAIL | ______ | 🟢/🟡/🔴 | |

### Card 2 Results
| Test | Result | Confidence Score | Traffic Light | Notes |
|------|--------|------------------|----------------|-------|
| 2a: Provider Lookup | [ ] PASS / [ ] FAIL | ______ | 🟢/🟡/🔴 | |
| 2b: Enrollment Check | [ ] PASS / [ ] FAIL | ______ | 🟢/🟡/🔴 | |
| 2c: Claim Validation | [ ] PASS / [ ] FAIL | ______ | 🟢/🟡/🔴 | |

### Cards 4 & 5 Results
| Test | Result | UI Elements | Interactivity | Notes |
|------|--------|------------|----------------|-------|
| 4: Governance Metrics | [ ] PASS / [ ] FAIL | ✅ / ❌ | ✅ / ❌ | |
| 5a: Investigation Metrics | [ ] PASS / [ ] FAIL | ✅ / ❌ | ✅ / ❌ | |
| 5b: Elaborate + Sources | [ ] PASS / [ ] FAIL | ✅ / ❌ | ✅ / ❌ | |

---

## CRITICAL SUCCESS CRITERIA

All of the following must be TRUE for deployment to be considered successful:

✅ **Cards 1 & 2 - Confidence Scores**
- [ ] All 6 tests (1a, 1b, 1c, 2a, 2b, 2c) return confidence_score field in API response
- [ ] All 6 tests display traffic light (🟢/🟡/🔴) in Claude response
- [ ] Confidence scores are correctly mapped to traffic lights:
  - 🟢 GREEN: confidence ≥ 0.85 (HIGH veracity)
  - 🟡 YELLOW: 0.60 ≤ confidence < 0.85 (MEDIUM veracity)
  - 🔴 RED: confidence < 0.60 (LOW veracity)

✅ **Cards 4 & 5 - Architectural Parity**
- [ ] Card 4 Spectrum Analyzer displays and is fully interactive
- [ ] Card 5 Spectrum Analyzer displays with DIFFERENT dimensions (Claims Data Quality, Outlier Detection, Network Analysis, Investigation Cases, Data Correction Status, Analysis Tool Status)
- [ ] Card 5 breakdown data shows CARD 5-SPECIFIC sources (CMS inauthenticity, NIST, investigation management)
- [ ] All 3 sections collapsible/expandable in both cards
- [ ] Breakdown panels functional with traffic light visuals, equalizer visuals, and source removal

✅ **Overall System Health**
- [ ] No JavaScript errors in browser console
- [ ] No API errors (all responses HTTP 200)
- [ ] All cards load in <3 seconds
- [ ] All Claude queries respond in <5 seconds

---

## REGULATORY APPROVAL GATE

### Submit Test Results To: Bob Pollock (Government Stakeholder)
**Required for Approval:**
1. ✅ All 9 tests PASS
2. ✅ All critical success criteria met
3. ✅ Screenshots of each test result
4. ✅ Console logs showing confidence_score fields
5. ✅ Architecture blueprint documentation reviewed

**Next Steps After Approval:**
1. Phase 3: Proof-of-concept scaling (rest of 2026 through early 2027)
2. Full production rollout planning
3. Training documentation for external users
4. SLA and monitoring setup

---

## TEST EXECUTION LOG

**Tester Name:** _________________  
**Test Date:** _________________  
**Environment:** Railway Production  
**Browser:** _________________  
**Browser Version:** _________________  

### Notes & Issues Encountered
```
[Space for detailed notes about any issues or unexpected behavior]

```

### Final Sign-Off
- [ ] All tests executed
- [ ] All results documented
- [ ] Ready for regulatory review

**Tester Signature:** _________________ **Date:** _________________

