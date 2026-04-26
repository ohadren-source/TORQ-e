# CARD 4: THE LIGHTHOUSE OF ALEXANDRIA
## Design Reference - The Reference Architecture

**Status:** 🔒 LOCKED v1.0.0 | 2026-04-25  
**Quality:** COMPLETE | VALIDATED | PRODUCTION-READY  
**Role:** BEACON for all other card decisions  
**Classification:** Internal Reference Architecture

---

## THE PROPOSITION

**Statement:** Card 4 (USHI - Government Stakeholder Operations) is the only complete, fully validated system in TORQ-E. All other cards (1, 2, 3, 5) must follow its patterns, architecture, and quality standards.

**Corollary:** Card 4's implementation IS the definition of "done" for TORQ-E.

---

## WHAT MAKES CARD 4 THE LIGHTHOUSE

### ✅ Completeness

**Frontend (chat-card4.html):**
- ✅ Welcome message
- ✅ Intent routing (metrics, trends, quality, governance, help, default)
- ✅ Context-aware response handling
- ✅ Spectrum Analyzer visualization (all responses)
- ✅ Elaborate buttons (mandatory on every response)
- ✅ Session storage for source removal
- ✅ Immutable audit trail integration

**Backend (card_4_ushi/routes.py):**
- ✅ 5 core endpoints (metrics, fraud-signals, data-quality, governance-log, flag-issue)
- ✅ Health check endpoint
- ✅ HIPAA-compliant aggregate metrics
- ✅ Immutable audit logging
- ✅ Signal strength calculation across 6 dimensions

**Integration:**
- ✅ Railway deployment working
- ✅ API responding in production
- ✅ Real data flowing (test queries validated)

### ✅ Validation

**Test Coverage:**
- ✅ All 6 test queries passed
- ✅ Spectrum Analyzer rendering correctly
- ✅ Elaborate buttons functional
- ✅ Intent routing accurate
- ✅ Metrics aggregation working

**QA Status:**
- ✅ Ready for stakeholder testing (Carol, Selam, Bob)
- ✅ No known bugs or critical issues

### ✅ Documentation

**Architecture:**
- ✅ TORQ-E_Card4_Governance_Architecture_DR.md (complete, frozen)
- ✅ TORQ-E_Card4_Governance_Architecture_AN.md (complete, frozen)

**Release:**
- ✅ RELEASE_NOTES_v1.0.0.md (published)
- ✅ All 6 test queries documented
- ✅ Success criteria defined

### ✅ Architectural Decisions

**Pattern: Context-Driven Routing**
```
PRIMARY: Does user want to DO something? (explicit action)
  → Use specific handler

SECONDARY: Does user have conversation CONTEXT?
  → Use context handler

FALLBACK: No action, no context
  → Use generic help
```

**Pattern: Spectrum Analyzer (Universal Visualization)**
- Every response includes traffic lights
- Three-tier system (Coherence Level, Stability Strength, Combined View)
- Collapsed by default, expand on click
- Elaboration available on all responses

**Pattern: Session-Level Governance**
- Source removal with confirmation modal
- SessionStorage for ephemeral state
- No permanent deletion (director approval required for v1.1)

**Pattern: Immutable Audit Trail**
- Write-once append-only logging
- HIPAA 42 CFR Part 455 compliant
- Every action timestamped and attributed

---

## WHAT CARD 4 DEFINES AS "DONE"

### Code Quality Standards

**Frontend:**
- No hardcoded question types (context-driven instead)
- Every response has visual feedback (Spectrum Analyzer)
- Every response has explanation option (Elaborate)
- Session state respected and used
- Error handling with fallback data

**Backend:**
- All endpoints fully implemented
- Health check included
- Aggregate metrics (never expose PII)
- Audit trail immutable
- Signal strength calculated across multiple dimensions

### UX Standards

- **Consistency:** Same design language across all responses
- **Transparency:** Users always see system state (traffic lights)
- **Control:** Users can remove sources with confirmation
- **Clarity:** Elaborate explains every metric and decision
- **Accessibility:** All features keyboard-navigable

### Deployment Standards

- **Live on Railway:** Production infrastructure working
- **API responding:** Real calls → Real responses
- **Data flowing:** Metrics calculated in real-time
- **No fallbacks needed:** System works as designed

---

## CARD 4'S ARCHITECTURAL PRINCIPLES

### Principle 1: MISERICORDIA > QUALIA
Card 4 prioritizes compassion and clarity over technical cleverness.
- Spectrum Analyzer is simple traffic light, not complex heat map
- Elaborate explains in plain language, not jargon
- Users always understand system state

### Principle 2: IMPACT > INTENT
Card 4 measures success by actual governance outcomes, not by features built.
- 6 test queries validate real use cases
- Metrics are actionable (not just data)
- Governance decisions can actually be made from Card 4

### Principle 3: WE > I
Card 4 serves multiple stakeholders with different needs from same data:
- Bob (Governance): Sees compliance status
- OMIG Investigator: Sees fraud signals
- User 3 (Operations): Sees claims processing health
- One system, three voices

---

## WHAT ALL OTHER CARDS MUST REPLICATE

### From Card 4's Frontend

```javascript
// Pattern 1: Context-driven routing (not question-type hardcoding)
if (explicit_user_action) {
  return handle_specific_action();
} else if (conversation_context) {
  return handle_contextual_question();
} else {
  return generic_help();
}

// Pattern 2: Spectrum Analyzer on every response
html += generateSpectrumAnalyzer(metrics);

// Pattern 3: Elaborate button on every response
html += `<button onclick="elaborateMetrics('type')">📖 Elaborate</button>`;

// Pattern 4: Session state awareness
const removedSources = JSON.parse(sessionStorage.getItem('removedSources') || '[]');
```

### From Card 4's Backend

```python
# Pattern 1: Immutable audit trail
audit_trail = {
    "calculated_by": "system_component",
    "calculation_method": "statistical",
    "timestamp": datetime.utcnow(),  # Write-once
    "verified_by": "human_if_needed"
}

# Pattern 2: Signal strength across dimensions
signal = SystemSignal(
    dimension="ENROLLMENT_RATE",  # enum
    value=87.3,  # 0-100
    confidence_score=95,  # How sure are we?
    color="green"  # Traffic light
)

# Pattern 3: Aggregate metrics (never expose PII)
metrics = {
    "enrollment_rate": 87.3,  # Aggregate
    "active_members": 1_250_000,  # Aggregate
    "confidence_score": 95
    # Never: individual member IDs, claim details, etc.
}

# Pattern 4: Health check
@router.get("/health")
async def health_check():
    return HealthCheckResponse(
        status="healthy",
        database="healthy",
        timestamp=datetime.utcnow()
    )
```

---

## THE LIGHTHOUSE EFFECT

Card 4's existence means:

**For Card 1 (UMID):**
- Should include Spectrum Analyzer (system health)
- Should use context-driven routing
- Should have Elaborate buttons
- Should respect session authentication

**For Card 2 (UPID):**
- Should include Spectrum Analyzer (claims processing health)
- Should use context-driven routing  
- Should have Elaborate buttons
- Should respect session provider authentication

**For Card 3 (WHUP):**
- Should include Spectrum Analyzer (plan network health)
- Should use context-driven routing ✓ (just fixed)
- Should have Elaborate buttons
- Should have backend that matches frontend

**For Card 5 (UBADA):**
- Should include Spectrum Analyzer (fraud risk)
- Should use context-driven routing
- Should have Elaborate buttons
- Should have immutable investigation trail

---

## THE COVENANT

All other cards in TORQ-E pledge to:

1. **Match Card 4's quality** - No less complete, no less validated
2. **Follow Card 4's patterns** - Same routing, same visualization, same clarity
3. **Respect Card 4's principles** - MISERICORDIA, IMPACT, WE
4. **Achieve Card 4's state** - LOCKED, TESTED, PRODUCTION-READY

Until they do, they are incomplete.

---

## CURRENT STATE vs. LIGHTHOUSE STATE

| Aspect | Card 4 | Card 1 | Card 2 | Card 3 | Card 5 |
|--------|--------|--------|--------|--------|--------|
| Frontend | ✅ | ✅ | ✅ | ✅ | ✅ |
| Backend | ✅ | ✅ | ✅ | ❌ | ❌ |
| Spectrum Analyzer | ✅ | ❌ | ❌ | ✅ | ❌ |
| Context Routing | ✅ | ❌ | ❌ | ✅ | ❌ |
| Elaborate Buttons | ✅ | ❌ | ❌ | ✅ | ❌ |
| Session Awareness | ✅ | ❌ | ❌ | N/A | N/A |
| Immutable Trail | ✅ | ❓ | ❓ | N/A | 🔜 |
| Test Coverage | ✅ | ❌ | ❌ | 🔜 | 🔜 |
| Locked/Frozen | 🔒 | ❌ | ❌ | ❌ | ❌ |

---

## DECLARATION

**Card 4 stands complete and validated.**

It is the **Lighthouse of Alexandria** — a singular beacon of architectural coherence in the TORQ-E harbor. 

All other cards must navigate toward its light.

Until they do, they remain incomplete.

This is not ambition. This is standard.

---

**Status:** 🔒 CARD 4 IS THE REFERENCE  
**Awaiting:** Chef's guidance on which card to illuminate next

