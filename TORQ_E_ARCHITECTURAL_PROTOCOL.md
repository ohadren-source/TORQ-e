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
- The state has fraud happening because it can't track one person across systems
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
- **UHWP** (Universal Health & Wellness Program) — Never changes. Tracks plan enrollment and network status.
- **USHI** (Universal Stakeholder ID) — Never changes. Gives government oversight the full picture.
- **UBADA** (Universal Business/Data Analyst ID) — Never changes. Gives fraud investigators the tools to detect patterns.

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
│  │     │ (UHWP)         │  │ (UBADA)                 │ │  │
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
│  │     /api/analyst/fraud-assessment                    │  │
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
│  │ 3. State Lic │ │ UHWP_RECORDS │ │ Eligibility  │       │
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
│  │  CMS NPPES registry      │  │  Fraud pattern detection │
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

**Card 3: UHWP (Plan Admin)**
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
- Question: "Is this fraud?"
- River Path: Billing patterns → Peer comparison → Outcome verification
- Success = Fraud risk score + evidence
- Escalation = "Investigation case created"

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

**Last Updated:** April 24, 2026  
**Status:** LIVE. This document governs all TORQ-e development.  
**Authority:** Architecture, implementation, testing, deployment.

**This is the covenant.**
