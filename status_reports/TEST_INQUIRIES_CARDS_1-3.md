# TORQ-E TEST INQUIRIES
## 9 Queries to Test Elaborate Buttons + Clarity Light + Session Context

**Testing Focus:** All three cards with session context active, elaborate buttons functional, clarity lights rendering

---

## CARD 1: UMID (Member Eligibility)
### Session: UMID present in sessionStorage

**Test 1: Coverage Status Check**
```
User Query: "Am I still covered by Medicaid?"
Expected Response:
- Concise: "YES - Your coverage is active until 12/31/2026"
- Clarity Light: 🟢 GREEN (ACTIVE)
- Sources: [Medicaid State Database | Income Verification System]
- Elaborate Button: Explains how coverage status was determined
```

**Test 2: Recertification Deadline**
```
User Query: "When do I need to recertify?"
Expected Response:
- Concise: "Your recertification is due 06/15/2026 (52 days remaining)"
- Clarity Light: 🟢 GREEN (ON TRACK)
- Sources: [Medicaid State Database | Recertification Schedule]
- Elaborate Button: Explains recertification process and what happens if delayed
```

**Test 3: Income Change Impact**
```
User Query: "What if my income increases to $2,500 a month?"
Expected Response:
- Concise: "Your coverage would NOT be affected. You remain eligible."
- Clarity Light: 🟢 GREEN (STILL ELIGIBLE)
- Sources: [Income Limit Thresholds | State Guidelines]
- Elaborate Button: Explains income limits, 130% FPL calculation, safety margin
```

---

## CARD 2: UPID (Provider Claims)
### Session: provider_id present in sessionStorage

**Test 1: Claim Validation**
```
User Query: "Is this member eligible for coverage?"
Expected Response:
- Concise: "YES - Member is enrolled and in-network for your facility"
- Clarity Light: 🟢 GREEN (VALID)
- Sources: [Claims Database | Member Enrollment Registry]
- Elaborate Button: Explains validation process (enrollment check, network status, active plan)
```

**Test 2: Claims Processing Status**
```
User Query: "What's the status of my claims processing?"
Expected Response:
- Concise: "Processing healthy. Average claim decision: 5-7 business days"
- Clarity Light: 🟢 GREEN (NORMAL)
- Sources: [Claims Processing Dashboard | Fraud Detection Engine]
- Elaborate Button: Breakdown of claims by status (pending, approved, paid), average processing times
```

**Test 3: Fraud Detection Check**
```
User Query: "Does this claim have any fraud signals?"
Expected Response:
- Concise: "No fraud signals detected. Claim is safe to submit."
- Clarity Light: 🟢 GREEN (CLEAR)
- Sources: [Fraud Detection Engine v2.1 | Claims History Analysis]
- Elaborate Button: Explains what was scanned (duplicate check, coding anomalies, member history, provider patterns)
```

---

## CARD 3: WHUP (Plan Network)
### Session: Active in chat (no special session requirement)

**Test 1: Show Plans by State**
```
User Query: "Show me the top 3 plans available in New York"
Expected Response:
- Concise: "Top 3 Medicaid Plans in NY"
  1. Empire BlueCross BlueShield (HMO | Managed)
  2. UnitedHealthcare Community (PPO | Open Network)
  3. Molina Healthcare (HMO | Managed)
- Clarity Light: 🟢 GREEN (Network Adequacy 92%)
- Sources: [Network Registry | Plan Formulary Database]
- Elaborate Button: Explains network adequacy score, what it measures (specialist access, geographic coverage, appointment wait times)
```

**Test 2: Check Eligibility**
```
User Query: "What plans am I eligible for?"
Expected Response:
- Concise: "You qualify for 5 plans based on your profile"
  1. Empire BlueCross BlueShield ✓
  2. UnitedHealthcare Community ✓
  3. Molina Healthcare ✓
- Clarity Light: 🟢 GREEN (ELIGIBLE)
- Sources: [Network Registry | Plan Eligibility Database]
- Elaborate Button: Explains how eligibility was determined (enrollment status, income, household size verification)
```

**Test 3: Compare Plans**
```
User Query: "Which plan is best if I make $10k a month?"
Expected Response:
- Concise: "For your income level, these plans offer similar affordability"
  - Empire BlueCross: Lower copays
  - UnitedHealthcare: More provider flexibility
- Clarity Light: 🟡 YELLOW (Consider Both Options)
- Sources: [Network Registry | Plan Formulary Database | CMS Quality Ratings]
- Elaborate Button: Explains HMO vs PPO trade-offs, how to choose based on doctor preferences and specialist needs
```

---

## TEST EXECUTION CHECKLIST

### Per Query, Verify:

- [ ] **Session Context Works**
  - Card 1: Shows "Welcome back, [Member]" with UMID if present
  - Card 2: Shows "Welcome back, [Provider]" with provider_id if present
  - Card 3: No session message needed (conversational only)

- [ ] **Clarity Light Renders**
  - Color is correct (🟢 green / 🟡 yellow / 🔴 red)
  - Text label is clear (Healthy / Needs Review / Critical)
  - Light dot displays correctly

- [ ] **Source Citations Display**
  - URLs are clickable (test one link to verify)
  - Timestamp format is correct (ISO 8601)
  - Multiple sources separated by pipes (|)

- [ ] **Elaborate Button Works**
  - Button visible (📖 Elaborate)
  - Click toggles elaboration text visible/hidden
  - Button text changes to "Hide Details"
  - Elaboration text appears in styled box (gray background, left border)

- [ ] **Message Flows Correctly**
  - No JavaScript errors (check browser console)
  - Chat scrolls to latest message
  - Send button enables/disables appropriately

---

## BROWSER CONSOLE CHECK

After each test inquiry, open DevTools (F12) and check:
```
Console tab: No red errors
Network tab: API calls successful (Card 3 especially - /api/card3/programs, /api/card3/eligible-programs)
Elements tab: Clarity light has correct class (clarity-light green/yellow/red)
```

---

## EXPECTED OUTCOMES

**All 9 Inquiries Should Result In:**
1. ✅ Concise answer displayed
2. ✅ Clarity light with correct color
3. ✅ Source citations with working links
4. ✅ Elaborate button that toggles details
5. ✅ No console errors
6. ✅ Session context recognized (Cards 1-2)
7. ✅ Smooth message flow and scrolling

---

**Ready to test. Deploy to Railway first, then run these 9 inquiries sequentially.**

