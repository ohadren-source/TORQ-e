# TORQ-e: Complete Specification Summary
## Foundation Work Complete (April 24, 2026)

**Status:** Architecture specification phase COMPLETE. Ready for implementation.

---

## Executive Summary: The Three Pillars

TORQ-e is built on three pillars that distinguish it from all existing Medicaid solutions:

### 1. **Confidence & Transparency (Cards 1 & 2)**
- Every query result shows where the data came from
- Every result shows how confident we are in that data
- Users understand data reliability without technical jargon
- Signal-over-noise consensus: when sources disagree, we tell you why

### 2. **HIPAA-Compliant Governance (Cards 4 & 5)**
- **Card 4 (USHI):** Government oversight with aggregate-only access (de-identified, minimum necessary principle)
- **Card 5 (UBADA):** Fraud investigation with full-identified access BUT complete audit logging (every query, every correction, every decision recorded)
- Governance is visible on the facade (three-tier transparency)
- Every action is auditable + attributed + justified (immutable append-only logs)

### 3. **Institutional Memory (Dynamic Source Management)**
- System learns: which sources are reliable, which are problematic
- Analysts can strike unreliable sources + add new reliable sources
- Every source decision is logged + justified
- Over time, confidence improves because the system learns

---

## What Was Completed

### 1. Card 4 (USHI - Government Stakeholder) - FULLY SPECIFIED ✅

**Added to:** TORQ_E_ARCHITECTURAL_PROTOCOL.md PART 5 (3,200+ lines)

**Specification Includes:**
- Problem statement: Government officials lack visibility into system health
- Five core responsibilities: compliance monitoring, fraud detection, performance tracking, data quality assessment, governance actions
- Complete River Path example: denial rate query flowing through 3 data sources
- Five use cases with River Path for each
- HIPAA compliance requirements mapped to design
- Red/Yellow/Green veracity visualization rules
- Three-tier transparency UI/UX architecture
- Five Claude tools specified with input/output contracts
- Governance action workflow: FLAG → INVESTIGATE → APPROVE → AUDIT
- Database models for governance tracking
- Complete monitoring metrics
- System prompt for Card 4 Claude

**Key Design Principle:** HIPAA minimum necessary principle enforced. USHI can only see aggregate, de-identified data. No member names. No provider IDs. Only patterns, trends, counts.

**Ready For:** Backend implementation (governance audit trails, queries, Claude tools)

---

### 2. Card 5 (UBADA - Data Analyst) - FULLY SPECIFIED ✅

**Added to:** TORQ_E_ARCHITECTURAL_PROTOCOL.md PART 6 (4,200+ lines)

**Specification Includes:**
- Problem statement: Fraud signals are invisible, corrections disappear, patterns can't be seen
- Three core functions: interactive data exploration, statistical fraud detection, governance & corrections
- Detailed fraud investigation workflow (5 phases): exploration → peer comparison → pattern investigation → evidence documentation → escalation
- Three UI components: Claims table, Network visualization, Statistical analysis
- Collaborative investigation workspace: projects, comments, peer review, evidence tracking
- UBADA data access rules: FULL access to identified data, but everything logged
- Five Claude tools specified: claims explorer, outlier scorer, relationship navigator, investigation creator, correction requester
- Complete investigation workflow: 6 steps from initiation to follow-up
- Database models for investigations, corrections, collaboration
- Monitoring metrics for investigation health
- System prompt for Card 5 Claude

**Key Design Principle:** UBADA has FULL data access (names, SSNs, IDs) but with complete audit logging. Every query, every correction, every decision is recorded with WHO/WHAT/WHEN/WHY.

**Ready For:** Backend implementation (data explorer, investigation workspace, Claude tools)

---

### 3. Red/Yellow/Green Component - FULLY SPECIFIED ✅

**Created:** RED_YELLOW_GREEN_COMPONENT_SPEC.md (2,200+ lines)

**Specification Includes:**
- Confidence-to-veracity mapping: 0.85-1.0 → GREEN, 0.60-0.84 → YELLOW, <0.60 → RED
- Four rendering modes:
  1. Inline Badge (minimal: color + label)
  2. Inline Indicator (badge + source)
  3. Expandable Card (full detail with collapsible section)
  4. Tooltip (hover detail)
- Data structure (TypeScript interface for confidence objects)
- JavaScript API (RYGComponent class with all methods)
- Integration examples for both Card 4 & Card 5
- Full accessibility requirements (WCAG AA compliance)
- Testing checklist
- Implementation plan (files to create)

**Key Design Principle:** Color + text + icon + tooltip provide layered information. No reliance on color alone (accessibility). Responsive design scales from badge to full card.

**Ready For:** Frontend implementation (shared component for Cards 4 & 5)

---

### 4. ECHOSYSTEM Generalization - COMPLETE ✅

**Updated:** ECHOSYSTEM_DEFINITION.md

**New Addition:** 
- Added antonym documentation (Echo Chamber)
- Clarified distinction between ECHOSYSTEM (all surfaces verified) and echo chamber (isolated reinforcement)
- Provided example showing how contradictions stay hidden in echo chamber but surface in ECHOSYSTEM

**Key Insight:** ECHOSYSTEM is what prevents fragmented systems from hiding dysfunction. The echo IS the system.

---

### 5. Gap Analysis & Accountability - COMPLETE ✅

**Documented:**
- TORQ-E_FUNCTION_AND_GAPS.md: Comprehensive audit of what's built vs. what's needed
- DR.md: Append-only log of all decisions (Changes 1-17)
- HIPAA_TO_TORQ-E_MAPPING.md: Regulatory requirements mapped to system design

**Key Finding:** The real value proposition is "auditable clarity about the reliability of its own data." As data quality improves, confidence scores increase visibly.

---

## Architecture Now Complete

### What's Specified

| Component | Specification | Status |
|---|---|---|
| Card 1 (UMID) Member Eligibility | PART 2 | ✅ LIVE |
| Card 2 (UPID) Provider System | PART 2 + PART 4 | ✅ LIVE |
| Card 4 (USHI) Government Stakeholder | PART 5 | ✅ SPEC COMPLETE |
| Card 5 (UBADA) Data Analyst | PART 6 | ✅ SPEC COMPLETE |
| Governance & Audit Trail | PART 5 & 6 | ✅ SPEC COMPLETE |
| Red/Yellow/Green Component | Separate document | ✅ SPEC COMPLETE |
| HIPAA Compliance | Separate document | ✅ DOCUMENTED |
| ECHOSYSTEM Framework | Separate document | ✅ GENERALIZED |

### What's Excluded (Deferred)

| Component | Reason |
|---|---|
| Card 3 (WHUP) Plan Administrator | Read-only dashboard; lower priority than governance cards 4 & 5 |

---

## Key Architectural Decisions

### 1. Governance as Core, Not Bolted-On
**Principle:** Every data access, every correction, every decision is logged with full attribution.

**Implementation:** Audit trail is immutable, append-only, HIPAA-compliant. This is not optional—it's regulatory requirement.

**Impact:** Users see governance on the facade (three-tier transparency). Builds trust in the system.

---

### 2. De-Identification by Role
**Principle:** USHI sees aggregate + de-identified data only. UBADA sees full data but with complete audit logging.

**Implementation:**
- USHI: Counts, percentages, trends, relationships (no names/IDs)
- UBADA: Full identified data, but every query logged with WHO/WHAT/WHEN/WHY

**Impact:** Complies with HIPAA minimum necessary. Government gets oversight without exposing PHI.

---

### 3. Confidence Flows Everywhere
**Principle:** Every data point carries confidence score + source + freshness + completeness + caveat.

**Implementation:**
- Card 1 & 2 (live): Confidence calculated but not passed to Claude (gap to fix)
- Card 4 & 5 (specs): Confidence is foundational to every query result

**Impact:** Users understand data reliability. System learns (confidence increases with better data).

---

### 4. River Path as Core Algorithm
**Principle:** Graceful degradation. Try primary source. If fails, try secondary. If fails, try tertiary. If all fail, escalate with reason.

**Implementation:**
- Every lookup follows this pattern
- Never hangs. Never crashes. Never gives wrong answer invisibly.
- Always explains why it failed and next step

**Impact:** System is recoverable. Users know why they got an answer (or why they didn't).

---

### 5. Investigation as Collaborative, Auditable Process
**Principle:** When analyst finds fraud, they can document it in a workspace with peers, then escalate with full evidence package.

**Implementation:**
- Investigation project with team assignment
- Comments, peer review, evidence attachments
- Every action logged with attribution
- Escalation creates formal case with full audit trail

**Impact:** Institutional memory. No mysteries. Next analyst sees history.

---

## Critical Success Factors

### 1. Governance Audit Trail Must Be Built First
**Why:** Both Cards 4 & 5 depend on it. Can't show government stakeholder dashboard without audit trail. Can't show data analyst workspace without audit trail.

**What:** Create database models (GovernanceFlag, GovernanceApproval, InvestigationProject, etc.) + API endpoints to log/retrieve actions

**Timeline:** ~8-12 hours of backend work

---

### 2. Red/Yellow/Green Component Must Be Reusable
**Why:** Cards 4 & 5 both use it extensively. Build once, use everywhere.

**What:** Create RYGComponent class (JavaScript) + CSS + HTML tests. Component must work in all four modes (badge, inline, expandable, tooltip).

**Timeline:** ~6-10 hours of frontend work

---

### 3. Claude Tools Must Match Specification
**Why:** If Claude tools don't align with specified behavior, entire system breaks down. Users get different answers than expected.

**What:** Implement each tool exactly as specified in PART 5 & 6. No shortcuts. Test thoroughly.

**Timeline:** ~20-30 hours of backend + testing work

---

### 4. Confidence Data Must Flow Through to Claude
**Why:** Currently (Cards 1 & 2), confidence is calculated but Claude doesn't see it. Users get answers without understanding data quality.

**What:** Modify `execute_tool()` in chat.py to pass confidence + caveat data to Claude context. Update system prompts.

**Timeline:** ~4-6 hours of refactoring + testing

---

## Implementation Roadmap

### Phase 1: Foundation (Shared Infrastructure)
**Goal:** Build components both Cards 4 & 5 depend on

1. **Governance Database Models** (8 hrs)
   - GovernanceFlag, GovernanceApproval, InvestigationProject, InvestigationComment, DataCorrection, OutlierFinding
   - API endpoints to create/read/update actions

2. **Red/Yellow/Green Component** (10 hrs)
   - RYGComponent JavaScript class
   - CSS for all modes
   - Accessibility verification

3. **Wire Confidence Through Claude** (6 hrs)
   - Modify chat.py to pass confidence in tool results
   - Update Card 1 & 2 system prompts to explain confidence
   - Test with sample queries

**Subtotal: ~24 hours**

---

### Phase 2: Card 4 (USHI)
**Goal:** Build government stakeholder dashboard

1. **Card 4 Backend** (20 hrs)
   - Implement 5 Claude tools (aggregate_metrics, fraud_signals, data_quality, governance_log, flag_issue)
   - Query engine for government-level data (aggregate, de-identified)
   - Governance action handlers (flag, investigate, approve)

2. **Card 4 Frontend** (16 hrs)
   - Dashboard layout (metrics + KPIs)
   - Three-tier transparency UI (badge, expandable card, full log)
   - Governance action forms (flag, approve, challenge)
   - Red/Yellow/Green integration

**Subtotal: ~36 hours**

---

### Phase 3: Card 5 (UBADA)
**Goal:** Build data analyst investigation workspace

1. **Card 5 Backend** (24 hrs)
   - Implement 5 Claude tools (explore_claims, compute_outliers, navigate_graph, create_investigation, request_correction)
   - Graph database + network visualization engine
   - Statistical analysis library (Z-scores, clustering, outlier detection)
   - Investigation project management + collaboration

2. **Card 5 Frontend** (20 hrs)
   - Multi-panel data explorer (claims table, network graph, statistics)
   - Investigation workspace (comments, peer review, evidence attachments)
   - Data correction interface
   - Red/Yellow/Green integration

**Subtotal: ~44 hours**

---

### Total: ~104 hours of implementation work

(Assuming 1-2 developers, ~6-8 weeks of focused development)

---

## What's NOT Changing

- **Card 1 (UMID):** Already live. No architectural changes needed.
- **Card 2 (UPID):** Already live. Only change: wire confidence through Claude (phase 1).
- **Main.py:** Demo scope confirmed (Cards 1, 2, 4, 5 only; Card 3 excluded).
- **River Path Algorithm:** No changes. Cards 4 & 5 inherit same principles.

---

## Success Criteria

By end of implementation:

- [ ] Card 4 (USHI) dashboard shows government stakeholder metrics with confidence indicators
- [ ] Card 4 governance log is immutable and audit-compliant (HIPAA-ready)
- [ ] Card 5 data explorer allows investigators to query claims, providers, networks
- [ ] Card 5 investigation workspace supports peer collaboration + evidence tracking
- [ ] All confidence scores flow through Claude responses (Cards 1, 2, 4, 5)
- [ ] Red/Yellow/Green component works consistently across both cards
- [ ] All Claude tools match specification exactly
- [ ] All database models and audit trails are immutable and append-only
- [ ] System is HIPAA-compliant (verified through audit log)
- [ ] Users can see governance (three-tier transparency)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Governance logging becomes bottleneck | Slow queries, system lag | Use async logging, separate audit database |
| Red/Yellow/Green component complex to test | Bugs cause visibility issues across cards | Comprehensive unit + integration tests, accessibility audit |
| Claude tools don't align with spec | Users get unexpected behavior | Rigorous spec review, test each tool against spec |
| De-identification rules unclear | HIPAA violations risk | Legal review of de-identification implementation |
| Investigation workspace too complex | Users struggle to use it | User testing during development, iterative refinement |

---

## Documentation Locations

All specifications are findable:

- **TORQ_E_ARCHITECTURAL_PROTOCOL.md** — Main architecture document (PARTS 1-6)
  - PART 1: Plain Language overview
  - PART 2: Technical deep dive (Cards 1, 2)
  - PART 3: Governance & accountability
  - PART 4: UPID provider enrollment
  - PART 5: USHI government stakeholder (NEW)
  - PART 6: UBADA data analyst (NEW)

- **RED_YELLOW_GREEN_COMPONENT_SPEC.md** — Veracity visualization component (NEW)

- **HIPAA_TO_TORQ-E_MAPPING.md** — HIPAA requirements mapped to design

- **ECHOSYSTEM_DEFINITION.md** — Domain-agnostic framework + antonym

- **DR.md** — Accountability log (Changes 1-17)

- **TORQ-E_FUNCTION_AND_GAPS.md** — Gap analysis & completeness audit

---

## Principle Reminder

The covenant stands:

**Don't design systems that hide what they're doing.**

TORQ-e shows its work. Governance is visible. Confidence is explicit. Contradictions surface. Corrections are attributed. Users understand why they got an answer.

This is what makes it trustworthy.

---

**Status:** Specification foundation complete. Ready for implementation phase.

**Date:** April 24, 2026
