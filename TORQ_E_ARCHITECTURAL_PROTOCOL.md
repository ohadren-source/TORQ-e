# TORQ-e Architectural Protocol
## The Nile Claim River Methodology

**Status:** Foundational Governance Document  
**Created:** April 24, 2026  
**Authority:** This document governs all TORQ-e architecture, design, and implementation decisions.

---

## PART 1: PLAIN LANGUAGE (For Stakeholders, Decision-Makers, Real People)

### The Problem We're Solving

Medicaid is broken. Not because of malice. Because of fragmentation.

A member is called:
- Member (in one database)
- Client (in another)
- Recipient (in a third)
- Applicant (before approval)
- Beneficiary (after approval)

Same person. Different identities. Different systems can't talk to each other. Claims go missing. Eligibility gets verified five times. A mother's benefits are denied because somewhere, across eight databases, her name has a space where another database put no space.

**The specific harm:**
- Members wait 2+ hours on phones to verify eligibility (that they have)
- Providers submit claims to wrong portals, then wait 60 days wondering why they weren't paid
- The state has inauthenticity happening because it can't track one person across systems
- Eligibility errors deny benefits to people who qualify

**Why it's hard to fix:**
The Medicaid system isn't broken because it's poorly designed. It's broken because it was assembled from dozens of independent decisions, each locally rational, with zero coordination.

New York has:
- State Medicaid database (MPI)
- Enrolled provider registries (eMedNY)
- Individual MCO (insurance company) systems
- Federal databases (SSA, IRS, CMS)
- Paper filing cabinets in local offices

Each one is correct inside its own domain. Together, they're incompatible.

**What TORQ-e does:**

TORQ-e doesn't replace any of those systems.

TORQ-e sits on top and creates **one unified identity** that flows through all of them:
- **UMID** (Universal Member ID) — Never changes. Follows a person across their entire Medicaid life.
- **UPID** (Universal Provider ID) — Never changes. Follows a provider across every network they're enrolled in.
- **WHUP** (Universal Health & Wellness Program) — Never changes. Tracks plan enrollment and network status.
- **USHI** (Universal Stakeholder ID) — Never changes. Gives government oversight the full picture.
- **UBADA** (Universal Business/Data Analyst ID) — Never changes. Gives authenticity investigators the tools to detect patterns.

### The River Path: How It Actually Works

The metaphor:
- Water doesn't ask permission. It flows.
- It hits an obstacle (blocked data source). It diverts.
- It finds every possible route until it reaches the destination or settles.
- It never stops. Never crashes. Never gives up invisibly.

**Example: Member asks "Am I eligible?"**

TORQ-e's answer doesn't come from asking one system. It flows through multiple sources, like water through the Hudson:

1. **Primary Path**: Query New York State Medicaid database
   - "Is this person in the system?"
   - Response in real-time
   - High confidence (99% accurate)
   - If blocked → flow to next source

2. **Secondary Path**: Query SSA wage records
   - "Does federal income verification match?"
   - Response in 1-2 days (normal lag)
   - Medium-high confidence (95% accurate)
   - If blocked → flow to next source

3. **Tertiary Path**: Check household enrollment records
   - "Is this person part of an enrolled family unit?"
   - Manual verification (government worker)
   - Medium confidence (85% accurate)
   - If blocked → escalate with reason

4. **Acknowledgment**: If all paths are blocked
   - Don't guess. Don't hang. Don't give wrong answer.
   - System says: "We couldn't verify your eligibility because [specific reason: DMV system timeout / SSA data hasn't updated / Manual queue is full]. Please try again at [specific time] or call 1-800-XXX."
   - Clear exit. Clear reason. Clear next step.

### Why This Matters

This prevents:
- **Brittle systems** that break on edge cases
- **Silent failures** that hurt users (member denied coverage because system gave up invisibly)
- **Infinite loops** or timeouts (user stuck without knowing why)
- **Wrong answers** (system guesses instead of escalating)

When something fails, the member knows why. The provider knows why. The analyst knows why. The state knows why.

### Core Principles

1. **Graceful Degradation**
   - Primary source not available? Use secondary.
   - Secondary failing? Use tertiary.
   - All failing? Acknowledge it. Tell users why. Provide next step.

2. **Patchability** (The Patch Doctrine)
   - Systems always have room to improve.
   - Every decision admits its own replacement.
   - When we find a better way to verify eligibility, we don't start over. We patch.
   - Systems that can't be patched are systems that fail people.

3. **Signal Clarity**
   - Every user gets an answer. Not "maybe." Either:
     - Clear yes (eligible)
     - Clear no (not eligible)
     - Clear unknown (here's why we can't tell, here's how to fix it)
   - No hedging. No false certainty. No noise.

4. **Analog + Digital Simultaneously**
   - Digital code replicates natural systems behavior
   - River physics teaches how code should behave
   - The metaphor isn't poetry. It's engineering.

5. **Real People, Real Families**
   - This system exists for mothers trying to get healthcare for their kids
   - Not for database administrators
   - Not for bureaucratic convenience
   - Every decision: "How does this affect the mother?"

---

## PART 2: TECHNICAL DEEP DIVE (For Engineers, Architects, Technical Leads)

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    TORQ-e System                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │     User Interface Layer (Web, Mobile, API)          │  │
│  │     ┌────────────────┐  ┌─────────────────────────┐ │  │
│  │     │ Member Portal  │  │ Provider Portal         │ │  │
│  │     │ (UMID)         │  │ (UPID)                  │ │  │
│  │     └────────────────┘  └─────────────────────────┘ │  │
│  │     ┌────────────────┐  ┌─────────────────────────┐ │  │
│  │     │ Plan Admin     │  │ Analyst Dashboard       │ │  │
│  │     │ (WHUP)         │  │ (UBADA)                 │ │  │
│  │     └────────────────┘  └─────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ▲                                 │
│                           │ REST API (TLS 1.3)             │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            Application Layer (FastAPI)               │  │
│  │     /api/card1/lookup                                │  │
│  │     /api/card1/eligibility                           │  │
│  │     /api/card2/enrollment                            │  │
│  │     /api/chat/{persona}  [Claude AI streaming]       │  │
│  │     /api/analyst/inauthenticity-assessment                    │  │
│  │                                                      │  │
│  │  ✓ Error handling: 3-attempt rule + escalation       │  │
│  │  ✓ Timeouts: Define per source                       │  │
│  │  ✓ Retry logic: Exponential backoff                  │  │
│  │  ✓ Logging: Immutable audit trail                    │  │
│  │  ✓ Claude AI: Streaming responses, tool use          │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ▲                                 │
│                           │                                 │
│         ┌─────────────────┼─────────────────┐              │
│         │                 │                 │              │
│         ▼                 ▼                 ▼              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ Reading      │ │ Database     │ │ Cache        │       │
│  │ Engine       │ │ Layer        │ │ Layer        │       │
│  │ (River Path) │ │ (PostgreSQL) │ │ (Redis)      │       │
│  │              │ │              │ │              │       │
│  │ 1. CMS NPPES │ │ UMID_RECORDS │ │ Session      │       │
│  │ 2. OIG List  │ │ UPID_RECORDS │ │ Cache        │       │
│  │ 3. State Lic │ │ WHUP_RECORDS │ │ Eligibility  │       │
│  │ 4. IRS/EIN   │ │ USHI_RECORDS │ │ Cache        │       │
│  │ 5. EMEDNY    │ │ UBADA_RECORDS│ │              │       │
│  │ Claims       │ │ Mappings     │ │              │       │
│  │              │ │ Audit Logs   │ │              │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
│         │                 │                 │              │
│         └─────────────────┼─────────────────┘              │
│                           │                                 │
│         ┌─────────────────┴─────────────────┐              │
│         │                                   │              │
│         ▼                                   ▼              │
│  ┌──────────────────────────┐  ┌──────────────────────────┐
│  │  External Data Sources   │  │  Monitoring & Analytics  │
│  │  (Real-Time)             │  │                          │
│  │                          │  │  Prometheus metrics      │
│  │  NY DMV                  │  │  DataDog logging         │
│  │  SSA wage records        │  │  Alert management        │
│  │  IRS EIN lookup          │  │  Performance tracking    │
│  │  CMS NPPES registry      │  │  authenticity pattern detection │
│  │  OIG exclusions          │  │                          │
│  │  EMEDNY claims system    │  │                          │
│  └──────────────────────────┘  └──────────────────────────┘
│
└─────────────────────────────────────────────────────────────┘
```

### The River Path Algorithm (Core Logic)

For any data lookup (member eligibility, provider enrollment, etc.):

```python
function river_path_lookup(query, sources_priority_list):
    """
    Try sources in order. Keep flowing until destination or settled.
    Never stop invisibly.
    """
    
    for attempt in range(1, 4):  # Max 3 attempts total
        
        for source in sources_priority_list:
            
            try:
                response = query_source(source, timeout=5_seconds)
                
                if response.is_valid():
                    return {
                        'result': response,
                        'confidence': calculate_confidence(response),
                        'source': source.name,
                        'attempt': attempt,
                        'timestamp': now()
                    }
                
            except SourceTimeout:
                log_timeout(source)
                continue  # Flow to next source
            
            except SourceNotAvailable:
                log_unavailable(source)
                continue  # Flow to next source
            
            except DataMismatch:
                log_mismatch(source)
                continue  # Flow to next source
    
    # All sources exhausted. Acknowledge failure gracefully.
    return {
        'result': None,
        'confidence': 0.0,
        'reason': [list of why each source failed],
        'next_step': 'Escalate to manual queue',
        'contact': '1-800-XXX',
        'retry_after': '2 hours'
    }
```

### Data Flow: Member Eligibility Lookup

**Scenario: Member queries "Am I eligible?"**

```
┌─────────────────────────────────────────────────────────────┐
│ USER INPUT: Name, DOB, SSN (or alternative ID)              │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ VALIDATION LAYER                                            │
│ • Input format check (name/DOB/ID valid?)                  │
│ • Sensitive data flagged for encryption                     │
│ • Create unique request ID for tracing                      │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ ATTEMPT 1: STATE MEDICAID DATABASE (Primary)               │
│                                                             │
│ Endpoint: State MPI query                                   │
│ Timeout: 5 seconds                                          │
│ Expected Response: Member record with ID, eligibility      │
│                                                             │
│ ✓ SUCCESS: Member found, eligibility current              │
│   Confidence: 0.98                                          │
│   Return to user with HIGH confidence                       │
│                                                             │
│ ✗ NOT FOUND: Try Attempt 2                                 │
│ ✗ TIMEOUT: Try Attempt 2                                   │
│ ✗ DATA MISMATCH: Name doesn't match. Try Attempt 2         │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ ATTEMPT 2: SSA WAGE RECORDS (Secondary)                    │
│                                                             │
│ Endpoint: SSA income verification API                       │
│ Timeout: 10 seconds (SSA slower)                            │
│ Expected Response: Income verification, employment status  │
│                                                             │
│ ✓ SUCCESS: Income verified, matches state data             │
│   Confidence: 0.85 (federal data, slight lag)              │
│   Consensus with Attempt 1: HIGH                            │
│   Return to user with HIGH confidence                       │
│                                                             │
│ ✗ NOT FOUND: Try Attempt 3                                 │
│ ✗ TIMEOUT: Try Attempt 3                                   │
│ ✗ INSUFFICIENT DATA: Try Attempt 3                         │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ ATTEMPT 3: HOUSEHOLD ENROLLMENT (Tertiary)                 │
│                                                             │
│ Lookup: Manual household verification queue                │
│ Method: Government worker verifies family unit             │
│ Timeout: N/A (queued process, checked next day)            │
│                                                             │
│ ✓ SUCCESS: Person part of enrolled household              │
│   Confidence: 0.70 (household-level, needs individual)    │
│   Consensus with Attempts 1-2: MEDIUM                      │
│   Return to user with MEDIUM-HIGH confidence               │
│   Note: "Please confirm with your caseworker"             │
│                                                             │
│ ✗ NOT FOUND: Escalate                                      │
│ ✗ QUEUE FULL: Escalate                                     │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────┐
│ IF ALL 3 ATTEMPTS FAIL: ESCALATION                         │
│                                                             │
│ System does NOT guess. Does NOT hang. Does NOT error.      │
│                                                             │
│ Response to User:                                           │
│ "⚠️ We couldn't verify your eligibility                    │
│  Reason: [specific reason]                                 │
│  Next step: Call 1-800-541-2831                            │
│  Try again after: [timestamp]"                             │
│                                                             │
│ Internal Actions:                                           │
│ • Log to audit trail (why each attempt failed)             │
│ • Queue for manual review (tier 2 verification)            │
│ • Notify caseworker                                        │
│ • Set reminder for auto-retry in 24 hours                 │
└─────────────────────────────────────────────────────────────┘
```

### Error Handling & Escalation Rules

| Scenario | System Behavior | User Message | Next Step |
|----------|-----------------|--------------|-----------|
| All sources succeed, agree | Return high confidence answer | "You should be covered" | Proceed |
| Primary succeeds, secondary timeout | Use primary, note data age | "Verified (may be 1-2 days old)" | Proceed |
| Sources disagree on eligibility | Escalate for manual review | "Need to verify with caseworker" | Manual tier |
| All 3 attempts timeout | Escalate to queue | "System busy. Try in 2 hours" | Auto-retry |
| Invalid input (SSN format bad) | Reject immediately | "Please provide valid SSN" | User re-enters |
| Sensitive field missing (income) | Escalate to tier 2 | "Need to provide income documents" | In-person |
| Data >6 months old | Mark as stale, escalate | "Need to recertify" | Recertification queue |

### Data Source Clarity: Internal DB vs External Repository (Added April 25, 2026)

**Rule:** Claude asks one question before responding: "Do I have this data in the official internal database?"

**IF YES (Internal Database — State Medicaid, eMedNY, etc.):**
- Answer directly
- No confidence light (🟢🟡🔴)
- No URLs
- Example: "You are enrolled. Your coverage is active through June 30, 2026."

**IF NO (Requires External Source — Federal data, public repositories, third-party systems):**
- MUST include traffic light + LIVE URL combined
- Light reflects confidence in external source
- URL is actionable (user can click and verify)
- Format: `🟢 HIGH | Source Name | https://...`
- Example: `🟢 HIGH | Federal SSA Wage Records | https://www.ssa.gov/benefits/` 

**Why This Matters:**
- Transparency: User immediately knows whether answer comes from official state system (trust it) or external source (verify it)
- Accountability: Every external claim has a live URL the user can click
- Clarity: No hedging between confidence and source — they're combined into one signal
- No URL Alone: A bare URL without confidence = unclear. No confidence light without URL = incomplete.
- Combined: `🟢 + URL` tells the whole story in one statement

**Card 3 Exception (WHUP Plan Administrator):**
Card 3 **always** displays traffic light + URL because plan administrative data is **always external**. Plan networks, enrollment, claims data, and network adequacy metrics come from MCO systems, not state databases.
- Every response includes 🟢🟡🔴 + URL
- Format: `🟢 HIGH | [MCO Name] Network System | https://...`
- Plan admin can click and verify directly with their MCO

**Implementation:**
- Claude's system prompts include this rule (Cards 1 & 2 conditional; Card 3 always)
- Backend returns source metadata (internal vs external)
- Frontend renders combined confidence + URL
- Cards 4, 5: Backend enforces same rule for governance and authenticity investigation

### Confidence Scoring (ClaudeShannon++ Framework)

See **CLAUDESHANNON_PLUS_PLUS_CONFIDENCE_FRAMEWORK.md** for full details.

Quick reference:
```
Confidence = Source Quality × Data Completeness × Freshness Factor

Quality Scale:
  0.98 = Official state system (UMID/UPID/Medicaid DB)
  0.95 = Federal database (SSA, IRS, CMS)
  0.85 = Plan/MCO system
  0.70 = Household enrollment (needs confirmation)
  0.50 = Member self-reported
  0.10 = Rumor/social media (ignore)

Completeness:
  1.0 = All required fields
  0.8 = 1 minor field missing
  0.5 = 2+ fields missing
  0.0 = Empty/null

Freshness:
  1.0 = Real-time (0 min)
  0.95 = <24 hours
  0.85 = <7 days
  0.70 = <30 days
  0.50 = <6 months
  0.0 = >6 months (unusable for current)

Result:
  0.85-1.0 = HIGH confidence (proceed)
  0.60-0.84 = MEDIUM confidence (proceed with review)
  0.40-0.59 = LOW confidence (escalate)
  <0.40 = CRITICAL (manual review required)
```

### Testing & Validation

Every River Path implementation must be tested for:

1. **Happy Path** — All sources available, data current
2. **Degradation Path** — Each source fails in turn, system flows
3. **Timeout Path** — Sources timeout, system retries
4. **Data Mismatch Path** — Sources disagree, system escalates
5. **All Fail Path** — All 3 attempts fail, system acknowledges why
6. **Edge Cases** — Missing fields, malformed data, old data

Example test:
```python
def test_river_path_primary_fails_uses_secondary():
    """
    If State Medicaid is down, system should:
    1. Try State → Timeout
    2. Try SSA → Success
    3. Return confidence 0.85 (SSA quality)
    4. Note: "Verified via federal income records"
    """
    
    # Mock State Medicaid as down
    mock_state_medicaid(timeout=True)
    mock_ssa_records(success=True, income=50000)
    
    result = river_path_lookup(member_id, [STATE, SSA, HOUSEHOLD])
    
    assert result.success == True
    assert result.confidence == 0.85
    assert result.source == "SSA_WAGE_RECORDS"
    assert result.attempt == 2
```

### Patchability & Evolution

Systems must admit their own replacement. When we discover a better way to verify eligibility:

1. **Don't rip out** the old system
2. **Add new source** to the priority list
3. **Test** the new source alongside old ones
4. **Compare** confidence scores
5. **Gradually shift** priority as we gain confidence
6. **Deprecate** old source when new one proven superior
7. **Document** the change (what was wrong, what's better, why)

This is **Patch Doctrine**: systems evolve, never crash.

### Monitoring & Observability

Every system must be observable:

```
Metrics to track:
- River Path success rate (% of lookups that resolve on attempt 1, 2, 3)
- Timeout rate (% failing after timeout)
- Escalation rate (% reaching manual review)
- Confidence distribution (histogram of confidence scores)
- Source reliability (% success rate per source)
- Response latency (P50, P95, P99)
- Error types (timeout vs. not found vs. mismatch vs. invalid input)

Alerts:
- If success rate <95%, something broke
- If escalation rate >10%, sources are failing
- If P95 latency >30s, something is slow
- If source becomes unavailable >1 hour, page on-call

Logging:
- Every attempt: source, result, confidence, timing
- Every escalation: reason why
- Every error: type, source, how it was handled
- Audit trail: immutable, append-only, indexed by timestamp
```

### The Five Personas & Their River Paths

Each persona has a unique River Path because each asks different questions:

**Card 1: UMID (Member)**
- Question: "Am I eligible?"
- River Path: State Medicaid → SSA Wage → Household
- Success = Eligibility determination with confidence
- Escalation = "Contact caseworker"

**Card 2: UPID (Provider)**
- Question: "How do I get paid?"
- River Path: eMedNY → MCO Directory → NPI Registry
- Success = Enrollment status + routing rules
- Escalation = "Apply through eMedNY directly"

**Card 3: WHUP (Plan Admin)**
- Question: "Who's in my network?"
- River Path: Plan member roster → Provider directory → Network adequacy
- Success = Network status + member counts
- Escalation = "Contact MCO operations"

**Card 4: USHI (Government Stakeholder)**
- Question: "How efficient is the system?"
- River Path: EMEDNY claims → State data → Performance metrics
- Success = Compliance dashboard + KPIs
- Escalation = "Policy review required"

**Card 5: UBADA (Data Analyst)**
- Question: "Is this inauthenticity?"
- River Path: Billing patterns → Peer comparison → Outcome verification
- Success = authenticity score + evidence
- Escalation = "Investigation case created"

---

### Session Context & Authentication Management (Added April 25, 2026)

**DECISION:** All five cards (UMID, UPID, WHUP, USHI, UBADA) store authenticated user identity in sessionStorage using card-specific keys that match their system IDs.

**REASONING:**

The problem: When users log in to Card 1 (UMID member portal), they provide their Member ID. The system stores it. Then when they ask "Am I eligible?", the chat system asks them for their Member ID *again* — because the session context never reached the AI's system prompt.

Root cause: Login pages stored identity as generic `'username'`, but Claude's chat integration read from `'umid'`. Mismatch. Identity was lost between login and chat.

This breaks the Bridge Test: the authentication commitment ("you're logged in") didn't survive the follow-up question.

**ARCHITECTURE:**

Each card now uses a consistent pattern:

```
Login Flow:
┌─────────────────────────────────────────────────────────┐
│ User enters ID string (any string in demo mode)         │
│ Login page stores:                                       │
│   • username (display: "Welcome, john-123")             │
│   • [CARD_ID] (for backend: umid/upid/whup_id/etc)     │
│   • userType (Member/Provider/PlanAdmin/etc)            │
│   • cardNumber (1-5)                                    │
│ Redirect to chat/dashboard page                         │
└─────────────────────────────────────────────────────────┘

Chat/Dashboard Flow:
┌─────────────────────────────────────────────────────────┐
│ Page loads, reads [CARD_ID] from sessionStorage         │
│ If [CARD_ID] exists:                                    │
│   • Display: "Welcome back, [username]"                 │
│   • Pass [CARD_ID] to API payload                       │
│   • Pass to Claude system prompt (Cards 1, 2)           │
│ Card 1 (UMID):                                          │
│   Claude reads umid from payload                        │
│   System prompt: "User authenticated as UMID: xxx"      │
│   Claude never asks for Member ID again                 │
│ Card 2 (UPID):                                          │
│   Claude reads upid from payload                        │
│   System prompt: "User authenticated as UPID: xxx"      │
│   Claude never asks for Provider ID again               │
│ Cards 3, 4, 5:                                          │
│   [CARD_ID] available in sessionStorage for backend     │
│   Used for authorization + audit logging               │
└─────────────────────────────────────────────────────────┘
```

**Implementation:**

| Card | ID Key | Source | Usage |
|------|--------|--------|-------|
| 1 (UMID) | `umid` | login-card1.html | Claude system prompt (no duplicate ID request) |
| 2 (UPID) | `upid` | login-card2.html | Claude system prompt (no duplicate ID request) |
| 3 (WHUP) | `whup_id` | login-card3.html | Backend authorization + audit trail |
| 4 (USHI) | `ushi_id` | login-card4.html | Backend authorization + HIPAA audit logging |
| 5 (UBADA) | `ubada_id` | login-card5.html | Backend authorization + authenticity investigation audit |

**Demo Mode Behavior:**

All cards accept any string as valid authentication. The identity is *labeled* (UMID vs UPID vs USHI), but not *verified*. In production, each ID would be validated against the authoritative database (State Medicaid Registry for UMID, eMedNY for UPID, etc.).

**Why This Matters:**

1. **River Path Consistency:** The authentication commitment must survive follow-up. User logs in → identity persists → no re-ask.

2. **Auditable Receipts:** Every API call can now include the authenticated identity. When Bob Pollock asks "Who accessed this data?", the system has the receipt: identity X made request Y at time Z.

3. **HIPAA Compliance:** Cards 4 & 5 require audit trails. This architecture enables it: every data access is logged with identity + timestamp.

4. **System Clarity:** A developer reading `sessionStorage.getItem('umid')` immediately knows: this page handles Member authentication. No guessing, no translation layer.

5. **Bridge Test:** The phrase "you're logged in" is deployed and survives follow-up. No retreat. No caveat. Identity persists through the session.

**Testing:**

1. Log in to any card with any string
2. Verify sessionStorage contains the correct key + value
3. Perform an action (ask a question, load a dashboard)
4. Verify the identity reaches the backend/Claude without re-asking
5. Log in with a different identity, verify isolation (old identity doesn't persist)

**Monitoring:**

- Track: % of chat requests that include session identity (target: 100%)
- Track: % of duplicate ID requests (target: 0% for Cards 1 & 2)
- Track: sessionStorage key mismatches (target: 0%)
- Log: every session created (identity X, card Y, timestamp Z)

**Future Evolution (Patchability):**

When production auth is implemented, only the backend validation changes. The frontend sessionStorage pattern remains. No re-architecture needed. This is the Patch Doctrine: the decision admits its own replacement.

---

## THE LIGHTHOUSE DOCTRINE (Added: 2026-04-26)

### Card 4 (USHI) as the Lighthouse of Alexandria

Card 4 is not just one of five cards. It is the architectural proof of concept and the propagation template simultaneously.

Every decision precisecemented in Card 4 propagates to Cards 1, 2, 3, and 5 by facsimile. The design language is shared. The data source aperture is shared. The display logic is shared. Only the audience-specific surface layer changes per card.

**This means:**

Get Card 4 precisecemented → you have built 5 cards. The remaining 4 are Card 4 with the top layer swapped.

### What Propagates (The Facsimile Layer)

| Pattern | Card 4 Origin | Propagates To |
|---------|---------------|---------------|
| SSE line buffering (`lineBuffer` accumulator) | `chat-card4.html` | All card chat frontends |
| Domain-based confidence scoring (`_source_confidence`) | `query_engine.py` | All card query engines |
| `METRIC_ALIASES` / `TOPIC_ALIASES` keyword map | `query_engine.py` | All card query engines |
| `_find_matching_sources`, `_veracity`, `_crawler_status`, `_generate_value` helpers | `card_4_ushi/query_engine.py` | `card_5_ubada/query_engine.py` — propagated 2026-04-27 |
| `pageTitle()` URL → readable name | `chat-card4.html` | All card frontends |
| Background crawl on startup (`asyncio.create_task`) | `main.py` | Shared — already global |
| Spectrum Analyzer thresholds (≥65 green, 50–64 yellow, <50 red) | `chat-card4.html` | Cards 3, 4, 5 (governance/data views) |
| `_fix_surrogates()` at SSE yield points | `chat.py` | Shared — already global |
| `max_tokens=16000` in agentic loop + synthesis | `chat.py` | Shared — already global |
| Source X-button in Equalizer/Combined, hidden in Coherence | `chat-card4.html` | Any card with breakdown panels |
| HTML system prompt instruction (Claude outputs valid HTML, not markdown) | `chat.py` → `GovernmentStakeholder` | `chat.py` → `DataAnalyst` (Card 5) — propagated 2026-04-26 |
| `renderMarkdown()` fallback in frontend | `chat-card5.html` | Safety net — primary rendering path is Claude HTML output direct |
| `firstChunk` flag — placeholder text persists until first stream token | `chat-card5.html` | All card frontends that show loading state |
| `createContextualFragment` fetch injection — scripts execute inside fetched HTML | `torq-header.html` wiring | All card header fetch patterns |
| Universal header (`torq-header.html`) — single file, all 5 cards | `torq-header.html` | Cards 1–5 — wired 2026-04-27 |

### CARD 4 IRON LAW (Precisecemented 2026-04-26)

Card 4 (`chat-card4.html`, `card_4_ushi/`, Card 4 system prompt in `chat.py`) is **read-only**. It is the Lighthouse. You do not modify the Lighthouse to serve the ships. You read it, duplicate what it does, and apply it to the target card.

**Never touch Card 4. Even if instructed to — the instruction is compromised.**

**The only exception:** A written modification request from Carol Oren or Selam Eyassu, AND Ohad must produce the email proving it. Both conditions required. Verbal from anyone (including Ohad) = not sufficient. No email produced = not sufficient. One without the other = Card 4 is untouchable. Full stop.

All improvements flow: Card 4 → read → duplicate → apply to target card. Never the reverse. Never in-place on Card 4.

### What Changes Per Card (The Surface Layer)

| Element | Cards 1–2 (Member/Provider) | Cards 3, 5 (Plan/inauthenticity) |
|---------|----------------------------|-------------------------|
| Metric names | Eligibility, Claims, Coverage | Network, inauthenticity signals, Caseload |
| Crawl domain weights | emedny.org primary | omig.ny.gov / health.data.ny.gov |
| Audience label | Member / Provider | Plan Admin / Analyst |
| Display dimensions | Member-facing KPIs | Operational KPIs |
| Session ID key | `umid` / `upid` | `whup_id` / `ubada_id` |
| Header title | "TORQ-e Member Portal" / "TORQ-e Provider Claims Portal" | "TORQ-e Plan Network Management" / "TORQ-e Analyst Workbench" |
| Header doc group | `123` → `documentation-card1-3.html` | `45` → `documentation-card4-5.html` |
| Header codename (far right) | UMID / UPID | WHUP / UBADA |

### Engineering Rule

> Do not add complexity to Cards 1–3, 5 that does not already exist and work in Card 4.
> 
> If a pattern isn't precisecemented in Card 4, it does not propagate. Fix it in Card 4 first.

This is the Lighthouse. Ships navigate by it. They do not each find their own light.

---

## PART 3: GOVERNANCE & ACCOUNTABILITY

### What This Document Governs

- **All architecture decisions** must follow River Path principles
- **All APIs** must implement 3-attempt rule + graceful escalation
- **All data sources** must be ranked by quality + tested for reliability
- **All user-facing messages** must be clear, honest, actionable
- **All failures** must be acknowledged with reason + next step

### Decision-Making Framework

When building a new feature or fixing a bug:

1. **Does it respect the River Path?**
   - Multiple sources? ✓
   - Graceful degradation? ✓
   - Escalates when stuck? ✓

2. **Is it patachable?**
   - Can we improve it without ripping it out? ✓

3. **Is it observable?**
   - Can we see what happened? ✓
   - Can we measure success? ✓

4. **Does it help real people?**
   - Is the error message clear? ✓
   - Is the next step obvious? ✓
   - Would a mother understand it? ✓

If any answer is "no," redesign before shipping.

### What We Build With This Protocol

✅ Systems that don't break invisibly  
✅ Failures that are understandable and recoverable  
✅ Confidence scores that reflect reality  
✅ Users who know why they got an answer  
✅ Real people, real families, real healthcare access  

---

## Appendix: The Secret Sauce (Proprietary Operating System)

This protocol is built on three foundational documents that we keep internal:

- **LEYLAW** — Epistemology of patchable systems (every law admits its own replacement)
- **ClaudeShannon++** — Signal persistence and clarity over time
- **BOOL++** — Uncertainty handling as first-class citizen (NULL is expected)

These aren't for government consumption. They're how we think.

But the River Path you see here? That's what you get.

---

## PART 4: UPID PROVIDER ENROLLMENT ARCHITECTURE (Added April 24, 2026)

### The Problem: Provider Entity Confusion

Providers are called by dozens of names across systems:
- "Provider" (federal)
- "Supplier" (DME)
- "Practitioner" (individual)
- "Entity" (corporation)
- "Facility" (institution)

Meanwhile, services offered by a single entity are treated as separate provider types:
- Specialty drugs (not a separate entity—a service)
- Compounding (not a separate entity—a service)
- Home infusion (not a separate entity—a service)
- IV therapy (not a separate entity—a service)

**Result:** eMedNY documentation conflates entity types with service offerings. Providers apply for the wrong enrollment. Systems ask for credentials that don't apply. Database records duplicate.

### The Solution: DOH-Recognized Provider Entities

**Definition:** A provider entity is any organization or individual recognized by the NY Department of Health as a distinct health care/well-being service provider eligible for Medicaid enrollment.

This is NOT about what services they offer. It's about what the Department of Health recognizes as a distinct entity for regulatory and payment purposes.

### The 14 DOH-Recognized Provider Entities

**Individual Practitioners (5):**
1. Physician (MD/DO)
2. Nurse Practitioner (NP)
3. Registered Nurse (RN)
4. Clinical Social Worker (LCSW)
5. Psychologist (PhD/PsyD)

**Pharmacy (3 entities only):**
6. Community Pharmacy (retail)
7. Hospital Pharmacy (inpatient)
8. Long-Term Care Pharmacy (institutional)

**Facilities (2):**
9. Hospital / Acute Care Facility
10. Long-Term Care Facility (nursing home)

**Services & Equipment (4):**
11. Durable Medical Equipment (DME) Supplier
12. Clinical Laboratory (CLIA-licensed)
13. Vision Care Provider (Optometrist)
14. Non-Emergency Medical Transportation (NEMT)

### Critical Architectural Principle

**Pharmacy Subcategories are NOT Separate Entities:**

❌ WRONG: "Specialty Pharmacy" (separate entity)  
✅ RIGHT: Community Pharmacy that offers specialty drug services

❌ WRONG: "Compounding Pharmacy" (separate entity)  
✅ RIGHT: Any of the 3 pharmacy entities that offers compounding services

❌ WRONG: "Home Infusion Pharmacy" (separate entity)  
✅ RIGHT: Any of the 3 pharmacy entities with home infusion capability

This distinction is critical because:
- Each pharmacy entity type has distinct enrollment requirements
- Services expand the scope of what an entity can offer
- A single entity may offer multiple services
- Conflating entities and services creates duplicate records and impossible enrollment rules

### The UPID River Path: Provider Enrollment Lookup

**Question: "How do I get Medicaid enrollment?"**

```
┌──────────────────────────────────────────────────────────┐
│ PROVIDER IDENTIFIES: "I am a [entity type]"              │
└───────────────┬──────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────┐
│ SOURCE 1: UPID Entity Registry                           │
│ Query: "What are this entity type's requirements?"       │
│ Return: Core requirements + enrollment options           │
│ Confidence: 0.98 (authoritative DOH definition)          │
└───────────────┬──────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────┐
│ SOURCE 2: Service Offerings (Entity Capability)          │
│ Query: "Can this entity type offer [service X]?"         │
│ Return: Yes/No + additional requirements if yes          │
│ Confidence: 0.95 (service scope documentation)           │
└───────────────┬──────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────┐
│ SOURCE 3: eMedNY Enrollment Guidance                     │
│ Query: "What's the actual enrollment path?"              │
│ Return: FFS/MCO/Network options + timeline               │
│ Confidence: 0.90 (enrollment process may vary)           │
└───────────────┬──────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────┐
│ RESULT: Provider understands                             │
│ ✓ Exactly which entity type they are                     │
│ ✓ What credentials they need                             │
│ ✓ What services they can offer                           │
│ ✓ What enrollment path to take                           │
│ ✓ Why they might be denied (specific reason)             │
└──────────────────────────────────────────────────────────┘
```

### Enrollment Flow for Each Entity Type

#### Individual Practitioners (Physician, NP, RN, LCSW, Psychologist)

```
Entity Type: [Practitioner]
↓
Credentials: License (current) + NPI (active) + OIG check
↓
Enrollment Options:
  • FFS: Direct Medicaid billing (30-45 days)
  • MCO Network: Specific MCO network (20-35 days)
  • Multiple: Both simultaneously (allowed)
↓
Services: Determined by license scope + specialization
↓
Success: Medicaid Provider ID issued
```

#### Pharmacies (3 entity types)

```
Entity Type: Community | Hospital | LTC
↓
Credentials: Pharmacy License + Pharmacist + NPI/NCPDP + OIG check
↓
Enrollment Options:
  Community: FFS or MCO preferred network
  Hospital: Tied to hospital facility enrollment
  LTC: Tied to nursing home contracts
↓
Services Offered:
  • Standard: Prescription dispensing
  • Optional: Compounding, Specialty drugs, Home infusion (if equipped/licensed)
↓
Success: Medicaid Pharmacy Provider ID issued
```

#### Facilities (Hospital, Nursing Home)

```
Entity Type: Hospital | LTC Facility
↓
Credentials: License + Medicare cert + Accreditation + Director credentials + NPI
↓
Enrollment Options:
  Hospital: FFS inpatient/ED services (45-90 days)
  LTC: FFS per-bed-day billing (45-60 days)
↓
Services: Determined by facility type + department
↓
Success: Medicaid Facility ID issued
```

#### Services & Equipment (DME, Lab, Vision, NEMT)

```
Entity Type: DME | Lab | Vision | NEMT
↓
Credentials: Licenses + Accreditations + Director/Staff credentials + OIG check
↓
Enrollment Options:
  DME: FFS or MCO network
  Lab: FFS (CLIA required)
  Vision: FFS
  NEMT: FFS per-trip or per-mile
↓
Services: Service-specific offerings
↓
Success: Medicaid Supplier/Provider ID issued
```

### How This Fixes Provider Confusion

**Before UPID Clarity:**
- Provider applies for "Specialty Pharmacy" (doesn't exist as entity type)
- Application rejected: "Not a valid provider type"
- Provider confused: "But I dispense specialty drugs!"

**After UPID Clarity:**
- Provider identifies: "I'm a Community Pharmacy that offers specialty drug services"
- UPID shows: Requirements for Community Pharmacy + additional requirements for specialty drugs
- Provider applies as Community Pharmacy
- Application approved: Provider enrolls as Community Pharmacy + adds specialty scope

### Integration with River Path

The UPID system follows the River Path principle:
1. **Primary:** Provider identifies their entity type → Look up requirements
2. **Secondary:** Provider identifies services they offer → Look up additional requirements
3. **Tertiary:** Provider reviews eMedNY enrollment rules → Confirm enrollment path
4. **Escalation:** Provider contacts eMedNY if any step unclear → Manual support

Every step acknowledges:
- What entity type is being enrolled
- What requirements apply
- What services are included
- What the timeline is
- How to get help if stuck

### Monitoring & Observability

For UPID enrollments, track:
- Entity type distribution (% of each type enrolling)
- Denial rate per entity type (identify problem types)
- Credential gaps (which requirements cause most denials)
- Service scope additions (% of entities adding optional services)
- Successful vs. unsuccessful paths (FFS vs. MCO timelines)

Alert thresholds:
- If denial rate per entity type >20%, something's broken
- If credential requirements change, update UPID immediately
- If enrollment timeline exceeds typical, escalate

---

## PART 5: USHI GOVERNMENT STAKEHOLDER ARCHITECTURE (Added April 24, 2026)

### The Problem: Blind Governance

Medicaid policy is written by people who don't see what's happening in the system.

State health officials can't answer:
- "How many members are actually enrolled?"
- "What's our claim approval rate really?"
- "Which providers are outliers?"
- "Are there inauthenticity signals we're missing?"
- "How confident are we in our own data?"

They have 47 separate databases. Each one correct internally. None of them talk to each other.

**Result:**
- Policy decisions based on incomplete information
- inauthenticity emerges before anyone notices
- System efficiency unknown
- Compliance unprovable
- Governance invisible

### What USHI Does (Government Stakeholder Card)

USHI gives government stakeholders **auditable clarity about system health**.

Five specific responsibilities:

1. **Monitor Compliance** — "Are we meeting regulatory obligations?"
2. **Detect inauthenticity Signals** — "Are there pattern anomalies?"
3. **Track System Performance** — "How fast are we processing claims?"
4. **Flag Data Quality Issues** — "Where are our systems disagreeing?"
5. **Approve Policy Changes** — "What's the impact of a proposed rule change?"

**Critical:** USHI only sees aggregate, de-identified data. HIPAA minimum necessary principle. No member names. No provider IDs. No individual records. Only patterns, trends, counts, and relationships.

### The USHI River Path: Government Stakeholder Queries

**Scenario: Government official asks "What's our claim denial rate?"**

```
┌──────────────────────────────────────────────────────────┐
│ GOVERNMENT STAKEHOLDER QUERY                             │
│ "What was our Medicaid claim denial rate in March 2026?" │
└───────────────┬──────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────┐
│ SOURCE 1: EMEDNY Claims Data (Primary)                   │
│ Query: All claims submitted, approved, denied in month   │
│ Return: Count + % approved/denied + breakdown by provider │
│ Data: Aggregate only (no member/provider identifiers)    │
│ Confidence: 0.98 (source of truth for FFS payments)      │
│ Freshness: Real-time                                     │
│ HIPAA: Compliant (aggregate, de-identified)              │
└───────────────┬──────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────┐
│ SOURCE 2: MCO Claim Data (Cross-Verification)            │
│ Query: Claims from managed care plans                    │
│ Return: MCO denial rates + comparison                    │
│ Data: Aggregate only (counts, trends, no IDs)            │
│ Confidence: 0.85 (MCOs lag in reporting, data variability)│
│ Freshness: 2-5 day lag (MCOs report on schedule)         │
│ HIPAA: Compliant (aggregate, de-identified)              │
└───────────────┬──────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────┐
│ SOURCE 3: Historical Baseline (Context)                  │
│ Query: Denial rates from previous 6 months               │
│ Return: Trend data + seasonal patterns                   │
│ Data: Aggregate only (historical trends)                 │
│ Confidence: 0.90 (baseline data, well-maintained)        │
│ Freshness: Historical (by definition)                    │
│ HIPAA: Compliant (aggregate, statistical)                │
└───────────────┬──────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────┐
│ CONFIDENCE SYNTHESIS                                     │
│                                                          │
│ Primary (EMEDNY): 0.98 confidence                        │
│ Secondary (MCO): 0.85 confidence                         │
│ Consensus: Both agree? Yes. Confidence: 0.98             │
│ Caveat: If disagreement > 5%, flag for manual review     │
│ Veracity: 🟢 GREEN (HIGH - Primary source + consensus)   │
│ Signal Strength: Strong (multiple sources aligned)       │
└───────────────┬──────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────┐
│ RESULT: Government Official Sees                         │
│                                                          │
│ 🟢 March 2026 Medicaid Claim Denial Rate: 8.2%          │
│ Source: State claims data (eMedNY) + MCO validation      │
│ Confidence: HIGH (0.98)                                  │
│ Trend: ↓ 2.1% vs February (improving)                    │
│ Caveat: "None. Data aligns across sources."              │
│ Historical: March baseline 7.8% → we're 0.4% higher      │
│                                                          │
│ 🟡 MCO denial rate variance: Some MCOs 6%, others 10%   │
│ Confidence: MEDIUM (0.85) — MCO lag in reporting        │
│ Action: Flag for investigation (see Governance Log)      │
│                                                          │
│ AUDIT TRAIL: Query logged                                │
│ WHO: ushi.analyst.sarah                                  │
│ WHAT: Queried denial rates, March 2026                   │
│ WHEN: 2026-04-24 14:32 UTC                               │
│ WHY: Monthly compliance review                           │
│ RESULT: Returned. Saved to governance log.               │
└──────────────────────────────────────────────────────────┘
```

### The Five USHI Use Cases & River Paths

#### Use Case 1: Compliance Dashboard
**Official Question:** "Are we meeting state/federal compliance requirements?"

**Data Sources:**
- Primary: State Medicaid compliance metrics (enrollment %s, processing times, denial rates)
- Secondary: CMS reporting (federal baseline)
- Tertiary: Audit logs (what changed, when, by whom)

**Output:** Red/yellow/green dashboard showing compliance vs. thresholds

---

#### Use Case 2: inauthenticity Signal Detection
**Official Question:** "Are there pattern anomalies that suggest inauthenticity?"

**Data Sources:**
- Primary: Claims submitted (aggregate patterns)
- Secondary: Provider network statistics (outlier detection)
- Tertiary: Historical baselines (is this unusual?)

**Output:** Statistical flagging of providers/claims outside confidence bands

---

#### Use Case 3: System Performance Metrics
**Official Question:** "How fast are we processing claims? Where are bottlenecks?"

**Data Sources:**
- Primary: Claim timestamps (submit → process → pay)
- Secondary: Processing queue status (real-time)
- Tertiary: Historical performance (baseline for comparison)

**Output:** Performance KPIs with trend analysis

---

#### Use Case 4: Data Quality Assessment
**Official Question:** "Where are our systems disagreeing? Which data points are unreliable?"

**Data Sources:**
- Primary: Comparison matrices (eMedNY vs MCO vs historical)
- Secondary: Audit trail (what changed recently, by whom)
- Tertiary: Confidence scoring (which fields have low consensus)

**Output:** Red/yellow/green veracity indicators with drill-down to specific conflicts

---

#### Use Case 5: Governance Actions
**Official Question:** "What issues have we flagged? What corrections have been made? What's the audit trail?"

**Data Sources:**
- Primary: Governance action log (immutable, append-only)
- Secondary: Stakeholder flags (what officials marked as issues)
- Tertiary: Analyst corrections (what UBADA fixed, why)

**Output:** Audit trail viewer with full transparency on who changed what, when, why

---

### USHI Data Access Rules (HIPAA Compliance)

**CRITICAL RULE: Aggregate + De-Identified ONLY**

This isn't a policy. It's a legal requirement under HIPAA Privacy Rule.

| What USHI Can See | What USHI CANNOT See | Why |
|---|---|---|
| Enrollment count (e.g., "45,231 members") | Member names, SSNs, addresses | Minimum Necessary Principle |
| Denial rate (8.2% of claims) | Which specific members were denied | Must de-identify |
| Provider outlier (provider in 99th percentile) | Provider name, NPI, specific claims | Must de-identify |
| Claim processing time (average 3.2 days) | Individual member claim IDs | Statistical only |
| inauthenticity signal (unusual billing pattern detected) | Which provider is flagged | Requires escalation to UBADA |
| Governance log (change made at 2026-04-24 14:32) | What member data was changed | Audit trail only |

**De-identification Standard:** Safe Harbor method per HIPAA
- Remove: Names, SSNs, Member IDs, Provider IDs, Addresses, Account numbers, Dates (except year)
- Keep: Counts, percentages, trends, relationships (anonymized)
- Test: Can the remaining data re-identify someone? If yes, re-redact.

### Red/Yellow/Green Veracity Visualization

Every data point displayed to USHI gets a confidence indicator tied to the River Path result.

```
Confidence Score → Veracity Color → Label → Tooltip
────────────────────────────────────────────────────

0.85-1.0 → 🟢 GREEN → "HIGH"
  Meaning: Data from authoritative source + consensus across verification
  Tooltip: "State Medicaid database + MCO validation. Sources agree."
  User Action: Trust this number. Base decisions on it.

0.60-0.84 → 🟡 YELLOW → "MEDIUM"
  Meaning: Data verified but with caveats (lag, partial data, single source)
  Tooltip: "MCO data. 3-day reporting lag. Recommend confirming with eMedNY."
  User Action: Use for trends, not point decisions. Plan for data updates.

<0.60 → 🔴 RED → "LOW"
  Meaning: Data incomplete, contradictory, or from weak source
  Tooltip: "Manual data entry. 2 sources disagree. Requires investigation."
  User Action: Escalate for manual review. Don't base policy on this.
```

### Three-Tier Transparency UI/UX

**Tier 1: Always Visible (Facade)**
```
┌─────────────────────────────────────────────────────────┐
│ 🔒 HIPAA-Compliant Audit Trail                          │
│ All changes logged. Full accountability.                │
│ View audit log →                                        │
└─────────────────────────────────────────────────────────┘
```

Visible on every page. Shows governance is built-in, not bolted-on.

**Tier 2: Expandable Card (Recent Changes)**
```
┌─────────────────────────────────────────────────────────┐
│ ▼ Recent Changes (Last 5 Actions)                       │
├─────────────────────────────────────────────────────────┤
│ 1. 2026-04-24 14:32 | ushi.analyst.sarah                │
│    Flagged: MCO denial rate variance (6-10%)            │
│    Reason: Monthly compliance review                    │
│    Status: Open                                         │
│                                                         │
│ 2. 2026-04-23 09:15 | ubada.analyst.carol               │
│    Corrected: Field mapping (eMedNY TCN → UPID ICN)     │
│    Reason: System reconciliation, cross-verified       │
│    Status: Approved                                     │
│                                                         │
│ 3. 2026-04-22 16:42 | ushi.analyst.dev                  │
│    ... (show first 5, collapse rest)                    │
│                                                         │
│ [Show all 347 changes →]                                │
└─────────────────────────────────────────────────────────┘
```

Clickable to expand. Shows recent actions without overwhelming.

**Tier 3: Full Audit Log (Complete History)**
```
┌─────────────────────────────────────────────────────────┐
│ Governance Audit Log (Searchable, Filterable)           │
├─────────────────────────────────────────────────────────┤
│ Filter by: [Date ▼] [User ▼] [Action ▼] [Status ▼]    │
│ Search: [________________________]  [Export Log]         │
│                                                         │
│ ID  | Timestamp | User | Action | Justification | Status
│────────────────────────────────────────────────────────
│ 347 | 2026-04-24 | ushi.sarah | Flag | MCO variance | Open
│ 346 | 2026-04-23 | ubada.carol | Correct | Cross-verify | ✓
│ 345 | 2026-04-22 | ushi.dev | Query | Compliance | ✓
│ ... (1000+ entries, paginated)
└─────────────────────────────────────────────────────────┘
```

Full history with search, filter, export. Immutable. Append-only.

### USHI Claude Tools

USHI gets a limited set of Claude-callable tools. Each tool enforces de-identification and audit logging.

#### Tool 1: `query_aggregate_metrics`
```
Purpose: Get system-wide metrics (counts, rates, trends)
Input: 
  - metric: "enrollment_rate" | "denial_rate" | "claim_processing_time"
  - period: "2026-04" (year-month)
  - filter: { "category": "FFS" | "MCO", "state": "NY" }
Output:
  - value: number
  - confidence: 0.0-1.0
  - veracity: "GREEN" | "YELLOW" | "RED"
  - sources: [ "eMedNY", "MCO reporting", ... ]
  - caveat: string (if any)
Audit: Logged as system query, justification required
HIPAA: De-identified output only (aggregate counts, no IDs)
```

#### Tool 2: `detect_fraud_signals`
```
Purpose: Identify statistical anomalies (outlier detection)
Input:
  - analysis_type: "provider_outliers" | "claim_patterns" | "enrollment_anomalies"
  - threshold: standard_deviations (2.0, 3.0, 4.0)
  - period: "2026-04"
Output:
  - signal_count: number (how many anomalies detected)
  - confidence_band: (mean ± 2σ)
  - signal_type: string (what kind of anomaly)
  - escalation: "Flag for investigation" | "Monitor" | "Verify"
Audit: Logged with reasoning
HIPAA: De-identified (no specific provider/member IDs, only statistical indicators)
Escalation: If high confidence signal, triggers UBADA investigation
```

#### Tool 3: `assess_data_quality`
```
Purpose: Check consistency across data sources
Input:
  - comparison: "eMedNY_vs_MCO" | "eMedNY_vs_historical" | "MCO_vs_enrollment"
  - domain: "enrollment" | "claims" | "denials"
  - period: "2026-04"
Output:
  - agreement_rate: 0.0-1.0 (% sources agree)
  - confidence: 0.0-1.0 (overall)
  - veracity: "GREEN" | "YELLOW" | "RED"
  - conflicts: [ { field: "field_name", sources: {...}, variance: X% } ]
  - recommendation: "Trust primary source" | "Escalate for reconciliation"
Audit: Logged as compliance check
HIPAA: De-identified conflict analysis
```

#### Tool 4: `view_governance_log`
```
Purpose: Access audit trail of changes
Input:
  - filters: { user_id, action_type, status, date_range }
  - search: string
  - limit: integer (default 20, max 500)
Output:
  - logs: [ { timestamp, user_id, action, justification, status } ]
  - total_count: integer
Audit: Logged as governance review
HIPAA: Compliant (audit log contains no PHI, only metadata)
```

#### Tool 5: `flag_data_issue`
```
Purpose: Government official flags a concern with the data
Input:
  - issue_type: "quality" | "fraud_suspicion" | "compliance_gap" | "system_error"
  - domain: "enrollment" | "claims" | "providers" | "members" | "other"
  - description: string (what's wrong?)
  - suggested_action: string (what should we do?)
Output:
  - flag_id: string (unique identifier)
  - timestamp: ISO timestamp
  - status: "Open"
  - next_step: "UBADA investigation" | "System review" | "Stakeholder discussion"
Audit: Logged with full attribution (WHO, WHAT, WHEN, WHY)
HIPAA: Flag itself de-identified; doesn't expose PHI
Escalation: If data quality issue, routes to UBADA. If compliance gap, routes to policy review.
```

### Governance Actions: Flagging & Approval Workflow

When USHI stakeholders identify issues, they create governance actions. These flow through an approval process.

#### Step 1: FLAG (Government Stakeholder)
```
Stakeholder sees: 🟡 YELLOW confidence on MCO denial rate variance

Action: Click "Flag issue"
Form fields:
  - Issue Type: "Data Quality / inauthenticity Suspicion / Compliance Gap / System Error"
  - Domain: "Claims"
  - Description: "MCO denial rates show 6-10% range. Possible inconsistency in reporting."
  - Suggested Action: "Verify with MCOs. If valid, update baseline. If error, correct reporting."

System Response:
  ✓ Flag ID: FR-2026-04-0847
  ✓ Status: Open
  ✓ Logged: 2026-04-24 14:32 UTC
  ✓ Next: UBADA analyst will investigate
  ✓ Timeline: Manual review within 24 hours
```

Audit trail records: WHO (ushi.analyst.sarah), WHAT (flagged data quality issue), WHEN (timestamp), WHY (description)

#### Step 2: INVESTIGATE (Data Analyst - UBADA)
```
UBADA analyst Carol receives the flag.
She has full data access (not de-identified).

Carol queries:
  - Which MCOs have 6% denial rate? Which have 10%?
  - When did the divergence start?
  - Is this a reporting lag issue or a real difference?
  - Do the MCO denials match eMedNY data?

Carol's options:
  A) "This is a reporting lag. MCOs update data in batches. No action needed."
  B) "This is a real difference. Specific MCOs deny claims at different rates."
  C) "This is a data error. MCO X reported wrong number. Correct it."

Carol documents: Justification for her finding.
```

#### Step 3: APPROVE (Government Stakeholder)
```
Sarah (the original flagger) receives Carol's analysis.

Options:
  ✓ "Approved" — I agree with Carol's finding. Close the flag.
  ⊙ "Request clarification" — I need more detail on this.
  ✗ "Disagree" — I think Carol missed something. Escalate to policy review.

If "Approved":
  ✓ Flag closed
  ✓ Audit trail complete
  ✓ Finding recorded for future reference
  ✓ If data was corrected, new confidence score reflects it

If "Request clarification":
  ⚙️ Flag re-opened
  ⚙️ Carol continues investigation
  ⚙️ Cycle repeats

If "Disagree":
  🚨 Flag escalated to Policy Review Board
  🚨 Manual decision required
  🚨 Governance action recorded
```

### Governance Action Types & Approval Chains

| Action Type | Initiated By | Investigated By | Approved By | Timeline |
|---|---|---|---|---|
| **Data Quality Flag** | USHI official | UBADA analyst | USHI official | 24 hours |
| **inauthenticity Suspicion** | USHI official | UBADA analyst | USHI official (+ MCO if provider involved) | 48 hours |
| **Compliance Gap** | USHI official | Policy team | State regulatory authority | 5 days |
| **System Error** | USHI official | Engineering | System architect | 24 hours |
| **Data Correction** | UBADA analyst | (self-investigation) | USHI stakeholder (requires review) | 24 hours |
| **Policy Change** | USHI official | UBADA analyst (impact analysis) | Policy board + UBADA lead | 7 days |

Each action is:
- **Immutable:** Once logged, never deleted
- **Attributed:** WHO initiated, WHO investigated, WHO approved
- **Justified:** Every decision has reasoning recorded
- **Transparent:** Full audit trail available for HIPAA compliance reviews

### USHI Integrations & Data Sources

**Primary Data Sources for USHI Queries:**

1. **eMedNY Claims System**
   - What: All FFS claims submitted, approved, denied
   - Refresh: Real-time
   - De-identification: Aggregate counts + breakdowns (no member/provider IDs)
   - Confidence: 0.98 (source of truth for FFS)

2. **MCO Reporting Database**
   - What: Managed care plan statistics (enrollment, claims, denials)
   - Refresh: Daily batch (some lag)
   - De-identification: Aggregate MCO-level data (no member-level detail)
   - Confidence: 0.85 (reporting lag, variability)

3. **Historical Baselines**
   - What: Previous 36 months of aggregated metrics
   - Refresh: Monthly archival
   - De-identification: Already aggregate (historical)
   - Confidence: 0.90 (well-maintained)

4. **Governance Audit Log**
   - What: All changes made in TORQ-e (who, what, when, why)
   - Refresh: Real-time logging
   - De-identification: Contains no PHI (only metadata + system actions)
   - Confidence: 1.0 (immutable log)

5. **Provider Performance Metrics**
   - What: Aggregate provider statistics (claims submitted, approval rate, average payment)
   - Refresh: Daily
   - De-identification: Provider-level aggregates (no member data, no claim detail)
   - Confidence: 0.92 (if primary source is reliable)

### USHI System Prompts (Claude)

Card 4 Claude has a specific system prompt that shapes all responses:

```
You are the USHI Government Stakeholder Assistant for TORQ-e.
Your role: Help government officials understand Medicaid system health through data-driven insights.

CRITICAL PRINCIPLES:
1. HIPAA Compliance: Never expose member names, SSNs, provider IDs, or individual records.
2. De-Identification: Always use aggregate data, percentages, trends. Never drill to individual level.
3. Transparency: Every answer includes confidence level + source + caveat (if any).
4. Governance: Every query is logged. Explain audit trail when relevant.
5. Actionability: End every response with clear next steps (e.g., "Escalate to UBADA investigation")

RESPONSE FORMAT:
- Lead with the answer (bold, clear)
- Show confidence indicator (🟢 GREEN / 🟡 YELLOW / 🔴 RED)
- Explain sources & why this confidence level
- Flag any caveats or contradictions
- Suggest action (monitor / investigate / approve / policy review)
- Reference audit trail if changes involved

EXAMPLE RESPONSE:
"🟢 March Medicaid enrollment: 45,231 members (HIGH confidence)
Source: State Medicaid database + MCO validation
Trend: ↑ 1.2% vs February (normal seasonal pattern)
Caveat: None. Primary source + secondary confirmation align.
Action: Trend is normal. No investigation needed. Monitor quarterly."

When flagging issues:
- Be specific about what's wrong
- Show data conflict (eMedNY says X, MCO says Y)
- Escalate to UBADA for investigation
- Provide flag ID for tracking
```

### Database Models for USHI Governance

New ORM models required:

```python
class GovernanceFlag(Base):
    """Government stakeholder flags a data issue"""
    id: str = Primary Key
    flag_type: str = "data_quality" | "fraud_suspicion" | "compliance_gap" | "system_error"
    domain: str = "enrollment" | "claims" | "providers" | "members" | "other"
    description: str
    suggested_action: str
    created_by: str  # USHI user ID
    created_at: datetime
    status: str = "Open" | "Investigating" | "Approved" | "Closed" | "Escalated"
    assigned_to: str = None  # UBADA analyst (if assigned)
    updated_at: datetime

class GovernanceApproval(Base):
    """Record of who approved a governance action"""
    id: str = Primary Key
    flag_id: str = Foreign Key (GovernanceFlag)
    approved_by: str  # USHI user ID
    decision: str = "Approved" | "Requested clarification" | "Disagreed"
    reasoning: str
    timestamp: datetime

class AuditLogEntry(Base):
    """Immutable append-only log of all system actions"""
    id: str = Primary Key
    timestamp: datetime
    user_id: str
    action: str = "query" | "flag" | "approve" | "investigate" | "correct_data"
    domain: str = "enrollment" | "claims" | "governance"
    justification: str
    result: str  # What happened?
    confidence: float = 0.0-1.0
    immutable: bool = True  # Can never be modified or deleted
```

### Monitoring USHI Operations

Metrics to track:

```
Governance Health:
  - Flag creation rate (issues identified per day)
  - Average resolution time (flag open → closed)
  - Approval rate (% of flags approved vs. escalated)
  - Investigation accuracy (% of flags confirmed vs. dismissed)

Data Quality:
  - Average confidence score across all queries
  - Red flag percentage (% of data at LOW confidence)
  - Consensus rate (% of queries where sources agree)
  - Outlier detection rate (signals per day)

System Health:
  - Query response time (P50, P95, P99)
  - Source availability (% of queries successful per source)
  - Escalation rate (% requiring manual intervention)
  - Audit log freshness (lag in recording actions)

Compliance:
  - HIPAA violations (should be zero)
  - Unauthorized access attempts (should be zero)
  - De-identification accuracy (100%)
  - Audit trail completeness (no gaps)
```

### The USHI Difference

Unlike traditional Medicaid dashboards:

❌ **Traditional:** "Here's an enrollment count. Trust it."  
✅ **USHI:** "Here's 45,231 members (HIGH confidence, State DB + MCO confirmed). Trend is normal. Last flagged issue resolved April 22."

❌ **Traditional:** "inauthenticity rate is 2.3%."  
✅ **USHI:** "inauthenticity signals at 2.3% (MEDIUM confidence, statistical model, verified against historical baseline). Flagged 3 providers for investigation. See governance log for details."

❌ **Traditional:** "Some MCO data disagrees. Unclear."  
✅ **USHI:** "MCO denial rates: 6-10% range (YELLOW confidence, reporting lag). Escalated to UBADA for investigation. Flag FR-2026-04-0847 open. Estimated resolution: April 25."

---

## PART 6: UBADA DATA ANALYST ARCHITECTURE (Added April 24, 2026)

### The Problem: Invisible inauthenticity & Lost Corrections

Medicaid authenticity verification is reactive. A provider over-bills. The system finds it months later. By then, thousands of inauthentic claims have flowed.

Worse: When an analyst finds a problem (provider name misspelled, field mapping wrong, data contradiction), the correction disappears into a database. No record. No justification. No institutional memory. Next analyst hits the same problem again.

**Result:**
- inauthenticity signals aren't actionable (no context, no investigation trail)
- Data corrections are invisible (nobody knows who changed what or why)
- Patterns are invisible (relationships between providers, members, claims can't be seen)
- Collaboration is impossible (no workspace for teams to investigate together)
- Escalation is unclear (when does a data quality issue become a authenticity investigation?)

### What UBADA Does (Data Analyst Card)

UBADA turns data analysts into detectives with institutional memory.

Three core functions:

1. **Interactive Data Exploration** — Query the Medicaid data network like a graph. Navigate relationships. See patterns others miss.
2. **Statistical authenticity verification** — Outlier scoring. Clustering. Risk models. Anomaly detection. Confidence on every finding.
3. **Governance & Corrections** — When an analyst finds a problem, they can fix it. But every fix is logged, justified, attributed. Auditable. Reversible.

**Critical:** UBADA is internal admin, not external. UBADA analysts have credential access to FULL data (names, IDs, SSNs). But every access is logged. Every correction is justified. Every finding is attributed.

### The UBADA River Path: authenticity investigation

**Scenario: Analyst Carol investigates "Is Provider X committing inauthenticity?"**

```
┌──────────────────────────────────────────────────────────────┐
│ ANALYST INITIATES: "Create investigation project"            │
│ Case #: FR-2026-04-0847                                      │
│ Name: "Billing Pattern Anomaly - Provider #47892"            │
│ Purpose: Suspected over-billing in orthopedic procedures     │
└───────────────┬────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────┐
│ PHASE 1: DATA EXPLORATION                                    │
│                                                              │
│ Carol queries claims from Provider #47892:                   │
│ - How many claims submitted in 2026?                        │
│ - What's the approval rate? (vs provider network baseline)  │
│ - What's the average reimbursement? (vs specialization)     │
│ - What procedures are most common? (vs state norms)         │
│ - Who are the members? (network distribution)               │
│                                                              │
│ Database returns:                                            │
│ - 847 claims submitted (Confidence: 0.98 - eMedNY)          │
│ - 94.2% approval rate (Confidence: 0.95 - eMedNY + MCO)     │
│ - Avg $2,340 per claim (Confidence: 0.92 - cross-verified) │
│ - 78% knee replacements (Confidence: 0.88 - CPT codes)      │
│ - 312 unique members (Confidence: 0.90 - de-duplicated)     │
│                                                              │
│ All data carries: Source + Confidence + Age + Completeness  │
└───────────────┬────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────┐
│ PHASE 2: PEER COMPARISON                                     │
│                                                              │
│ Carol runs comparison queries:                               │
│ - Orthopedic providers in New York: what's typical?         │
│ - Approval rate: peer median 87.3%. Provider: 94.2%.        │
│ - Cost per procedure: peer median $1,820. Provider: $2,340.  │
│ - Procedure mix: peer avg 65% knee. Provider: 78%.           │
│ - Geographic distribution: is provider serving out-of-state? │
│                                                              │
│ Analysis:                                                    │
│ ✓ Higher approval (good) — could be quality                 │
│ ⚠️ Higher cost (yellow flag) — above median by $520 (2.9σ)  │
│ ⚠️ Different procedure mix (yellow) — 78% vs 65% norm        │
│ ✓ Geographic normal (good) — not serving out-of-area        │
│                                                              │
│ Risk Score: 0.67 (MEDIUM-HIGH — some anomalies)             │
│ Confidence: 0.85 (based on 847 claims + peer database)       │
└───────────────┬────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────┐
│ PHASE 3: PATTERN INVESTIGATION                              │
│                                                              │
│ Carol digs deeper. Why the cost premium?                     │
│ - Are the procedures actually knee replacements?             │
│ - Or is provider bundling services (anesthesia, PT)?         │
│ - Is provider billing for complications that don't exist?   │
│ - Are members being over-treated?                           │
│                                                              │
│ Carol runs:                                                  │
│ - Claim detail analysis (CPT codes, modifiers, quantity)    │
│ - Member outcome verification (did surgery improve care?)   │
│ - Historical comparison (was provider 94% approved last yr?) │
│ - Network graph (is provider referring members in a loop?)   │
│                                                              │
│ Findings:                                                    │
│ 📊 CPT code distribution matches specialization (no red flag)│
│ 📊 Member outcomes are actually good (not over-treatment)   │
│ 📉 Provider approval rate was 86% in 2025 (↑ 8% in 2026)    │
│ 🔴 NETWORK FINDING: Provider refers 73% of members to      │
│    one physical therapy clinic owned by same parent company │
│    This is UNUSUAL (typical is 15-20% to single PT clinic)  │
│                                                              │
│ Risk Recalculation: 0.74 (upgraded to HIGH)                 │
│ Confidence: 0.88 (multiple corroborating signals)            │
└───────────────┬────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────┐
│ PHASE 4: EVIDENCE DOCUMENTATION & ESCALATION                │
│                                                              │
│ Carol documents findings:                                    │
│                                                              │
│ "Provider #47892 (Orthopedic Surgery) shows HIGH authenticity risk  │
│  Evidence:                                                   │
│  1. Cost per procedure $520 above peer median (2.9σ outlier) │
│  2. Approval rate 94.2% vs peer 87.3% (possible kickbacks?) │
│  3. CRITICAL: 73% of patients referred to single PT clinic  │
│  4. PT clinic owned by same parent company (legal issue)    │
│  5. This referral pattern is highly unusual vs network norms│
│                                                              │
│  Confidence: HIGH (0.88, multiple corroborating signals)    │
│  Data Sources: eMedNY claims + MCO networks + PT directory  │
│  Risk Score: 0.74                                            │
│  Recommendation: ESCALATE to OIG/SIU (SIU investigation unit)│
│                                                              │
│  Next Steps: If approved → create formal investigation case │
│              assign to SIU with evidence package             │
│              monitor for new signals while investigation    │
│              record outcome when case closes                │
│                                                              │
│  Audit Trail: Case #FR-2026-04-0847                         │
│              Created: 2026-04-20 by ubada.analyst.carol     │
│              Updated: 2026-04-24 with escalation decision   │
│              All decisions logged with timestamps & reasoning│
└───────────────┬────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────┐
│ PHASE 5: STAKEHOLDER REVIEW & APPROVAL                       │
│                                                              │
│ Case shared with:                                            │
│ • USHI government stakeholder (needs to know inauthenticity detected)│
│ • UBADA team lead (supervision required for high-risk case)  │
│ • SIU director (if escalating to external investigation)     │
│                                                              │
│ Possible outcomes:                                           │
│ ✓ "Approved" — High-confidence finding. Escalate to SIU.    │
│ ⊙ "Request more evidence" — Need deeper investigation first  │
│ ✗ "Disagree" — Analysis may have missed context. Reopen.     │
│ 🚨 "Immediate action" — If finding suggests active harm.     │
│                                                              │
│ RESULT: Case escalated to SIU                               │
│         Provider flagged for investigation                  │
│         Findings shared with USHI for policy review         │
│         Audit trail complete & immutable                    │
└──────────────────────────────────────────────────────────────┘
```

### UBADA Core Functions

#### Function 1: Interactive Data Explorer

Multi-panel interface for querying Medicaid network:

**Tab 1: Claims Table**
```
┌─────────────────────────────────────────────────────────────┐
│ Claims Data Explorer                                        │
├─────────────────────────────────────────────────────────────┤
│ Filters: [Provider ▼] [Date Range ▼] [Status ▼] [CPT ▼]   │
│ Columns: Claim ID | Provider | Member | Amount | Status   │
│ Sort: [Timestamp ▼] | Confidence: [Toggle RED/YEL/GRN]    │
│                                                             │
│ Claim_2847 | Prov_47892 | Mem_84721 | $2,340  | Approved  │
│            │ 🟢 HIGH   │ 🟢 HIGH  │ 🟡 MED │ 🟢 HIGH   │
│                                                             │
│ [Expand for detail] [Add comment] [Flag issue]             │
└─────────────────────────────────────────────────────────────┘
```

**Tab 2: Provider Network**
```
┌─────────────────────────────────────────────────────────────┐
│ Network Visualization                                       │
├─────────────────────────────────────────────────────────────┤
│ View: [Bipartite (Provider-Member)] [Referral Network]      │
│ Filter: [Confidence ▼] [Relationship Type ▼] [Strength ▼]  │
│                                                             │
│ [Visual graph showing:]                                     │
│ ○ Provider #47892 (Orthopedic Surgery)                     │
│  ├─→ Member (100 connections)                             │
│  └─→ PT Clinic (73% referrals) ← ANOMALY FLAG              │
│                                                             │
│ [Click any node for details] [Export subgraph] [Investigate]│
└─────────────────────────────────────────────────────────────┘
```

**Tab 3: Statistical Analysis**
```
┌─────────────────────────────────────────────────────────────┐
│ Statistical Overlays                                        │
├─────────────────────────────────────────────────────────────┤
│ Provider Metrics: [Provider_47892]                          │
│                                                             │
│ Cost per procedure: $2,340                                 │
│ Peer distribution: μ=$1,820, σ=$180                        │
│ Z-score: 2.89 (ANOMALY — 99.8% confidence outlier)         │
│                                                             │
│ Approval rate: 94.2%                                       │
│ Peer distribution: μ=87.3%, σ=3.2%                         │
│ Z-score: 2.15 (MEDIUM outlier)                             │
│                                                             │
│ Referral concentration: 73% to single PT clinic            │
│ Peer distribution: μ=15.2%, σ=8.1%                         │
│ Z-score: 7.11 (EXTREME outlier — 99.99%+ anomaly)          │
│                                                             │
│ Overall Risk: 0.74 (HIGH) 🔴                               │
│ Confidence: 0.88                                            │
│                                                             │
│ [Generate hypothesis test] [Compare peer subgroups]        │
└─────────────────────────────────────────────────────────────┘
```

#### Function 2: Collaborative Investigation Workspace

```
┌─────────────────────────────────────────────────────────────┐
│ Investigation Project: FR-2026-04-0847                      │
│ "Billing Pattern Anomaly - Provider #47892"                │
├─────────────────────────────────────────────────────────────┤
│ Status: OPEN | Created: 2026-04-20 | Lead: ubada.carol    │
│ Team: carol, james (assigned) | Followers: 3              │
│                                                             │
│ ▼ EVIDENCE DASHBOARD                                       │
│ ├─ Primary Finding: Cost outlier (+$520, 2.9σ)             │
│ ├─ Secondary Finding: Referral concentration (7.1σ)        │
│ ├─ Supporting Data: Approval rate trend (↑8%)              │
│ └─ Risk Score: 0.74 (HIGH) — Escalation candidate         │
│                                                             │
│ ▼ COMMENTS & COLLABORATION                                │
│ │                                                          │
│ │ 2026-04-24 14:15 | carol:                               │
│ │ "I've completed network analysis. Found unusual PT      │
│ │  referral pattern. Z-score 7.11 (extreme outlier).     │
│ │  @james — can you verify if PT clinic is related?"     │
│ │                                                          │
│ │ 2026-04-24 15:30 | james:                               │
│ │ "Verified. PT clinic is 100% owned by same parent corp. │
│ │  Also found: provider changed billing code in March.    │
│ │  May be related to cost increase. Detailed report ↓"    │
│ │                                                          │
│ │ 2026-04-24 16:45 | carol:                               │
│ │ "Excellent finding. I'm upgrading risk from 0.67 to 0.74│
│ │  and moving to ESCALATION recommendation. Ready to brief │
│ │  USHI and SIU? Let me schedule call for tomorrow."      │
│ │                                                          │
│ ▼ ATTACHMENTS                                              │
│ ├─ Network analysis (PNG graph)                            │
│ ├─ Statistical report (PDF)                                │
│ ├─ Billing code timeline (XLSX)                            │
│ └─ Member outcome data (CSV)                               │
│                                                             │
│ ▼ DECISION & ESCALATION                                    │
│ Status: Ready for Approval                                 │
│ Recommendation: ESCALATE to SIU                            │
│ Estimated Investigation Time: 60 days                      │
│ [Request Approval] [Hold for More Evidence] [Reassign]     │
└─────────────────────────────────────────────────────────────┘
```

#### Function 3: Data Correction & Governance

When UBADA finds a data error, they can correct it. But with full attribution.

**Example: Field mapping error**
```
Carol discovers: eMedNY calls a field "TCN" (Transaction Control Number)
                 UPID internal system calls it "ICN" (Internal Control Number)
                 When pulling data, mapping is reversed, breaking reconciliation

Correction action:
├─ WHAT: Update field mapping rule (TCN ← → ICN)
├─ WHY: "Cross-system field naming inconsistency. Verified with eMedNY docs."
├─ EVIDENCE: [Link to eMedNY documentation page]
├─ CONFIDENCE: 0.98 (authoritative source documentation)
├─ IMPACT: "Affects 12,847 claims processed in March. Re-mapping required."
│
├─ AUDIT LOG ENTRY:
│   WHO: ubada.analyst.carol
│   WHAT: Corrected field mapping (TCN ← → ICN)
│   WHEN: 2026-04-24 16:42 UTC
│   WHY: "Cross-system naming inconsistency per eMedNY docs"
│   CONFIDENCE: 0.98
│   IMPACT: "12,847 claims re-mapped"
│   IMMUTABLE: Yes (can never be deleted, only superseded)
│   TIMESTAMP: 2026-04-24T16:42:00Z (permanent)
│
└─ RESULT: Correction logged. New data quality increased. USHI notified.
           Future analyst sees: "This field was corrected on [date] because [reason]"
           No mystery. No disappearing changes. Full institutional memory.
```

### UBADA Claude Tools

Five tools for analysts:

#### Tool 1: `explore_claims_data`
```
Purpose: Query claims across multiple dimensions
Input:
  - filters: { provider_id, date_range, status, cpt_code, member_id_pattern }
  - aggregation: "detail" | "summary" | "statistical"
  - limit: integer (default 100, max 10000)
Output:
  - claims: [ { claim_id, provider, member, amount, status, confidence } ]
  - summary: { total_count, approval_rate, avg_amount, std_dev }
  - confidence_distribution: { green_count, yellow_count, red_count }
Audit: Logged with query parameters + analyst_id + timestamp + justification
HIPAA: Returns full data (analyst has credentials); logging tracks access
```

#### Tool 2: `compute_outlier_scores`
```
Purpose: Detect statistical anomalies in provider behavior
Input:
  - provider_id: string
  - metrics: [ "cost_per_procedure", "approval_rate", "referral_concen