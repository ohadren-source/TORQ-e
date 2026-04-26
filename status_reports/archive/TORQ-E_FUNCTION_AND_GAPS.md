# TORQ-e: Card Functions & Implementation Gaps

**Date:** April 24, 2026  
**Scope:** Complete system audit (63 files)  
**Purpose:** Answer two questions before proceeding with Card 4 design

---

## QUESTION 1: IS THE FUNCTION OF EVERY CARD CLEAR?

### CARD 1 (UMID - Unified Member Identity & Data): ✅ CLEAR & IMPLEMENTED

**Function:** Answer member question: "Am I eligible for Medicaid?"

**What It Does:**
- Member provides name/DOB/SSN
- System executes River Path across 3 data sources:
  1. State Medicaid database (0.98 confidence)
  2. SSA wage records (0.95 confidence)  
  3. Household enrollment (0.70 confidence)
- Returns eligibility status with confidence score
- Generates caveats if confidence below 0.85
- Shows clear next steps (call number, upload docs, recertification date)

**Claude Integration:** 
- Tools: `lookup_member`, `check_eligibility`, `check_recertification`
- Chat responds with eligibility status in plain English
- BUT: Confidence data not passed to Claude (Claude doesn't know confidence level)

**Interface:**
- Enrollment gate: "Do you have a UMID?"
- Chat: Member asks questions, Claude provides eligibility info
- Markdown formatting: working with parser fix

**Completeness:** ~85%
- Core logic: ✅ Complete
- Confidence framework: ✅ Complete (but not used by Claude)
- UI: ✅ Working
- Gap: Claude doesn't receive confidence context

---

### CARD 2 (UPID - Unified Provider Identity & Data): ✅ CLEAR & MOSTLY IMPLEMENTED

**Function:** Answer provider questions: "How do I get paid?" / "What's my enrollment status?" / "Where do I submit claims?"

**What It Does:**
- Provider provides NPI
- System executes River Path across 3 sources:
  1. eMedNY FFS enrollment (0.95 confidence)
  2. MCO aggregator (0.85 confidence)
  3. NPI database (0.70 confidence)
- Returns enrollment status (FFS/MCO/both), claims routing, payment info
- Validates claims for errors before submission
- Detects fraud signals on submitted claims

**Claude Integration:**
- Tools: `lookup_provider`, `check_enrollment`, `validate_claim`
- Chat responds with enrollment status, claims guidance, next steps
- BUT: Confidence data returned but not passed to Claude context
- BUT: Fraud detection engine exists but integration with chat unclear

**Interface:**
- Enrollment gate: "Do you have a Provider ID?"
- Chat: Provider asks about enrollment/claims, Claude provides answers
- Markdown formatting: working with parser fix

**Completeness:** ~70%
- Core logic: ✅ Complete (lookup + routing + fraud detection)
- Confidence framework: ⚠️ Basic (returns score but no consensus logic like Card 1)
- UI: ✅ Working
- Gaps: 
  - No signal-over-noise scoring (Card 1 has it, Card 2 doesn't)
  - Claude doesn't receive confidence context
  - Fraud detection not clearly integrated with chat

---

### CARD 3 (WHUP - Unified Health & Wellness Program): ❌ UNCLEAR & UNIMPLEMENTED

**Intended Function:** Answer plan administrator: "Who's in my network? Are we adequate?"

**What It SHOULD Do:**
- Load member roster for plan
- Show provider directory + network status
- Monitor network adequacy (specialty coverage, geographic access)
- Track plan performance metrics (denial rates, wait times)
- Escalate issues to MCO operations

**Current State:**
- ❌ No backend implementation (no card_3_uhwp directory)
- ⚠️ Frontend stubs exist (login, chat, tutorial)
- ❌ No Claude tools defined
- ❌ No database models for plans/networks/adequacy

**Why Unclear:**
Because the design questions aren't answered:
- What data sources? (Plan member roster, UPID reference, network adequacy standards?)
- What River Path? (Does it cascade across multiple MCOs?)
- What confidence framework? (How confident is roster data?)
- What veracity visualization? (Should plan admins see red/yellow/green?)

**Status:** Design needed before implementation

---

### CARD 4 (USHI - Universal Stakeholder Health Information): ⚠️ FUNCTION RECENTLY CLARIFIED BUT UNIMPLEMENTED

**Intended Function:** Answer government stakeholder: "How efficient/compliant is the system?"

**What It SHOULD Do (just designed today):**
- Expose aggregate system metrics (enrollment rates, claim processing times, denial rates)
- Show data quality/veracity with red/yellow/green indicators
- Display governance audit trail (who changed what, why)
- Allow stakeholders to flag data issues with full attribution
- Support HIPAA compliance requirements

**Current State:**
- ❌ No backend implementation (no card_4_ushi directory)
- ⚠️ Frontend stubs exist
- ❌ No Claude tools defined
- ❌ No database models for governance/audit
- ❌ No red/yellow/green UI component
- ❌ No specification for what tools/data sources should exist

**Design Status:** 
✅ Function clarified (just today)
✅ Governance model designed (Change 12 in DR.md)
✅ Three-tier transparency UI sketched
❌ Backend specification NOT written yet
❌ Database models NOT defined yet

**Blockers for Implementation:**
1. Formal specification document (what tools, data sources, metrics?)
2. Red/yellow/green UI component design & CSS
3. Governance/audit trail database schema
4. Claude system prompt clarification (what should Card 4 Claude do?)

**Status:** BLOCKED - Specification needed before implementation

---

### CARD 5 (UBADA - Universal Business/Data Analyst): ⚠️ FUNCTION RECENTLY CLARIFIED BUT UNIMPLEMENTED

**Intended Function:** Answer data analyst: "Is this fraud? What patterns do I see? What needs correcting?"

**What It SHOULD Do (just designed today):**
- Interactive data explorer (claims, providers, members, relationships)
- Granular statistical analysis (z-scores, outlier detection, clustering)
- Governance/audit trail for data corrections analysts make
- Collaboration workspace for investigation projects
- Red/yellow/green veracity on every data element

**Current State:**
- ❌ No backend implementation (no card_5_ubada directory)
- ⚠️ Frontend stubs exist
- ❌ No Claude tools defined
- ❌ No database models for investigations/corrections/collaboration
- ❌ No data explorer UI
- ❌ No collaboration features
- ❌ No red/yellow/green visualization

**Design Status:**
✅ Function clarified (just today)
✅ Data governance model designed (Change 12 in DR.md)
✅ Analyst audit trail conceptually designed
❌ Detailed specification NOT written yet
❌ Database models NOT defined yet
❌ Data explorer UI NOT designed yet

**Blockers for Implementation:**
1. Card 4 specification (Card 5 inherits same red/yellow/green patterns)
2. Formal specification for data explorer
3. Database models for data corrections, investigations, collaboration
4. UI/UX design for multi-panel analyst workspace
5. Claude tools definition (what can analysts query?)

**Status:** BLOCKED - Awaiting Card 4 completion (dependency)

---

## QUESTION 2: ARE THERE GAPS OR FUNCTIONALITIES UNACCOUNTED FOR?

### CRITICAL GAPS

#### 1. **Confidence Data Not Flowing Through Claude** (BOTH Cards 1 & 2)
**The Problem:**
- Card 1 routes return `confidence_score` in the JSON response
- Card 2 routes return `confidence_score` in the JSON response
- But Claude tools don't receive this in the tool context
- Claude's explanations don't reflect the confidence level
- Example: Claude says "You're eligible" without knowing if it's 0.95 confidence or 0.60

**Impact:**
- Members/Providers get answers without understanding data quality
- Claude can't explain why answers should be trusted differently
- Veracity is invisible even though it's been calculated

**What's Needed:**
- Modify `execute_tool()` in chat.py to pass confidence + caveat data to Claude context
- Update Card 1 & 2 system prompts to include confidence in explanations
- Example new prompt: "When you explain eligibility, note the confidence level: 'Your status is confirmed with high confidence (State Medicaid data)' or 'This is based on partial data so verify with caseworker'"

**Fix Complexity:** Medium (routing change + prompt update)

---

#### 2. **Red/Yellow/Green Veracity Visualization Doesn't Exist Anywhere** (CRITICAL for Cards 4 & 5)
**The Problem:**
- Design exists in DR.md (Change 12)
- No UI component built
- No CSS for color-coded confidence
- No mapping of 0.0-1.0 confidence to color + label
- Cards 4 & 5 can't be designed without this

**Impact:**
- Government stakeholders can't see data quality visually
- Data analysts can't see which data points are trustworthy
- Entire governance layer is invisible

**What's Needed:**
- Reusable UI component (HTML + CSS)
- Three-tier design:
  - Tier 1: Badge showing "HIPAA-Compliant Audit Trail"
  - Tier 2: Expandable card with recent changes
  - Tier 3: Full audit log with search/filter
- Color coding:
  - 🟢 GREEN (0.85-1.0): "HIGH - Authoritative source"
  - 🟡 YELLOW (0.60-0.84): "MEDIUM - Cross-verified with concerns"
  - 🔴 RED (<0.60): "LOW - Manual verification needed"
- Tooltip showing: source, age, completeness, agreement level

**Fix Complexity:** High (new component + integration)

---

#### 3. **Card 2 Missing Signal-Over-Noise Framework** (Gap between Cards 1 & 2)
**The Problem:**
- Card 1 has `score_consensus()` method (consensus scoring across multiple sources)
- Card 2 has basic confidence (0.95/0.85/0.70) but no consensus logic
- When Card 2 sources disagree (eMedNY vs MCO), there's no principled way to score confidence
- Example: eMedNY says provider is active, MCO says enrolled with restrictions—how confident should we be?

**Impact:**
- Card 2 responses less reliable when sources conflict
- No formalized way to combine conflicting data

**What's Needed:**
- Port Card 1's `ConfidenceScorer.score_consensus()` to Card 2
- Implement agreement metric for provider data conflicts
- Update provider_lookup.py to use consensus scoring

**Fix Complexity:** Medium (code migration + testing)

---

#### 4. **Governance/Audit Trail Framework Not Modeled** (Critical for Cards 4 & 5)
**The Problem:**
- DR.md has governance design (Change 12)
- No database models for governance actions
- No schema for:
  - Who made the change (UBADA ID, USHI ID)
  - What they changed (data field, old value, new value)
  - Why (justification text)
  - Audit trail (immutable, append-only log)
  - Collaboration (comments, peer review)

**Impact:**
- Can't implement governance features without models
- Can't track data corrections
- Can't maintain institutional memory

**What's Needed:**
- New ORM models:
  - `DataCorrection` - record of who changed what data element when
  - `GovernanceAction` - record of government stakeholder actions (flags, challenges, approvals)
  - `InvestigationProject` - UBADA collaboration workspace
  - `InvestigationComment` - peer review threads
  - `AuditLog` (extend existing) - comprehensive event log

**Fix Complexity:** Medium (database design + migrations)

---

#### 5. **Card 3 Not Designed at All** (Complete Gap)
**The Problem:**
- No specification for what Card 3 should do
- No backend
- Frontend stubs only

**Impact:**
- Can't implement until designed

**What's Needed:**
- Specification: "What questions does a plan administrator ask?"
- River Path design: "What data sources?"
- Confidence framework: "How confident in plan data?"
- Tools definition: "What Claude tools should exist?"

**Fix Complexity:** High (requires full design phase)

---

#### 6. **Card 4 Not Fully Specified** (Incomplete Design)
**The Problem:**
- Function clarified today (Change 12)
- Governance model designed
- But formal specification missing:
  - What data sources for government queries?
  - What River Path for system metrics?
  - What specific Claude tools?
  - What templates for governance actions?
  - What compliance mappings?

**Impact:**
- Backend can't be built without specification
- UI can't be designed without clarity on what data/actions exist

**What's Needed:**
- Formal Card 4 specification document covering:
  - Government stakeholder use cases
  - Data sources (claims, enrollments, metrics, audit logs)
  - River Path (cascade of verification sources)
  - Tools (what queries Claude can execute)
  - Governance actions (flag, request change, approve)
  - Compliance mappings (HIPAA requirements, CMS regulations)
  - Red/yellow/green visualization rules
  - Audit trail design
- Update TORQ_E_ARCHITECTURAL_PROTOCOL.md with Card 4 details

**Fix Complexity:** High (requires detailed specification)

---

#### 7. **Card 5 Data Explorer UI Doesn't Exist** (Complete Gap)
**The Problem:**
- Designed conceptually today
- No actual UI built
- No data explorer, no collaboration features

**Impact:**
- Can't show analysts any data
- Can't support investigations

**What's Needed:**
- Data explorer UI:
  - Multi-tab interface (Claims, Providers, Members, Relationships)
  - Sortable/filterable tables with confidence overlays
  - Network visualization (relationship graphs)
  - Statistical analysis overlays (outliers, z-scores)
- Collaboration UI:
  - Project management (create investigation, invite team)
  - Comment threads
  - Peer review workflows
  - Export/share capabilities
- Governance UI:
  - Data correction interface
  - Justification forms
  - Audit trail viewer

**Fix Complexity:** Very High (large UI feature set)

---

#### 8. **Fraud Detection Integration Unclear** (Card 2)
**The Problem:**
- Card 2 has `fraud_detection.py` module
- Returns fraud signals with risk scores
- But unclear how it integrates with chat
- No Claude tools explicitly expose fraud analysis
- No clear "when do we escalate to investigation?"

**Impact:**
- Fraud detection exists but isn't exposed to users/analysts
- No clear pathway from fraud signal → investigation

**What's Needed:**
- Clarify: Should fraud signals appear in Card 2 chat?
- Or should Card 5 pull fraud signals for investigation?
- Define: What triggers escalation to Card 5?
- Wire: fraud_detection module into Card 2 tools and/or Card 5 tools

**Fix Complexity:** Medium (clarification + tool wiring)

---

### SUMMARY TABLE: Gaps by Card

| Gap | Card 1 | Card 2 | Card 3 | Card 4 | Card 5 |
|-----|--------|--------|--------|--------|--------|
| **Confidence → Claude** | ❌ | ❌ | — | — | — |
| **Signal-Over-Noise** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Red/Yellow/Green UI** | — | — | — | ❌ CRITICAL | ❌ CRITICAL |
| **Governance Models** | ⚠️ | ⚠️ | ❌ | ❌ CRITICAL | ❌ CRITICAL |
| **Data Explorer UI** | — | — | — | — | ❌ |
| **Collaboration UI** | — | — | — | — | ❌ |
| **Specification** | ✅ | ✅ | ❌ | ⚠️ INCOMPLETE | ⚠️ INCOMPLETE |
| **Backend Implementation** | ✅ | ✅ | ❌ | ❌ | ❌ |

---

## RECOMMENDATIONS: What to Do First

### IMMEDIATE (Before Building Anything Else)

1. **Wire Confidence Through Claude** (Cards 1 & 2)
   - Modify chat.py tool execution to include confidence metadata
   - Update system prompts to reference confidence in explanations
   - Complexity: Medium
   - Timeline: 2-4 hours

2. **Design & Specify Card 4 Completely**
   - Use today's governance model (Change 12) as foundation
   - Write formal specification document
   - Define tools, data sources, use cases
   - Update TORQ_E_ARCHITECTURAL_PROTOCOL.md
   - Complexity: Medium
   - Timeline: 4-8 hours

3. **Build Red/Yellow/Green UI Component**
   - Reusable veracity visualization component
   - Three-tier transparency design
   - Color-coded confidence indicators
   - Tooltip/expanded details
   - Complexity: High
   - Timeline: 6-10 hours

### SECONDARY (After Above)

4. Port Signal-Over-Noise to Card 2
5. Define Governance Database Models
6. Specify Card 3 completely
7. Begin Card 4 backend + governance audit trail
8. Specify Card 5 data explorer + collaboration
9. Build Card 5 data explorer UI
10. Implement Card 5 backend

---

## CRITICAL ORDERING DEPENDENCY

```
Fix Confidence → Claude (1-2 hours)
    ↓
Design Card 4 Spec (4-8 hours)
    ↓
Build Red/Yellow/Green Component (6-10 hours)
    ↓
Implement Card 4 Backend + Audit Trail
    ↓
Design Card 5 Full Spec
    ↓
Implement Card 5 Backend + Explorer + Governance
```

Don't skip the early steps. Each builds on the last.
