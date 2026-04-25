# DR;AN: Comprehensive Architecture Note - TORQ-e Cards 1-5
**Date:** April 25, 2026  
**Scope:** Complete light system architecture, data flows, response schemas  
**Status:** Based on actual code review, not assumptions

---

## EXECUTIVE SUMMARY: THE LIGHT SYSTEM

All 5 cards use **the same fundamental light system architecture**, but with these critical differences:

| Aspect | Cards 1-2 | Card 3 | Cards 4-5 |
|--------|-----------|--------|-----------|
| **Light Name** | Clarity | Clarity | Coherence Level + Clarity Spectrum Equalizer |
| **Light Type** | Single light (RED/YELLOW/GREEN) | Single light (RED/YELLOW/GREEN) | 1 large light + 6 dimension lights |
| **Data Returned** | `clarity: "green"` (string) | `clarity: "green"` (string) | 6 numeric values (0-100%) + colors derived |
| **When Shown** | CONDITIONALLY (only external sources) | ALWAYS (all data) | ALWAYS (all metrics shown) |
| **Sources Display** | Collapsed stacks, NO remove buttons | Collapsed stacks (if any) | Collapsed stacks WITH remove buttons (✕) |
| **Backend Field** | `clarity` string | `clarity` string | Individual metric values: enrollment_rate, claims_processing, data_quality, audit_trail, compliance, system_stability |

---

## PART 1: CARDS 1 & 2 - THE "CLARITY" LIGHT SYSTEM

### 1.1 Card 1 (UMID) - Member Eligibility

**System Prompt Rule (Line 598-619 in chat.py):**
```
For EVERY eligibility or benefits question:
1. Use lookup_member or check_eligibility tools FIRST
2. If tool result has _confidence_metadata with veracity value:
   - Extract veracity (e.g., "HIGH (🟢)", "MEDIUM (🟡)", "LOW (🔴)")
   - Include traffic light in response
3. If NO confidence metadata (internal DB only):
   - Answer directly, NO traffic light
4. If cannot answer:
   - Recommend call 1-800-541-2831
```

**Confidence Mapping (Line 616-619):**
- 🟢 HIGH (0.85+): Authoritative state database
- 🟡 MEDIUM (0.60-0.84): Reliable but recommend verification
- 🔴 LOW (<0.60): Incomplete or conflicting

**What Gets Returned from Backend (Based on routes.py):**
```python
# check_eligibility endpoint returns EligibilityStatusResponse:
{
    "umid": "UMID123456",
    "member_name": "John Doe",
    "are_you_covered": "YES",  # or "NO"/"PENDING"
    "coverage_until": "2026-12-31",
    "confidence_score": 0.92,  # ← KEY FIELD
    "caveats": "Optional warning about data"
}

# check_recertification endpoint returns RecertificationStatusResponse:
{
    "umid": "UMID123456",
    "recertification_date": "2026-06-30",
    "days_until_due": 67,
    "status": "ON_TRACK",
    "confidence_score": 0.85,  # ← KEY FIELD (0.85 if >30 days, 0.65 if 0-30, 0.45 if overdue)
    "next_action": "..."
}
```

**How Claude Displays It (in chat.py _prepare_tool_result_for_claude, Lines 399-444):**
1. Backend returns confidence_score in response
2. chat.py extracts it and creates _confidence_metadata:
   ```python
   metadata["veracity"] = "HIGH (🟢)" if confidence_score >= 0.85 else "MEDIUM (🟡)" if confidence_score >= 0.60 else "LOW (🔴)"
   ```
3. Returns augmented result:
   ```python
   {
       "data": result,
       "_confidence_metadata": {
           "confidence": 0.92,
           "veracity": "HIGH (🟢)",
           "caveat": None,
           "sources": "State Medicaid DB"
       }
   }
   ```
4. Claude system prompt tells Claude: Extract `_confidence_metadata.veracity` and display it with the answer
5. Example response: `🟢 HIGH | Your coverage is active through December 2026`

**Critical Behavior: CONDITIONAL LIGHTS**
- Card 1 only shows lights when querying EXTERNAL sources (state database, eMedNY)
- If data is purely internal (cached in system), Claude system prompt says "NO traffic light needed"
- This distinction is critical: **lights = data reliability**, not system status

### 1.2 Card 2 (UPID) - Provider System

**System Prompt Rule (Line 640-670 in chat.py):**
```
For EVERY enrollment, claims, or verification question:
1. Use lookup_provider, check_enrollment, or validate_claim tools FIRST
2. If tool has _confidence_metadata with veracity:
   - Extract veracity (🟢🟡🔴)
   - Include in response
3. If no metadata:
   - Answer directly, NO light
4. Cannot answer:
   - Recommend eMedNY Support 1-800-343-9000
```

**Confidence Mapping (Line 658-661):**
- 🟢 HIGH (0.85+): Verified with official eMedNY systems
- 🟡 MEDIUM (0.60-0.84): Reliable but recommend verification
- 🔴 LOW (<0.60): Incomplete or conflicting

**What Gets Returned from Backend (Based on routes.py):**
```python
# check_enrollment endpoint returns ProviderEnrollmentStatusResponse:
{
    "upid": "UPID654321",
    "npi": "1234567890",
    "ffs_status": "ACTIVE",
    "mco_enrollments": {"MCO_A": "ACTIVE", "MCO_B": "ACTIVE"},
    "total_plans": 2,
    "credentials_valid": true,
    "confidence_score": 0.90,  # ← KEY FIELD
    # Calculation: 0.90 if valid+FFS+MCOs, 0.75 if partial, 0.50 if none
    "message_for_provider": "You are enrolled in 2 MCO plans and FFS"
}

# validate_claim endpoint returns ClaimValidationResponse:
{
    "valid": true,
    "errors": [],
    "warnings": [],
    "confidence_score": 0.95,  # ← KEY FIELD
    # Calculation: 0.95 if no errors/warnings, 0.75 if no errors, 0.40 if has errors
    "action": "SUBMIT",
    "message": "Claim is valid and ready to submit"
}
```

**How Claude Displays It: Same as Card 1**
- Extracts confidence_score from response
- Chat.py creates _confidence_metadata with veracity
- Claude displays inline with answer

**Critical Behavior: CONDITIONAL LIGHTS**
- Card 2 only shows lights when querying EXTERNAL sources (eMedNY, MCO systems)
- Same philosophy as Card 1: lights = data reliability

---

## PART 2: CARD 3 - THE "CLARITY" LIGHT SYSTEM (ALWAYS ON)

**Key Difference from Cards 1-2: ALWAYS shows lights**

### 3.1 Card 3 HTML Implementation

**Clarity Light CSS (Lines 259-300 in chat-card3.html):**
```css
.clarity-light {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: #f5f5f5;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
}

.clarity-light.green { color: #15803d; }
.clarity-light.yellow { color: #ca8a04; }
.clarity-light.red { color: #dc2626; }

.light-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
}

.clarity-light.green .light-dot { background: #22c55e; }
.clarity-light.yellow .light-dot { background: #eab308; }
.clarity-light.red .light-dot { background: #ef4444; }
```

**Clarity Light Rendering Function (Line 440-450):**
```javascript
function renderClarityLight(clarity) {
    const labelMap = {
        'green': 'Healthy',
        'yellow': 'Needs Review',
        'red': 'Critical'
    };
    return `<div class="clarity-light ${clarity}">
        <span class="light-dot"></span>
        <span>${labelMap[clarity] || clarity}</span>
    </div>`;
}
```

### 3.2 Card 3 Data Flow

**Backend Returns:**
```python
# Example response to plan query:
{
    "programs": [
        {"name": "Empire BlueCross", "type": "HMO", "network": "Managed"},
        ...
    ],
    "count": 5,
    "clarity": "green",  # ← String: "green", "yellow", or "red"
    "sources": [
        {"name": "Plan Network System", "url": "https://..."},
        ...
    ],
    "network_adequacy_score": 92
}
```

**Frontend Processing (Lines 563-577):**
```javascript
data.programs.forEach(...);  // Display plans
html += renderClarityLight(data.clarity);  // ← ALWAYS shows light
html += renderSources(data.sources);  // Shows sources
html += renderElaborateButton(...);  // Shows elaborate button
```

**Key Behavior:**
- Line 608 in mock mode: `html += renderClarityLight('green');` - Always green for mock
- Line 644 in real data: `html += renderClarityLight(data.clarity);` - Uses backend value
- **Sources display**: Line 457 shows sources as clickable links, BUT **NO remove buttons** ❌
- Card 3 does NOT allow source removal (unlike Cards 4-5)

**Card 3 System Prompt (Line 683-697 in chat.py):**
```
Plan administrative data is ALWAYS external to state systems.
ALWAYS show traffic light (🟢🟡🔴) + LIVE URL combined for every response
```

---

## PART 3: CARDS 4 & 5 - "COHERENCE LEVEL" + "CLARITY SPECTRUM EQUALIZER"

### 3.1 Data Structure Returned by Backend

**Card 4 Backend Returns Numeric Values (from query_engine.py):**
```python
# query_aggregate_metrics returns:
{
    "metric": "Current Enrollment Rate",
    "value": 87.3,  # Percentage
    "sources": ["State Medicaid Database", "MCO Reporting"],
    "confidence_score": 0.95,  # Separate from metric values
    "veracity": "HIGH (0.95)",
    "freshness": "Updated daily"
}
```

**BUT Card 4's HTML Frontend Expects (Lines 1153-1163 in chat-card4.html):**
```javascript
generateSpectrumAnalyzer({
    enrollment_rate: 87.3,      // 0-100 value
    claims_processing: 95,       // 0-100 value
    data_quality: 99,            // 0-100 value
    audit_trail: 100,            // 0-100 value
    compliance: 98,              // 0-100 value
    system_stability: 96.2       // 0-100 value
});
```

**This is a CONTRADICTION:**
- Backend returns single metric with confidence_score
- Frontend expects 6 numeric dimension values
- **This needs clarification from user**

### 3.2 Frontend Architecture (Lines 802-900+ in chat-card4.html)

**Coherence Level Display:**
```javascript
function generateSpectrumAnalyzer(metrics) {
    const getColor = (value) => {
        if (value >= 90) return 'green';
        if (value >= 70) return 'yellow';
        return 'red';
    };

    // Coherence = average of all 6 dimensions
    const coherenceValue = Math.round(
        (metrics.enrollment_rate + 
         metrics.claims_processing + 
         metrics.data_quality + 
         metrics.audit_trail + 
         metrics.compliance + 
         metrics.system_stability) / 6
    );
    
    const coherenceColor = getColor(coherenceValue);
    
    // Determine status
    if (coherenceValue >= 90) status = 'COHERENT';
    else if (coherenceValue >= 70) status = 'WAVERING';
    else status = 'FRAGMENTED';
}
```

**Large Traffic Light (80x80px):**
- Displays coherence score with color (green/yellow/red)
- Shows emoji: ✓ (green), ⚠ (yellow), ✕ (red)
- Shows percentage number: "92%"
- Shows status text: "COHERENT", "WAVERING", or "FRAGMENTED"

**Clarity Spectrum Equalizer (6 Dimensions):**
- Grid of 6 metric cards
- Each card has:
  * Small 32x32px traffic light (colored circle)
  * Metric name: "Enrollment Rate", "Claims Processing", etc.
  * Percentage value: "87.3%"
  * Progress bar (horizontal, 4px height)
- On click: Expands breakdown panel below with:
  * Traffic light visual (3 stacked circles)
  * Equalizer visual (5 bars)
  * Data source links WITH remove buttons (✕)
  * Calculation logic explanation
  * Detailed breakdown statistics

**Three Collapsible Sections:**
1. **Coherence Level** - Single large light + coherence score
2. **Clarity Spectrum Equalizer** - 6 metric cards in grid
3. **Combined View** - Both coherence + spectrum together

All sections toggle with icon rotation (▶ collapsed → ▼ expanded)

### 3.3 Source Removal (UNIQUE TO CARDS 4-5)

**Card 4 Breakdown Panel with Removable Sources:**
```javascript
function showBreakdown(element, metric) {
    // Create breakdown panel with:
    // - Traffic light visual
    // - Equalizer visual
    // - Sources list:
    //   [Name](URL) ✕  ← Remove button present
    //   [Name2](URL) ✕
    // - Calculation logic
    // - Breakdown stats
}

function removeSourceFromSession(url, name) {
    // 1. Show confirmation modal
    // 2. On confirm: Add to sessionStorage.removedSources
    // 3. Remove source from DOM
    // 4. DON'T refetch data (session-only removal)
}
```

**CARDS 1-3 DO NOT HAVE remove buttons**
- Sources display as citations with links
- But no ✕ button to remove
- Cannot be removed by user

---

## PART 4: SYSTEM PROMPT RULES BY CARD

### Card 1 (Member) - Lines 588-627
- TOOL USAGE MANDATORY: call check_eligibility for every eligibility question
- Conditional lights: Extract _confidence_metadata.veracity if present
- No lights for internal-only data
- Escalation: Call 1-800-541-2831

### Card 2 (Provider) - Lines 629-670
- TOOL USAGE MANDATORY: call check_enrollment, validate_claim for provider questions
- Conditional lights: Extract _confidence_metadata.veracity if present
- No lights for internal-only data
- Escalation: eMedNY Support 1-800-343-9000

### Card 3 (PlanAdmin) - Lines 672-697
- ALWAYS show traffic light + LIVE URL combined for every response
- Data is ALWAYS external (MCO systems, network registries)
- Example: `🟢 HIGH | [Plan Name] Network System | [URL]`

### Card 4 (GovernmentStakeholder) - Lines 699-765
- HIPAA-compliant: aggregate-only, never individual records
- Confidence scoring: Show 🟢🟡🔴 for all metrics
- Include freshness and sources: "HIGH confidence (0.95) | Updated daily"
- Never query individual member or provider data

### Card 5 (DataAnalyst) - Lines 767-849
- Full data access allowed (names, SSNs, NPIs)
- Every query logged immutably
- Confidence and risk scoring: Z-scores, percentiles, peer context
- Show 🟢🟡🔴 for all analysis outputs
- Use statistical language: "4.7σ above peer average (99.8th percentile)"

---

## PART 5: CRITICAL CONTRADICTIONS & AMBIGUITIES FOUND

### 🚨 Contradiction 1: Card 4 Data Structure Mismatch
**Issue:** Backend returns single metric with confidence_score, but frontend expects 6 numeric dimensions.

From query_engine.py (actual backend):
```python
return {
    "metric": "Current Enrollment Rate",
    "value": 87.3,
    "confidence_score": 0.95,
    ...
}
```

From chat-card4.html (expected frontend input):
```javascript
generateSpectrumAnalyzer({
    enrollment_rate: 87.3,
    claims_processing: 95,
    data_quality: 99,
    audit_trail: 100,
    compliance: 98,
    system_stability: 96
})
```

**Question:** Does Card 4 backend actually return 6 dimensions, or just one metric?

### 🚨 Contradiction 2: Card 1-2 Confidence Score vs Card 4-5 Coherence
**Issue:** Cards 1-2 return `confidence_score` (single float), Cards 4-5 display `enrollment_rate`, `claims_processing`, etc.

Cards 1-2 schema: `confidence_score: float`  
Cards 4-5 expected: 6 separate numeric fields

Are these really using the same light system, or are they fundamentally different?

### 🚨 Contradiction 3: Card 3 System Prompt vs Implementation
**Issue:** System prompt says "ALWAYS show traffic light + LIVE URL combined", but Card 3 HTML doesn't actually render URLs in the clarity-light component.

System prompt (Line 685):
```
ALWAYS show traffic light (🟢🟡🔴) + LIVE URL combined for every response
```

Actual renderClarityLight function returns:
```html
<div class="clarity-light green">
    <span class="light-dot"></span>
    <span>Healthy</span>
</div>
```

Where does the URL go? Is it separate?

### 🚨 Ambiguity 1: Card 1-2 Conditional Lights Logic
**Unclear:** Exactly what determines "internal DB only" vs "external source"?

System prompt says: "If tool returns data WITHOUT confidence metadata (internal DB only): Answer directly, NO traffic light"

But all Card 1 tools (check_eligibility, check_recertification) return confidence_score. When would there be NO confidence metadata?

### 🚨 Ambiguity 2: Card 4-5 Source Removal Scope
**Unclear:** When user removes a source in Card 4, does it:
a) Remove from that specific query only (session temporary)?
b) Remove from all subsequent queries in session?
c) Affect backend permanently?

Current code suggests (a) - sessionStorage.removedSources, but this needs confirmation.

---

## PART 6: WHAT I UNDERSTAND WITH CONFIDENCE

✅ **Confirmed Facts:**

1. **All 5 cards use traffic lights** (🟢🟡🔴) for data representation
2. **Cards 1-2 show lights CONDITIONALLY** - only when querying external sources
3. **Card 3 shows lights ALWAYS** - on every plan/eligibility result
4. **Cards 4-5 show lights ALWAYS** - 1 coherence light + 6 dimension lights
5. **Card 3 sources have NO remove buttons** ❌
6. **Cards 4-5 sources HAVE remove buttons** (✕)
7. **System prompts explicitly tell Claude when to extract and display lights**
8. **_confidence_metadata is the wrapper Claude uses to see veracity**
9. **Backend confidence_score maps to Claude display** via: HIGH (≥0.85) | MEDIUM (≥0.60) | LOW (<0.60)
10. **Chat.py _prepare_tool_result_for_claude() does the extraction** (Lines 399-444)

---

## PART 7: WHAT NEEDS CLARIFICATION FROM USER

❓ Before deployment, please clarify:

1. **Card 4-5 Data Structure:** Does the backend actually return 6 separate metric values (enrollment_rate, claims_processing, etc.), or does it return single metrics that get synthesized into 6 dimensions on the frontend?

2. **Card 1-2 Conditional Logic:** What's the actual rule for when cards return confidence_score vs when they don't? All current Card 1-2 endpoints return confidence_score.

3. **Card 3 URL Display:** How are URLs combined with the clarity light in Card 3? Are they shown separately below the light, or as part of the same component?

4. **Card 4-5 Source Removal:** Is source removal:
   - Session-only (sessionStorage.removedSources)?
   - Or does it affect the backend/future queries?

5. **Light Visibility Rule:** Can I summarize it as:
   - Card 1: Only show light when calling external DB tools
   - Card 2: Only show light when calling external enrollment/claims tools
   - Card 3: Always show light (data always external)
   - Card 4-5: Always show lights (metrics always shown)

---

## SUMMARY: ACTUAL ARCHITECTURE

**The Real Light System:**
- All 5 cards display traffic lights
- Cards 1-2: Conditional display (external sources only)
- Cards 3-5: Always display lights
- Cards 1-2 return: `confidence_score` (0-1.0 float)
- Card 3 returns: `clarity` (string: "green"/"yellow"/"red")
- Cards 4-5 return: 6 numeric dimensions (0-100%)
- Claude extracts veracity from metadata and displays inline
- Cards 4-5 allow source removal, Cards 1-3 don't

**Before you ship anything, which of these ambiguities/contradictions need to be resolved first?**

