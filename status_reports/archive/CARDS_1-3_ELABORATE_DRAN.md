# CARDS 1-3 ELABORATE INTEGRATION
## Design Reference & Implementation Plan

**Date:** 2026-04-25  
**Phase:** Frontend UI Layer - Clarity Light + Elaborate Buttons  
**Pattern:** Concise answer → Click for details  
**Order:** Card 3 → Card 1 → Card 2

---

## WHAT'S BEING BUILT

### For Each Card (1, 2, 3)

**Response structure (from API):**
```json
{
  "clarity": "green|yellow|red",
  "clarity_metric": 92.5,
  "sources": [
    { "name": "...", "url": "...", "timestamp": "..." }
  ],
  "message": "Concise answer here",
  "elaboration": "Detailed explanation here..."
}
```

**Frontend renders:**
```html
<!-- 1. Concise message (primary) -->
<p>Concise answer here</p>

<!-- 2. Clarity light (visual status) -->
<div class="clarity-light green">
  <div class="light-dot"></div>
  <span>Healthy</span>
</div>

<!-- 3. Source citations (fine print) -->
<div class="sources-citation">
  <a href="[url]">Network Registry</a> | 2026-04-25
</div>

<!-- 4. Elaborate button -->
<button onclick="toggleElaborate(this)">📖 Elaborate</button>

<!-- 5. Elaboration (hidden, toggle on click) -->
<div class="elaboration" style="display: none;">
  Detailed explanation here...
</div>
```

---

## CARD-BY-CARD MAPPING

### CARD 3 (WHUP - Plan Network Management)

**API Response includes:**
- `clarity`: Network adequacy status (green/yellow/red based on 75%-85%-100% thresholds)
- `sources`: [Network Registry, Plan Formulary Database]
- `elaboration`: "Network adequacy measures whether the plan's provider network meets state requirements..."

**Frontend Response Functions to Update:**
1. `handlePlanSearch()` - "Show me plans"
   - Concise: Top X plans, network status
   - Clarity: Green/Yellow/Red (from `data.clarity`)
   - Sources: Fixed (Network Registry, Formulary)
   - Elaborate: Explain adequacy score by plan

2. `handleEligibilityCheck()` - "Am I eligible?"
   - Concise: You qualify for X plans
   - Clarity: Green (eligible) / Red (not eligible)
   - Sources: Fixed (Network Registry, Member eligibility)
   - Elaborate: How eligibility was determined

3. `handlePlanComparison()` - "Compare these plans"
   - Concise: Comparison breakdown
   - Clarity: Green (all adequate) / Yellow (mixed) / Red (concerns)
   - Sources: Fixed (Network Registry, Formulary, CMS Ratings)
   - Elaborate: Details on each metric

4. `handleContextualQuestion()` - "Which is best?"
   - Concise: Recommendation based on context
   - Clarity: Green (recommended) / Yellow (consider both)
   - Sources: Fixed (Network Registry)
   - Elaborate: Why this recommendation

5. `getHelpMessage()` & `handleClarification()`
   - Concise: Help text
   - NO clarity light (informational only)
   - Elaborate: Optional

---

### CARD 1 (UMID - Member Eligibility)

**Backend needs to add to responses:**
- `clarity`: Eligibility status (green=active, red=inactive, yellow=pending)
- `sources`: [Medicaid State Database, Income Verification System]
- `elaboration`: "How we determined your eligibility..."

**Chat Functions to Update (chat-card1.html):**
1. Login flow → Dashboard → Show member info
   - Concise: "Your coverage: ACTIVE until 12/31/26"
   - Clarity: Green light
   - Sources: Fixed (State DB, Income verify)
   - Elaborate: "We verified your SSN, income, and household status..."

2. Recertification check
   - Concise: "Recert due 06/15/26 (52 days)"
   - Clarity: Green (on-track) / Yellow (alert) / Red (overdue)
   - Sources: Fixed (State DB)
   - Elaborate: "Based on your last certification date and state requirements..."

3. Income change check
   - Concise: "New income $X/month. Coverage impact: NONE"
   - Clarity: Green (no impact) / Yellow (possible impact) / Red (loss of coverage)
   - Sources: Fixed (Income limits, State DB)
   - Elaborate: "Your new income is 45% of the state limit. You remain eligible because..."

---

### CARD 2 (UPID - Provider Claims)

**Backend needs to add to responses:**
- `clarity`: Claims processing health (green=good, yellow=review needed, red=critical)
- `sources`: [Claims Database, authenticity verification Engine]
- `elaboration`: "How we processed your claim..."

**Chat Functions to Update (chat-card2.html):**
1. Claim submission
   - Concise: "Claim submitted. Status: PENDING REVIEW"
   - Clarity: Green (processing normally) / Yellow (under review) / Red (rejected)
   - Sources: Fixed (Claims DB, inauthenticity engine)
   - Elaborate: "Your claim is in our standard review queue. Expected decision: 5-7 days..."

2. Claim validation
   - Concise: "Member is eligible. Claim is in-network."
   - Clarity: Green (valid) / Yellow (needs verification) / Red (invalid)
   - Sources: Fixed (Claims DB, Member eligibility DB)
   - Elaborate: "We verified the member's enrollment, plan coverage, and provider network status..."

3. authenticity verification
   - Concise: "No inauthenticity signals detected."
   - Clarity: Green (clear) / Yellow (minor concerns) / Red (high risk)
   - Sources: Fixed (authenticity verification engine, Claims DB)
   - Elaborate: "We scanned for: duplicate claims, coding anomalies, member history patterns..."

---

## CSS ADDITIONS (All Three Cards)

```css
.clarity-light {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin: 12px 0;
    padding: 8px 12px;
    background: #f5f5f5;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
}

.clarity-light.green .light-dot {
    background: #22c55e;
}

.clarity-light.yellow .light-dot {
    background: #eab308;
}

.clarity-light.red .light-dot {
    background: #ef4444;
}

.light-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: inline-block;
}

.sources-citation {
    font-size: 11px;
    color: #666;
    margin: 8px 0;
    border-top: 1px solid #eee;
    padding-top: 8px;
    font-style: italic;
}

.sources-citation a {
    color: #2d6a4f;
    text-decoration: none;
    border-bottom: 1px dotted #2d6a4f;
}

.sources-citation a:hover {
    text-decoration: underline;
}

.elaborate-btn {
    background: none;
    border: none;
    color: #2d6a4f;
    cursor: pointer;
    font-size: 13px;
    text-decoration: none;
    padding: 4px 0;
    margin-top: 8px;
    font-weight: 500;
}

.elaborate-btn:hover {
    text-decoration: underline;
}

.elaboration {
    margin-top: 12px;
    padding: 12px;
    background: #f9f9f9;
    border-left: 3px solid #2d6a4f;
    border-radius: 4px;
    font-size: 13px;
    line-height: 1.6;
    color: #555;
}

.elaboration strong {
    color: #2d6a4f;
}
```

---

## JAVASCRIPT HELPER (All Three Cards)

```javascript
function toggleElaborate(btn) {
    const elaboration = btn.nextElementSibling;
    if (elaboration && elaboration.classList.contains('elaboration')) {
        const isHidden = elaboration.style.display === 'none';
        elaboration.style.display = isHidden ? 'block' : 'none';
        btn.textContent = isHidden ? '📖 Hide Details' : '📖 Elaborate';
    }
}

function renderClarityLight(clarity) {
    const colorMap = {
        'green': '🟢',
        'yellow': '🟡',
        'red': '🔴'
    };
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

function renderSources(sources) {
    if (!sources || sources.length === 0) return '';
    const links = sources.map(s => 
        `<a href="${s.url}" target="_blank">${s.name}</a>`
    ).join(' | ');
    return `<div class="sources-citation">${links}</div>`;
}

function renderElaborateButton(elaborationText) {
    if (!elaborationText) return '';
    return `<button class="elaborate-btn" onclick="toggleElaborate(this)">📖 Elaborate</button>
            <div class="elaboration" style="display: none;">${elaborationText}</div>`;
}
```

---

## EXECUTION PLAN

**Card 3 (90 min):**
1. Add CSS for clarity light, sources, elaborate
2. Update handlePlanSearch() - add clarity + sources + elaborate
3. Update handleEligibilityCheck() - add clarity + sources + elaborate
4. Update handlePlanComparison() - add clarity + sources + elaborate
5. Update handleContextualQuestion() - add clarity + sources + elaborate
6. Test: Verify clarity light colors, source links work, elaborate toggles

**Card 1 (120 min):**
1. Find chat-card1.html
2. Add CSS (same as Card 3)
3. Add session context check at init
4. Update response handlers to include clarity + sources + elaborate
5. Update Card 1 backend routes to include clarity + sources in responses
6. Test: Session usage, clarity light, elaborate toggle

**Card 2 (120 min):**
1. Find chat-card2.html
2. Add CSS (same as Card 3)
3. Add session context check at init
4. Update response handlers to include clarity + sources + elaborate
5. Update Card 2 backend routes to include clarity + sources in responses
6. Test: Session usage, clarity light, elaborate toggle

**Then:**
- Deploy to Railway
- Test end-to-end all three cards
- Verify Clarity lights show correctly
- Verify elaborate toggles work
- Verify source citations are clickable

---

**READY TO BUILD: Cards 1-3 Elaborate Integration + Clarity Lights + Session Context**

