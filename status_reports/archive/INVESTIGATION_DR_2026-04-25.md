# TORQ-E System Investigation Report
## Design Reference (DR) - Internal Technical Findings

**Date:** 2026-04-25  
**Investigator:** Watson (Sous Chef Engineer)  
**Classification:** Internal Technical Analysis  
**Audience:** Architecture team only

---

## EXECUTIVE SUMMARY

Full system audit of TORQ-E codebase reveals:
- **1 CRITICAL BLOCKER:** Card 3 backend missing entirely
- **2 MEDIUM ISSUES:** Cards 1-2 don't use session context  
- **1 HOUSEKEEPING:** Archived files still in active folder
- **1 TIMELINE:** Card 5 designed but not built

---

## INVENTORY AUDIT

### File System Snapshot

**Frontend Files Found:**
- `login-card1.html` - Authentication gateway
- `login-card2.html` - Authentication gateway
- `login-card3.html` - Authentication gateway
- `login-card4.html` - Authentication gateway
- `login-card5.html` - Authentication gateway
- `chat-card1.html` - Member portal chat interface
- `chat-card2.html` - Provider claims chat interface
- `chat-card3.html` - Plan network chat interface
- `chat-card4.html` - Government governance chat interface (LOCKED v1.0.0)
- `chat-card5.html` - authenticity investigation chat interface
- `landing.html` - Home page (status banner removed ✓)
- `qualifier-card1.html` - ARCHIVED but still present
- `qualifier-card2.html` - ARCHIVED but still present
- `tutorial-*.html` (5 tutorials)
- `signup-info-card*.html` (enrollment help)
- `card4-5-header.html` - Shared header for Cards 4-5

**Backend Structure Found:**
```
/code/backend/
  ├── torq_e_backend.py (Flask app)
  ├── torq_e_mcp_server.py (MCP server)
  ├── requirements_torq_e.txt
  ├── .env.template
  └── Procfile

/card_1_umid/
  ├── routes.py (✓ exists)
  ├── schemas.py (✓ exists)
  ├── eligibility.py (✓ exists)
  ├── confidence.py (✓ exists)
  ├── river_path.py (✓ exists)
  └── __init__.py

/card_2_upid/
  ├── claims_routing.py (✓ exists)
  ├── fraud_detection.py (✓ exists)
  └── __init__.py

/card_3_uhwp/
  └── ❌ DOES NOT EXIST

/card_4_ushi/
  └── routes.py (✓ exists, locked)

/card_5_ubada/
  └── ❌ DESIGN ONLY (no implementation yet)
```

**Documentation Found:**
- `/docs/` - Complete journey blueprints (5 cards)
- `/code/specs/` - Technical specifications (5 cards)
- Architecture docs, infrastructure docs, testing docs

---

## INVESTIGATION FINDINGS

### FINDING #1: CRITICAL - Card 3 Backend Missing

**Location:** `/card_3_uhwp/` folder does not exist  
**Evidence:**
- `chat-card3.html` EXISTS (fully functional chat interface)
- Chat makes API calls to `http://localhost:3000/api/card3/programs`
- No corresponding backend route handler exists
- No Card 3 folder in codebase

**Current State - What Chat is Doing:**
```javascript
// Line 463 in chat-card3.html
const response = await fetch(`${BACKEND_URL}${API_BASE}/programs${params}`);
// Where API_BASE = '/api/card3'
// BACKEND_URL = 'http://localhost:3000'
```

**What Happens When Called:**
- API request fails (404 or connection refused)
- Chat catches error and falls back to `showMockPlans()`
- Mock data is returned (5 hardcoded plans)
- User never knows backend doesn't exist

**Mock Data Path - Line 495:**
```javascript
function showMockPlans(state = null, count = 5) {
    const mockPlans = [
        { name: 'Empire BlueCross BlueShield', type: 'HMO', network: 'Managed' },
        { name: 'UnitedHealthcare Community', type: 'PPO', network: 'Open Network' },
        { name: 'Molina Healthcare', type: 'HMO', network: 'Managed' },
        { name: 'Centene Local Plans', type: 'HMO', network: 'Managed' },
        { name: 'Aetna Medicaid', type: 'Flex PPO', network: 'Tiered' }
    ];
```

**Dependencies That Should Exist But Don't:**
- `card_3_uhwp/routes.py` - API endpoints for `/api/card3/programs`, `/api/card3/eligible-programs`
- `card_3_uhwp/schemas.py` - Request/response models
- Database models for Program/Plan data
- Query logic to fetch real plans by state

**Severity:** 🔴 **CRITICAL - Blocks production deployment**  
**Impact:** Chat works but on fake data. No actual plan data available.

---

### FINDING #2: MEDIUM - Card 1 & 2 Don't Use Session Context

**Issue Pattern:** Chat interfaces ask for information already in session

**Card 1 (UMID) Specific Evidence:**

User flow:
1. User logs in at `login-card1.html` with username/password OR UMID
2. Session is established (UMID should be in `sessionStorage`)
3. User redirected to `chat-card1.html`
4. Chat displays: "To look up your Medicaid coverage, I'll need: → Your Member ID or → Your Social Security Number"

**Problem:** Chat doesn't check if UMID is already in session before asking

**Code Location - chat-card1.html:**
- No check for `sessionStorage.getItem('umid')` or similar
- No conditional logic: "If user is logged in, use their UMID automatically"
- Always asks for identification

**Authentication Gap:**
- Backend has `RiverPathExecutor` (line 20 in card_1_umid/routes.py) for member lookup
- Backend has session token verification (implied by `Depends(get_db)`)
- Frontend chat doesn't leverage any of this session state

**Card 2 (UPID) Status:**
- `chat-card2.html` exists
- Not yet inspected but likely has same issue
- Backend has `ClaimValidator` and claims routing logic
- Frontend probably doesn't use session for provider authentication

**Severity:** 🟡 **MEDIUM - UX issue, not functionality broken**  
**Impact:** Users feel like their identity is not recognized; bad experience

---

### FINDING #3: HOUSEKEEPING - Qualifier Pages Still Present

**Files That Should Be Archived/Deleted:**
- `qualifier-card1.html`
- `qualifier-card2.html`

**Status:**
- Task #4 says "Archive qualifier-card1.html and qualifier-card2.html"
- Files physically still in `/TORQ-e/` folder
- Links removed from landing page (✓ landing.html doesn't reference them)
- NOT accessible from normal navigation

**Risk:** Low but present
- Direct URL access: `https://domain.com/qualifier-card1.html` still works
- Confuses codebase - dead code in active folder
- Unclear archive location

**Severity:** 🟢 **LOW - Cleanup task**  
**Impact:** None on functionality, minor on codebase clarity

---

### FINDING #4: TIMELINE - Card 5 Backend Not Started

**Status:** Design complete (TORQ-E_Card5_Rollout_Strategy.md created 2026-04-25)  
**Implementation Status:** NOT STARTED

**What Exists:**
- Rollout strategy document (6-week build plan)
- `chat-card5.html` (stub with welcome message)
- Specification (UBADA_SPECIFICATION.txt)
- Journey blueprint (UBADA_JOURNEY_BLUEPRINT.txt)

**What Doesn't Exist:**
- `/card_5_ubada/` backend folder
- API endpoints (no `/api/card5/create-case`, `/api/card5/add-evidence`, etc.)
- Database models for FraudSignal, FraudCase
- Pattern detection engine
- Investigator interface backend logic

**Timeline Impact:**
- Current: 0% implementation
- Planned: 6 weeks to GA
- Blocks: Card 5 deployment, full system deployment
- Dependency: Requires Cards 1-4 signals to be flowing

**Severity:** 📋 **PLANNING - Affects timeline, not current state**  
**Impact:** None yet; becomes critical in 2-3 weeks when Card 5 build should start

---

## ARCHITECTURAL OBSERVATIONS

### Pattern 1: Conversational vs. Authenticated Cards

**Cards 1-2 (Authenticated):**
- User logs in with credentials
- Session state established
- Chat should inherit that context
- Currently: Asks for re-authentication in chat

**Cards 3-5 (Conversational):**
- Users ask open-ended questions
- Chat routes based on intent + context
- Card 3: Fixed to use context-driven routing ✓
- Card 4: Already uses context-driven routing ✓
- Card 5: Will need same pattern

**Gap:** Cards 1-2 haven't adopted session-context pattern yet

### Pattern 2: Mock Data Fallback

**Current Implementation:**
- All chats have mock data fallback
- If API fails → return mock data
- Users don't know difference

**Examples:**
- Card 1: `showMockEligibility()` function
- Card 3: `showMockPlans()` function (just fixed count display)
- Card 4: `getOfflineMetrics()` function

**Problem:** Card 3 backend doesn't exist, so fallback is permanent

### Pattern 3: API Endpoint Structure

**Card 1 Endpoints (exist):**
```
POST /api/card1/lookup
POST /api/card1/eligibility-check
POST /api/card1/recertification-status
POST /api/card1/document-upload
POST /api/card1/income-change
GET  /api/card1/health
```

**Card 2 Endpoints (implied, needs verification):**
```
POST /api/card2/submit-claim
POST /api/card2/validate-claim
GET  /api/card2/claim-status
```

**Card 3 Endpoints (MISSING):**
```
GET  /api/card3/programs (by state)
GET  /api/card3/eligible-programs (by member)
POST /api/card3/plan-comparison
```

**Card 4 Endpoints (exist):**
```
POST /api/card4/metrics
POST /api/card4/inauthenticity-signals
POST /api/card4/data-quality
GET  /api/card4/governance-log
```

**Card 5 Endpoints (DESIGNED but NOT IMPLEMENTED):**
```
POST /api/card5/create-case
POST /api/card5/add-evidence
GET  /api/card5/case/{id}
GET  /api/card5/cases
POST /api/card5/escalate-case
```

---

## SUMMARY TABLE

| Case | Component | Status | Severity | Root Cause |
|------|-----------|--------|----------|-----------|
| A | Card 3 Backend | ❌ Missing | 🔴 CRITICAL | Never built |
| B | Card 1 Session | ⚠️ Broken UX | 🟡 MEDIUM | Chat doesn't use `sessionStorage` |
| B | Card 2 Session | ❓ Unknown | 🟡 MEDIUM | Not inspected |
| C | Qualifier Pages | 📋 Orphaned | 🟢 LOW | Not deleted/archived |
| D | Card 5 Backend | 📋 Planned | 📋 N/A | In 6-week roadmap |

---

## NEXT STEPS (For Chef's Decision)

**Immediate (Case A):**
- Decide Card 3 backend approach (new routes vs. mock endpoints)
- Create `/card_3_uhwp/` folder structure
- Implement program query logic

**Short-term (Case B):**
- Inspect `chat-card2.html` for session issues
- Refactor Cards 1-2 chat to check `sessionStorage` first
- Apply session-context pattern (similar to Card 3 fix)

**Cleanup (Case C):**
- Delete or archive qualifier pages

**Timeline (Case D):**
- No action needed now
- Card 5 build starts after Cards 1-3 resolved

---

**Investigation Complete. Awaiting Chef's orders on Case Priority.**

