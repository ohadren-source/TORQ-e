# TORQ-E FILE SCHEME
## Complete Directory Structure & Navigation Map

**Generated:** 2026-04-25  
**Purpose:** Self-serve navigation without asking Chef

---

## ROOT LEVEL FILES

```
/TORQ-e/
├── landing.html                    [HOME PAGE - 5 card selector]
├── main.py                         [FastAPI app - route registration]
├── models.py                       [Database models - all cards]
├── database.py                     [Database session/config]
├── config.py                       [Environment/settings]
├── chat.py                         [Chat router]
├── governance.py                   [Governance router]
├── source_management.py            [Source removal/audit]
├── audit_logging.py                [Immutable audit trail]
├── rbac.py                         [Role-based access control]
├── pii_encryption.py               [Data encryption]
├── compliance_integration.py        [HIPAA compliance]
├── test_card5.py                   [Card 5 tests]
├── test_integration.py             [Integration tests]
```

---

## CARD 1: UMID (Member Eligibility)

### Frontend (HTML)
```
├── login-card1.html                [Login/authentication]
├── chat-card1.html                 [MAIN CHAT - needs Elaborate button]
├── tutorial-card1.html             [How-to guide]
├── signup-info-card1.html          [Enrollment help]
├── qualifier-card1.html            [ARCHIVED - delete/archive]
```

### Backend (Python)
```
/card_1_umid/
├── __init__.py                     [Router export]
├── routes.py                       [6 endpoints: lookup, eligibility, recert, documents, income, health]
├── schemas.py                      [Pydantic request/response models]
├── river_path.py                   [Member identification algorithm]
├── eligibility.py                  [Eligibility determination logic]
├── confidence.py                   [Confidence scoring]
```

### What Needs Doing
- [ ] Add Clarity traffic light to responses (eligibility status → green/yellow/red)
- [ ] Add fixed source citations (Medicaid record, income verification)
- [ ] Add Elaborate button to chat responses (concise first, then button)
- [ ] Chat-card1.html needs to check sessionStorage.getItem('umid') at init

---

## CARD 2: UPID (Provider Claims)

### Frontend (HTML)
```
├── login-card2.html                [Login/authentication]
├── chat-card2.html                 [MAIN CHAT - needs Elaborate button]
├── tutorial-card2.html             [How-to guide]
├── signup-info-card2.html          [Provider enrollment help]
├── qualifier-card2.html            [ARCHIVED - delete/archive]
```

### Backend (Python)
```
/card_2_upid/
├── __init__.py                     [Router export]
├── routes.py                       [Endpoints: lookup, enrollment/check, claims/validate, claims/submit, claims/status, fraud/analyze]
├── schemas.py                      [Pydantic models]
├── claims_routing.py               [Claims routing logic]
├── fraud_detection.py              [Fraud detection]
├── provider_lookup.py              [Provider identification]
```

### What Needs Doing
- [ ] Add Clarity traffic light to responses (claims health → green/yellow/red)
- [ ] Add fixed source citations (Claims database, fraud engine)
- [ ] Add Elaborate button to chat responses
- [ ] Chat-card2.html needs to check sessionStorage.getItem('provider_id') at init

---

## CARD 3: UHWP (Plan Network Management)

### Frontend (HTML)
```
├── login-card3.html                [Login/authentication]
├── chat-card3.html                 [MAIN CHAT - needs Elaborate button]
├── tutorial-card3.html             [How-to guide]
```

### Backend (Python) - JUST BUILT
```
/card_3_uhwp/
├── __init__.py                     [✅ Router export]
├── routes.py                       [✅ 4 endpoints: health, programs, eligible-programs, plan-comparison]
├── schemas.py                      [✅ Pydantic models with Clarity light + sources]
```

### What Needs Doing
- [ ] Add Elaborate button to chat-card3.html responses (concise first, then button)
- [ ] Chat should render:
  - Clarity light (🟢/🟡/🔴)
  - Fixed source citations (Network Registry, Formulary DB)
  - Elaborate button → Show adequacy breakdown by plan

---

## CARD 4: USHI (Government Governance)

### Frontend (HTML)
```
├── login-card4.html                [Login/authentication]
├── chat-card4.html                 [✅ COMPLETE - Spectrum Analyzer + Elaborate + source removal]
├── card4-dashboard.html            [Dashboard view]
├── tutorial-card4.html             [How-to guide]
├── card4-5-header.html             [Shared header for Cards 4-5]
├── faq-card4-5.html                [FAQ]
├── documentation-card4-5.html      [Documentation]
```

### Backend (Python)
```
/card_4_ushi/
├── __init__.py                     [Router export]
├── routes.py                       [✅ 5 endpoints: metrics, fraud-signals, data-quality, governance-log, flag-issue]
├── query_engine.py                 [Query execution]
```

### Status
- ✅ **LOCKED v1.0.0** - Complete, validated, production-ready
- ✅ Three-tier Spectrum Analyzer (Coherence, Stability, Combined)
- ✅ Elaborate buttons on all responses
- ✅ User-removable sources (session-level + confirmation modal)
- ✅ Immutable audit trail

---

## CARD 5: UBADA (Fraud Investigation)

### Frontend (HTML)
```
├── login-card5.html                [Login/authentication]
├── chat-card5.html                 [Welcome message stub]
├── tutorial-card4-5.html           [Shared tutorial with Card 4]
├── card4-5-header.html             [Shared header]
```

### Backend (Python)
```
/card_5_ubada/
├── __init__.py                     [Router export]
├── routes.py                       [Endpoints: create-case, add-evidence, get-case, get-cases, escalate]
├── query_engine.py                 [Query execution]
```

### Status
- ✅ Backend ready (routes + schemas)
- ⏳ Frontend development: 6-week roadmap
- Will duplicate Card 4's architecture (three-tier Spectrum Analyzer)

---

## SUPPORTING INFRASTRUCTURE

### Code Backend (Flask)
```
/code/backend/
├── torq_e_backend.py               [Flask app - reading engines & MCP protocols]
├── torq_e_mcp_server.py            [MCP server]
├── requirements_torq_e.txt         [Python dependencies]
├── .env.template                   [Environment template]
├── Procfile                        [Railway deployment]
```

### Specifications & Documentation
```
/code/specs/
├── UMID_SPECIFICATION.txt
├── UPID_SPECIFICATION.txt
├── UHWP_SPECIFICATION.txt
├── USHI_SPECIFICATION.txt
├── UBADA_SPECIFICATION.txt

/docs/
├── ARCHITECTURE_TECHNICAL.md
├── DATABASE_README.md
├── ENV_CONFIG_AND_MOCKING.md
├── TEST_CASES_COMPREHENSIVE.md
├── READING_ENGINE_SOURCES_ROADMAP.md
├── THE_INFRASTRUCTURE_OF_ERASURE.md

/docs/journeys/
├── UMID_JOURNEY_BLUEPRINT.txt
├── UPID_JOURNEY_BLUEPRINT.txt
├── UHWP_JOURNEY_BLUEPRINT.txt
├── USHI_JOURNEY_BLUEPRINT.txt
├── UBADA_JOURNEY_BLUEPRINT.txt
```

### Branding
```
/branding/
├── logo/
│   └── TdST.png                    [Logo image]
├── BRANDING.md                     [Branding guidelines]
├── FAVICON_SETUP.md                [Favicon setup]
```

---

## FRONT-END WORK QUEUE (Cards 1-3 Elaborate Integration)

### Priority Order (Chef's directive)

**1. CARD 3** → `/TORQ-e/chat-card3.html`
- File exists ✅
- Backend exists ✅
- Needs: Elaborate button implementation

**2. CARD 1** → `/TORQ-E/chat-card1.html`
- File exists ✅
- Backend exists ✅
- Needs: Session context + Clarity light + Elaborate button

**3. CARD 2** → `/TORQ-E/chat-card2.html`
- File exists ✅
- Backend exists ✅
- Needs: Session context + Clarity light + Elaborate button

---

## FILE PATHS FOR SCRIPT AUTOMATION

**If running bash scripts:**

| Purpose | Path |
|---------|------|
| Chat file for Card 3 | `/sessions/eager-youthful-albattani/mnt/SNGBOTME/../3_6_Nife.pi/TORQ-e/chat-card3.html` |
| Chat file for Card 1 | `/sessions/.../TORQ-e/chat-card1.html` |
| Chat file for Card 2 | `/sessions/.../TORQ-e/chat-card2.html` |
| Backend routes Card 3 | `/sessions/.../TORQ-e/card_3_uhwp/routes.py` |
| Main FastAPI app | `/sessions/.../TORQ-e/main.py` |
| Models/DB | `/sessions/.../TORQ-e/models.py` |

---

## KEY PATTERNS

### HTML Chat Files
- **Location:** Root level (`/TORQ-e/chat-card*.html`)
- **Structure:** 
  - JavaScript at bottom for API calls
  - `const API_BASE = '/api/cardX'`
  - `const BACKEND_URL = 'http://localhost:3000'` (or actual domain)
  - Mock fallback in try/catch blocks

### Backend Routes
- **Location:** `/card_X_yyy/routes.py`
- **Pattern:** FastAPI router with prefix `/api/cardX`
- **Schemas:** `/card_X_yyy/schemas.py`
- **Init:** `/card_X_yyy/__init__.py` exports router
- **Registration:** `main.py` imports and includes router

### Response Structure (Cards 1-3)
```python
{
  "clarity": "green|yellow|red",  # Traffic light
  "sources": [                    # Fixed citations
    {
      "name": "...",
      "url": "...",
      "timestamp": "ISO8601"
    }
  ],
  "timestamp": "ISO8601",
  # ... card-specific data
}
```

---

## COMMANDS I'LL USE (No more asking)

✅ **Find chat files:** `*.html` glob on `/TORQ-e/` root  
✅ **Find backend routes:** `/card_X_yyy/routes.py`  
✅ **Find schemas:** `/card_X_yyy/schemas.py`  
✅ **Register new routes:** Edit `main.py` import + include_router  
✅ **Backend request/response:** Card 4 is reference (chat-card4.html + routes.py)  

---

**File Scheme Complete. Moving to Card 3 Frontend → Card 1 → Card 2.**

