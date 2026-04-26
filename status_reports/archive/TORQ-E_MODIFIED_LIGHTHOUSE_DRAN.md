# TORQ-E Modified Lighthouse Architecture
## Design Reference & Architecture Notes (DR;AN)

**Date:** 2026-04-25  
**Status:** LIGHTHOUSE ARCHITECTURE ESTABLISHED  
**Author:** Watson (Sous Chef Engineer)  
**Classification:** Internal Technical Architecture  
**Audience:** Architecture team

---

## EXECUTIVE SUMMARY

TORQ-E now operates on a **tiered lighthouse system** where Card 4 (USHI) serves as the complete reference architecture, Card 5 replicates Card 4's pattern with different data, and Cards 1-3 use a **simplified "Clarity" variant**.

**Three Tiers of Implementation:**
1. **Full Lighthouse (Card 4 & Card 5):** Three-tier Spectrum Analyzer, user-removable sources, session-level governance
2. **Modified Lighthouse (Cards 1-3):** Single Clarity traffic light, fixed source URLs, director-level control only
3. **No lighthouse (pending Cases):** Currently architectural decisions pending

---

## THE LIGHTHOUSE PRINCIPLE

### Card 4: The Reference (🔒 LOCKED v1.0.0)

**What Makes It Complete:**
- **Frontend:** Context-driven routing, Spectrum Analyzer (three-tier), Elaborate buttons, session state awareness
- **Backend:** 5 core endpoints, health checks, HIPAA-compliant aggregate metrics, immutable audit logging
- **Architecture:** Signal strength across 6 dimensions, traffic-light visualization, user-controlled source removal with confirmation
- **Validation:** All 6 test queries passing, no known bugs, production-ready
- **Pattern:** Users can see what's happening, understand why, and remove individual sources from their session

**Core Patterns to Replicate:**
```
Context-Driven Routing:
  IF explicit_user_action → handle_specific_action()
  ELSE IF conversation_context → handle_contextual_question()
  ELSE → generic_help()

Every Response Includes:
  1. Spectrum Analyzer (three-tier: Coherence, Stability, Combined)
  2. Elaborate button (📖 shows metrics explanation)
  3. Source removal UI (X button to remove sources from session)

Session Governance:
  - SessionStorage tracks removed sources
  - Confirmation modal on removal ("Are you sure?")
  - System respects user preference in current session
  - Director can permanently remove (v1.1 feature)

Immutable Audit:
  - Every action timestamped
  - Write-once append-only logging
  - HIPAA 42 CFR Part 455 compliant
```

---

## CARD 5: THE DUPLICATE PATTERN

### Architecture: Card 4 → Fraud Investigation Data

Card 5 will be **structurally identical to Card 4** but with fraud/investigation domain data.

**What Changes:**
- Data source: Fraud signals, pattern detection, investigator actions (instead of governance metrics)
- Signal dimensions: Fraud risk, behavioral anomaly, financial impact, temporal pattern, case severity, investigation status
- Users: Fraud investigators, data analysts (instead of government stakeholders)
- Audit focus: Investigation trail (every data access, correction, case modification tracked)

**What Stays Identical:**
- Frontend pattern: Context-driven routing
- Visualization: Full three-tier Spectrum Analyzer (Coherence, Stability, Combined)
- UX: Elaborate buttons, source removal, session awareness
- Backend: Health checks, immutable audit logging, signal strength calculation
- Governance: User-removable sources at session level, director-permanent removal (v1.1)

**Implementation Timeline:** 6 weeks post Cards 1-3 completion

---

## CARDS 1-3: MODIFIED LIGHTHOUSE

### Simplified Architecture: Single Clarity Traffic Light

Cards 1-3 operate as **authenticated, state-aware systems** (vs. Card 4-5's conversational systems). They require a simplified lighthouse that shows system health without the conversational complexity.

**What Cards 1-3 Are:**
- **Card 1 (UMID):** Member authentication → Shows member eligibility/coverage status
- **Card 2 (UPID):** Provider authentication → Shows claims processing health
- **Card 3 (WHUP):** Plan network conversations → Shows plan adequacy/network status

**Modified Lighthouse Design:**

```
┌─────────────────────────────────────┐
│  CLARITY TRAFFIC LIGHT               │
│  🟢 System Healthy                   │
│  🟡 Degraded                         │
│  🔴 Critical                         │
└─────────────────────────────────────┘

Below Light:
├─ Source Citation 1 (URL) | Timestamp
├─ Source Citation 2 (URL) | Timestamp
└─ Source Citation 3 (URL) | Timestamp

NO REMOVAL UI FOR USERS
(Director-controlled only)
```

**Key Differences from Card 4:**
1. **No Coherence Level** - Too much detail for authenticated use cases
2. **No Stability Strength** - Not needed; sources are fixed
3. **No Combined View** - Single Clarity light is sufficient
4. **No X button** - Users cannot remove sources
5. **No Elaborate toggle** - Sources are static
6. **Fixed URLs** - URLs come from director-approved sources only
7. **Director-level only** - When director modifies sources, ALL users see new set; no session-level variation

**Source Management:**
- Sources are **fixed by director/system** (e.g., state Medicaid database, provider network registry, plan actuarial data)
- Users see these sources but **cannot modify**
- If source needs removal → Director makes decision → All users see updated set
- No ephemeral session-level removal like Card 4

**Implementation for Each Card:**

| Card | Clarity Light Measures | Sources Display | User Control | Director Control |
|------|----------------------|-----------------|--------------|-----------------|
| 1 (UMID) | Member eligibility, enrollment status, recertification risk | Medicaid record, verification timestamp, income documentation | View only | Can change data source verification method |
| 2 (UPID) | Claims processing health, validation pass rate, fraud detection sensitivity | Claims database, fraud engine version, provider verification timestamp | View only | Can adjust fraud detection thresholds |
| 3 (WHUP) | Network adequacy, plan compliance, provider count by specialty | Network registry, plan formulary version, CMS file timestamp | View only | Can update network definitions, formulary versions |

---

## CASE PRIORITIZATION

### CRITICAL: Case A — Card 3 Backend Missing
**Severity:** 🔴 **BLOCKS PRODUCTION**

**Current State:**
- `chat-card3.html` exists and is functional
- Chat makes API calls to `/api/card3/programs`, `/api/card3/eligible-programs`
- **Backend routes DO NOT EXIST**
- Fallback to mock data (5 hardcoded plans) is permanent

**What Needs Building:**
```python
/card_3_uhwp/
├── routes.py (NEW)
│   ├── GET /api/card3/programs (by state) → Returns all plans in state
│   ├── GET /api/card3/eligible-programs (by member) → Returns plans eligible for member
│   └── POST /api/card3/plan-comparison → Compare selected plans
├── schemas.py (NEW)
│   ├── Program (name, type, network, enrollment, adequacy_score)
│   └── PlanComparison request/response
├── database.py (NEW)
│   └── Query logic for plan data
└── __init__.py
```

**Implementation Roadmap:**
1. Create folder structure `/card_3_uhwp/`
2. Define database schema for Program/Plan data
3. Implement routes with real data queries (or seed data if DB not ready)
4. Integrate with existing Flask backend
5. Test with chat-card3.html
6. Add Clarity traffic light visualization (modified lighthouse)

**Success Criteria:**
- Real data flowing from backend (not mock)
- Chat receives actual plans based on state/member parameters
- Clarity traffic light shows network adequacy (🟢/🟡/🔴)
- Source citations display (network registry, formulary version)

---

### MEDIUM: Case B — Cards 1-2 Session Context
**Severity:** 🟡 **UX ISSUE**

**Current State:**
- User logs in with credentials (UMID for Card 1, provider credentials for Card 2)
- Session established with user identity
- Chat asks "What's your Member ID?" or re-authenticates provider
- **System doesn't use session state** in chat interface

**What Needs Fixing:**
- Card 1: Read `sessionStorage.getItem('umid')` at chat start
  - If logged in: "Welcome back, member. Your ID is [UMID]. What can I help with?"
  - If not logged in: "Please log in first"
- Card 2: Read `sessionStorage.getItem('provider_id')` at chat start
  - If logged in: "Welcome [Provider Name]. What claims need help?"
  - If not logged in: "Please authenticate"

**Implementation Roadmap:**
1. Locate chat files for Cards 1-2 (backend templates? dynamic serving?)
2. Add session check at chat initialization
3. Use session identity in context-driven routing
4. Add Clarity traffic light for Card 1 (eligibility status) and Card 2 (claims health)
5. Link to appropriate sources (Medicaid record, claims database)

**Success Criteria:**
- Users don't re-authenticate after login
- Chat recognizes logged-in user immediately
- Clarity light shows user-specific status
- No mock fallback for authenticated users

---

### LOW: Case C — Housekeeping
**Severity:** 🟢 **CLEANUP**

**Files to Archive/Delete:**
- `qualifier-card1.html` (orphaned, not in landing.html navigation)
- `qualifier-card2.html` (orphaned, not in landing.html navigation)

**Action:** Delete from `/TORQ-e/` folder or move to `/archive/` subfolder

---

### TIMELINE: Case D — Card 5 Build
**Severity:** 📋 **FUTURE**

**Current State:**
- Design complete (Rollout Strategy documented)
- Frontend stub exists (`chat-card5.html`)
- Backend NOT STARTED

**Start After:** Cards 1-3 are complete and deployed

**Implementation:** Will follow Card 4 pattern exactly (full three-tier Spectrum Analyzer, user-removable sources, immutable audit trail)

---

## ARCHITECTURAL DECISIONS

### Decision 1: Lighthouse Tiering

**Chosen:** Three-tier implementation model
- **Tier 1 (Full):** Card 4 (governance) + Card 5 (fraud) — Complete Spectrum Analyzer, user agency
- **Tier 2 (Modified):** Cards 1-3 (authenticated) — Single Clarity light, fixed sources, director-controlled
- **Rationale:** Cards 4-5 are conversational/exploratory (users need flexibility). Cards 1-3 are state-aware/authenticated (users need certainty, not choice).

### Decision 2: Source Permanence

**Chosen:** Cards 1-3 sources are director-controlled, not user-removable
- **Why:** Members/Providers need confidence in data source. One person removing a source shouldn't affect another's trust.
- **Director Removal:** When a source truly needs replacement, director approves system-wide → ALL users see new source
- **Card 4 Different:** Government stakeholders investigating patterns need to test hypotheses (remove one source, see if pattern holds). Session-level removal makes sense.

### Decision 3: Visualization Simplicity

**Chosen:** Single traffic light for Cards 1-3, three-tier for Cards 4-5
- **Why:** Simplicity matches use case. Card 1 member just needs: "Is my coverage active?" (🟢/🔴). Card 4 investigator needs: "Where exactly is the problem?" (three-tier breakdown).

---

## IMPLEMENTATION ROADMAP

### Immediate (Week 1)
**Case A: Build Card 3 Backend**
- Create `/card_3_uhwp/routes.py` with program queries
- Implement Clarity traffic light (network adequacy metric)
- Add source citations (network registry, formulary version)
- Replace mock data with real queries
- Test end-to-end with chat-card3.html

### Short-term (Week 2-3)
**Case B: Fix Cards 1-2 Session Context**
- Locate Card 1 & 2 chat files
- Add session initialization checks
- Implement Clarity traffic light for member eligibility (Card 1) and claims health (Card 2)
- Add source citations
- Apply context-driven routing with session awareness

### Cleanup (Week 3)
**Case C: Archive Qualifier Pages**
- Delete or move `qualifier-card1.html`, `qualifier-card2.html`

### Future (Week 4+)
**Case D: Card 5 Build Plan**
- Mirror Card 4 architecture
- Implement fraud signal dashboard
- Build investigator interface
- 6-week timeline before GA

---

## CODE PATTERNS: CARDS 1-3 CLARITY LIGHT

### Frontend Pattern (All Three Cards)

```javascript
// Initialize with session
const userIdentity = sessionStorage.getItem('umid') || 
                    sessionStorage.getItem('provider_id');

if (!userIdentity) {
  showLoginRequired();
  return;
}

// Context-driven routing (same as Card 4)
if (explicit_user_action) {
  handleAction();
} else if (conversation_context) {
  handleContextualQuestion();
} else {
  showHelp();
}

// Every response includes Clarity light
function renderClarityLight(status) {
  const colors = { green: '#22c55e', yellow: '#eab308', red: '#ef4444' };
  html += `
    <div class="clarity-light">
      <div class="traffic-light" style="background: ${colors[status]}"></div>
      <span>${status === 'green' ? '✓ Healthy' : 
              status === 'yellow' ? '⚠ Degraded' : '✗ Critical'}</span>
    </div>
  `;
  
  // Always include fixed source citations (NO REMOVAL UI)
  html += `
    <div class="sources">
      <a href="${source1.url}" target="_blank">${source1.name}</a> | ${source1.timestamp}
      <a href="${source2.url}" target="_blank">${source2.name}</a> | ${source2.timestamp}
    </div>
  `;
  
  return html;
}
```

### Backend Pattern (All Three Cards)

```python
# Card 1 example - same pattern for Cards 2-3
@router.get("/api/card1/member-status/{umid}")
async def get_member_status(umid: str):
    """Return member eligibility status with Clarity metric"""
    try:
        member = db.get_member(umid)
        enrollment_status = "active" if member.is_enrolled else "inactive"
        
        clarity_light = "green" if enrollment_status == "active" else "red"
        
        return {
            "umid": umid,
            "clarity": clarity_light,  # Traffic light status
            "enrollment_status": enrollment_status,
            "recertification_date": member.recert_date,
            "sources": [  # Fixed sources, director-controlled
                {
                    "name": "Medicaid State Database",
                    "url": "https://medicaid.state.ny.gov/verification",
                    "timestamp": "2026-04-25T10:30:00Z"
                },
                {
                    "name": "Income Verification System",
                    "url": "https://income-verify.state.ny.gov",
                    "timestamp": "2026-04-24T15:00:00Z"
                }
            ]
        }
    except Exception as e:
        return {
            "clarity": "red",
            "error": "Unable to verify status",
            "sources": get_default_sources()  # Director-set default sources
        }
```

---

## SUCCESS METRICS

### Card 3 Backend (Case A)
- ✅ Real data returned (not mock)
- ✅ Clarity light reflects actual network status
- ✅ Source citations display with timestamps
- ✅ No JavaScript errors in fallback
- ✅ Chat end-to-end flow works

### Cards 1-2 Session (Case B)
- ✅ Users don't re-authenticate after login
- ✅ Session identity used in chat routing
- ✅ Clarity light shows user-specific status
- ✅ Sources are fixed and trustworthy
- ✅ No hardcoded question-type routing

### System Overall
- ✅ Card 4 remains locked reference (no changes)
- ✅ Cards 1-3 adopt modified lighthouse pattern consistently
- ✅ Card 5 ready for 6-week build (design approved)
- ✅ All documentation up-to-date (DR;AN for each card)

---

## NEXT STEP

**Ready to build Case A (Card 3 backend).**

Awaiting Chef's confirmation to proceed.

---

**Status:** 🔒 CARD 4 LOCKED | ✅ CARD 3 ROUTED | 🔧 CARDS 1-2 IDENTIFIED | 📋 CARD 5 DESIGNED  
**Architecture:** Tiered Lighthouse Established | Modified Clarity System Defined | Implementation Roadmap Ready

