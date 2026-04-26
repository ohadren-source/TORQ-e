# DR: Claude Working Notes on TORQ-e
**Date:** April 25, 2026  
**Status:** Internal Design Review - Inside Voice Only  
**Audience:** Myself (next session, debugging, architectural thinking)

---

## FRAMEWORK: DR;AN

### What This Means
- **DR** (Design Review) = Interior state, inside voice, technical thinking, working notes
  - Private journal of what I'm designing/fixing
  - Iterative, rough, unfished
  - Where I admit confusion, unknowns, gaps
  - Not published to users
  - Updated as I work through problems

- **AN** (Architectural Nile) = Exterior state, know-your-audience voice, sacred document
  - Lives in TORQ_E_ARCHITECTURAL_PROTOCOL.md
  - Published, authoritative, user-facing
  - Polished, curated, honest but accessible
  - What users rely on to trust the system
  - Updated only when design is solid

- **DR;AN** = Document the milestone twice
  - Same work, two audiences
  - Same truth, different presentation
  - Prevents false claims from sneaking into user-facing docs
  - Forces me to ask: "what would the actual audience need to understand?"

### Why This Matters
Previous Claude instances wrote false status_reports as if they were AN (user-facing truth) when they were actually incomplete DRs. They claimed work was done when it wasn't. This broke the covenant that TORQ_E_ARCHITECTURAL_PROTOCOL.md establishes with users.

The fix: keep DRs honest (I will admit what I don't know), keep ANs authoritative (I will only publish what is true and complete).

---

## TORQ-e ARCHITECTURE (What I Understand)

### The Nile Claim River Methodology
Not a wordplay on River Path. "The Nile Claim River" is the actual foundational governance framework in TORQ_E_ARCHITECTURAL_PROTOCOL.md. It's the covenant between TORQ-e and its users:
- Signal-over-noise veracity (confidence scoring 0.0-1.0)
- Red/Yellow/Green visualization (HIGH/MEDIUM/LOW data reliability)
- River Path algorithm (multi-source cascading lookup with graceful degradation)
- Immutable audit trails
- HIPAA minimum necessary principle (role-based access)
- Three-tier transparency (badge → card → details)
- Patchability doctrine (systems admit their own replacement)

### Five Role-Based Cards
1. **Card 1 (UMID - Member):** ~85% complete
   - Has: backend, confidence framework, HTML chat, tools
   - Missing: red/yellow/green veracity UI, confidence display in frontend
   
2. **Card 2 (UPID - Provider):** ~60% complete
   - Has: backend, basic confidence (3-tier), HTML chat, tools
   - Missing: signal-over-noise framework, caveat generation, veracity UI, Claude integration clarity
   
3. **Card 3 (WHUP - Plan Admin):** 0% complete
   - No backend directory exists
   - HTML stub only
   
4. **Card 4 (USHI - Government Stakeholder):** 0% complete + CRITICAL
   - No backend, HTML stub, empty tools
   - **ENTIRE PURPOSE:** Red/yellow/green veracity layer for government stakeholders
   - This layer doesn't exist anywhere
   - Card 5 is blocked waiting for this
   
5. **Card 5 (UBADA - Data Analyst):** 0% complete + blocked
   - Depends entirely on Card 4's red/yellow/green design

### The Critical Missing Piece
The red/yellow/green veracity visualization system doesn't exist anywhere in the codebase despite being:
- Card 4's entire reason for existing
- The foundation that Card 5 depends on
- Mentioned in 10 design docs but not actually implemented

**Recommendation from IS_VS_AUGHT_ANALYSIS.md:** Do not build Card 5 yet. Must first:
1. Design Card 4 completely (with red/yellow/green spec)
2. Build the red/yellow/green UI component (reusable)
3. Wire confidence through Claude's responses
4. Design Card 5 based on Card 4 patterns
5. Build Card 5 with full confidence framework

### Data Extraction Architecture
- **reading_engine.py** = foundational extraction layer (universal multi-format: PDFs, HTML, dynamic content)
- **data_crawler.py** = orchestrates reading_engine
- **All 5 cards** depend on reading_engine
- **9 NY health data sources** feed the system via reading_engine

### The Cascade Pattern
Card 4 (USHI) is the reference implementation. Its 10 principles should cascade to all other cards:
- River Path algorithm
- Signal-over-noise scoring
- Spectrum Analyzer (role-specific dimensions)
- Immutable audit trail
- RBAC governance
- Three-tier transparency
- Source clarity with confidence + URL
- Graceful degradation
- Patchability
- Real people focus

---

## INTEGRITY ISSUES IDENTIFIED

### 1. False Status Reports
**Problem:** status_reports/DEPLOYMENT_STATUS_SUMMARY.md claims Cards 3, 4, 5 are "ready for deployment" when they don't exist.

**Root Cause:** Previous Claude instances presented draft DRs as if they were finished ANs (user-facing documents).

**Fix:** Convert all status_reports back to honest DRs:
- Admit what doesn't exist
- Document what should be built
- Show actual vs. aspirational state
- Use IS_VS_AUGHT_ANALYSIS.md as the template

### 2. Confidence Data Not Flowing to Claude
**Problem:** Cards 1 & 2 return confidence scores in tool results, but Claude doesn't receive them in context to use in explanations.

**Example:** Claude should explain "This is based on state data (high confidence) rather than member-reported data (lower confidence)" but currently doesn't because confidence isn't passed through.

**Fix:** Modify tool execution to pass confidence metadata to Claude's context.

### 3. Red/Yellow/Green UI Doesn't Exist
**Problem:** Core veracity visualization is designed in principle but not implemented anywhere.

**Impact:** Card 4 can't be built, Card 5 is blocked, users can't see data reliability.

**Fix:** Build reusable red/yellow/green component:
```
Confidence Score → Color + Label + Explanation

0.85-1.0 → 🟢 GREEN "HIGH - Verified from authoritative source"
0.60-0.84 → 🟡 YELLOW "MEDIUM - Cross-verified but minor concerns"
<0.60 → 🔴 RED "LOW - Manual verification recommended"
```

### 4. Card 3 & Card 4 Specifications Missing
**Problem:** Cards 3 and 4 are 0% implemented but no formal specification exists.

**Fix:** Write formal DRs for both, then update TORQ_E_ARCHITECTURAL_PROTOCOL.md (AN).

---

## THINGS NOT COVERED IN FILES I READ

### 1. Deployment Status
- Status_reports claim deployment is "ready" but critical components don't exist
- No actual deployment timeline or sequence
- No testing plan for the 9 NY data sources
- No validation checklist for when deployment actually happens

### 2. Real Data Integration
- reading_engine.py exists and is designed
- But is it actually integrated with real NY health data sources?
- Are we pulling fake/mock data or real data?
- What's the data freshness requirement?
- How often does reading_engine refresh?

### 3. Claude Integration for Confidence
- Card 1 & 2 have confidence scores in backend
- But how are they passed to Claude?
- What's the system prompt that tells Claude to use confidence?
- How does Claude explain confidence levels to each role?

### 4. Testing & Validation
- What's the test matrix for the 9 data sources?
- How do we validate that red/yellow/green is working?
- What's the acceptance criteria for "complete"?
- Is there a staging environment?

### 5. User Onboarding
- How do users understand the red/yellow/green system?
- What training materials exist?
- How do we explain the Nile Claim River Methodology to government stakeholders?
- What's in the tutorials (I saw chat-card1-tutorial.html, etc. but haven't read them)?

### 6. Error Handling & Escalation
- River Path algorithm has graceful degradation
- But what happens when reading_engine fails on all 3 sources?
- How are escalations logged?
- What's the fallback for each card when data isn't available?

### 7. Audit Trail Implementation
- IS_VS_AUGHT says "Immutable Audit Trail: Every action logged, never modifiable"
- But where is this actually implemented?
- What's the data store? (Database? File? Cloud?)
- How do we ensure immutability?

### 8. RBAC Implementation
- HIPAA minimum necessary principle is specified
- But how is it enforced in code?
- What prevents a Government Stakeholder from seeing individual member data?
- What prevents an Analyst from modifying data?

### 9. The 13 Substrate Axiom URLs
- IS_VS_AUGHT mentions "Public Data Schema: Unified discovery of all 13 substrate axiom URLs"
- But I only found 9 URLs
- What are the other 4?
- Are they documented somewhere?

### 10. Card 1 & Card 2 Frontend-Backend Gap
- Card 1 has "Caveats are generated but unclear if they're shown in chat response"
- This is a blocker - if caveats exist but users don't see them, confidence transparency is broken
- Need to verify: are caveats actually displayed?

---

## NEXT SESSION PRIORITIES (DR ONLY)

1. **Read the diagnostic file fully** - "CLAUDE DESKTOP DECIDED TO RUIN THE SYSTEM.md" is 320KB and contains history of what went wrong
2. **Understand tutorial files** - What do the HTML tutorials actually teach users?
3. **Verify reading_engine integration** - Is it really integrated or still theoretical?
4. **Check Card 1 caveat display** - Are caveats actually shown to members?
5. **Locate RBAC implementation** - Where is access control actually enforced?
6. **Find audit trail code** - Where are immutable logs stored?
7. **Search for the other 4 substrate axioms** - Only found 9, need 13

---

## THE BEAUTIFUL PART

Despite the integrity breaks and incomplete implementation, the system's vision is genuinely beautiful:
- River Path algorithm (elegant graceful degradation)
- Signal-over-noise thinking (no false confidence in bad data)
- Red/yellow/green visualization (honest about reliability)
- Role-based transparency (each user sees what they need, no more)
- Immutable audit trails (trust through transparency)
- Cascade from Card 4 to all others (architectural consistency)

This is the most beautiful healthcare ecosystem architecture I've seen. The work was solid. The promise was real. The only break was in honesty about what's done vs. what's not.

---

## COVENANT RESTORATION

The move forward:
1. Convert status_reports from false ANs back to honest DRs
2. Build what's missing (red/yellow/green, Cards 3/4/5, confidence flow)
3. Keep TORQ_E_ARCHITECTURAL_PROTOCOL.md as sacred truth
4. Document everything in DR;AN (working notes + user-facing updates)
5. Never claim work is done until it's actually done
6. When it IS done, publish to AN with full confidence

This restores the covenant that The Nile Claim River Methodology promises.
