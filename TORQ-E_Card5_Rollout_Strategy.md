# TORQ-E Card 5: Fraud Investigation & Data Analytics (UBADA)
## Rollout Strategy & Implementation Roadmap

**Status:** DESIGN → BUILD → TEST → DEPLOY  
**Version:** 1.0.0 (Planning)
**Created:** 2026-04-25
**Target GA:** TBD (Post-Card 4 validation)

---

## Executive Summary

Card 5 (UBADA - Unified Behavioral Analytics & Detection Analysis) is the **fraud investigation and data analytics layer** for TORQ-e. It transforms raw signals from Cards 1-4 into actionable fraud cases with evidence chains, pattern analysis, and investigation workflows.

**Key Difference from Card 4:**
- **Card 4:** Shows system health (is everything working?)
- **Card 5:** Investigates anomalies (is there fraud happening?)

**Integration Model:** Card 5 consumes signals from all upstream cards but operates as an **independent investigation system** with its own casework, evidence management, and investigator workflows.

---

## Architecture Overview

### What Card 5 Does

1. **Signal Ingestion:** Consumes fraud signals from Cards 1-4
2. **Pattern Detection:** Identifies suspicious clusters (billing patterns, eligibility anomalies, provider networks, etc.)
3. **Case Management:** Creates, escalates, and tracks fraud investigation cases
4. **Evidence Chain:** Maintains immutable audit trail of all investigator actions
5. **Reporting:** Generates findings, referrals to OMIG, settlement recommendations

### Core Systems

```
Card 5 Architecture:

Fraud Signal Intake
  ↓
Pattern Detection Engine
  ↓
Case Management System
  ↓
Evidence & Audit Trail
  ↓
Investigator Interface (Chat)
  ↓
Reporting & Escalation
```

### Fraud Signal Types (From Upstream Cards)

**From Card 1 (Members):**
- Duplicate enrollments
- Eligibility gaming (disenroll/reenroll cycles)
- Address clustering (fraud rings)
- Death record mismatches

**From Card 2 (Providers):**
- Billing pattern anomalies
- Credential inconsistencies
- Network clustering (credentialing fraud)
- Billing to inactive/dead providers

**From Card 3 (Programs/Plans):**
- Benefit coordination failures
- Plan-switching anomalies
- Coverage gaps

**From Card 4 (Governance):**
- Compliance violations
- Audit trail gaps
- Data quality issues (data manipulation signals)

---

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1-2)
- [ ] Fraud signal data model (extends Card 4 signal architecture)
- [ ] Case management database schema
- [ ] Evidence chain/audit logging (immutable append-only)
- [ ] API endpoints for case CRUD operations
- [ ] Backend: 5 core endpoints

**Endpoints:**
```
POST /api/card5/create-case        → Start new fraud investigation
POST /api/card5/add-evidence       → Log investigator action/finding
GET  /api/card5/case/{case_id}     → Retrieve case with full history
GET  /api/card5/cases?status=open  → List cases by status
POST /api/card5/escalate-case      → Mark for OMIG referral
```

### Phase 2: Pattern Detection Engine (Week 2-3)
- [ ] Statistical anomaly detection (Z-score, isolation forest)
- [ ] Network graph analysis (provider/member clustering)
- [ ] Timeline analysis (sequence pattern detection)
- [ ] Behavioral baseline comparison
- [ ] Automatic signal → case routing

**Patterns to Detect:**
- Provider billing networks (unusual collaborations)
- Member eligibility rings (coordinated gaming)
- Timing clusters (statistically improbable enrollment volumes)
- Cross-card signal correlation (multiple dimensions flagging same entity)

### Phase 3: Investigator Interface (Week 3-4)
- [ ] Conversational chat interface (similar to Card 4)
- [ ] Case exploration queries ("Show me all cases involving Provider XYZ")
- [ ] Evidence visualization (timeline, network graph, metrics)
- [ ] Action logging (every investigator action is immutable)
- [ ] Elaboration system (explain why case was opened, what evidence exists)

**Query Types:**
- "What fraud cases are open?" (status queries)
- "Show me cases involving this provider" (entity search)
- "What's the evidence for case #12345?" (case detail)
- "Pattern analysis: clusters of providers" (network analysis)
- "Timeline: when did this member's behavior change?" (temporal analysis)

### Phase 4: Integration & Testing (Week 4-5)
- [ ] End-to-end workflow: Signal → Detection → Case → Investigation
- [ ] Cross-card validation (signal flow from Cards 1-4)
- [ ] Investigator testing (OMIG or internal QA)
- [ ] Evidence chain validation (audit trail integrity)
- [ ] Performance testing (response times, pattern detection speed)

### Phase 5: Deployment & Handoff (Week 5-6)
- [ ] Deploy to Railway (alongside Cards 1-4)
- [ ] Documentation (DR;AN for investigators)
- [ ] Training materials (how to use investigation interface)
- [ ] Escalation process (OMIG referral workflow)
- [ ] Go-live with initial cases

---

## Data Model

### FraudSignal (extends Card 4 SystemSignal)

```javascript
{
  id: string,
  source_card: enum (CARD_1_MEMBERS, CARD_2_PROVIDERS, CARD_3_PROGRAMS, CARD_4_GOVERNANCE),
  signal_type: enum (
    DUPLICATE_ENROLLMENT,
    ELIGIBILITY_GAMING,
    PROVIDER_NETWORK_ANOMALY,
    BILLING_PATTERN_ANOMALY,
    CREDENTIAL_INCONSISTENCY,
    DEATH_RECORD_MISMATCH,
    ADDRESS_CLUSTERING,
    TIMING_ANOMALY,
    COVERAGE_GAP,
    COMPLIANCE_VIOLATION
  ),
  risk_score: number (0-100),
  confidence: number (0-100),
  affected_entities: {
    member_ids: string[],
    provider_ids: string[],
    plan_ids: string[]
  },
  pattern_evidence: {
    pattern_type: string,
    supporting_signals: string[],
    statistical_significance: number
  },
  timestamp: datetime (immutable),
  source_audit_trail: string (reference back to originating card's audit log)
}
```

### FraudCase (Investigation Container)

```javascript
{
  id: string,
  status: enum (OPEN, UNDER_INVESTIGATION, ESCALATED, CLOSED, REFERRED_TO_OMIG),
  created_at: datetime,
  created_by: string (system | investigator),
  signals: FraudSignal[],
  case_title: string,
  summary: string,
  evidence: Evidence[],
  investigator_notes: string[],
  risk_assessment: {
    estimated_overpayment: number (USD),
    confidence: number (0-100),
    recommended_action: enum (CLOSE, MONITOR, INVESTIGATE, ESCALATE)
  },
  audit_trail: {
    all_actions: [{
      timestamp: datetime,
      actor: string,
      action: string,
      change: object,
      immutable_hash: string
    }]
  }
}
```

---

## Integration Points

### Signal Flow

```
Card 1 (Members) → Fraud Signals (eligibility, duplicates)
Card 2 (Providers) → Fraud Signals (billing, credentialing)
Card 3 (Programs) → Fraud Signals (benefits, coverage)
Card 4 (Governance) → Fraud Signals (compliance, audit)

All signals → Card 5 Signal Intake
           → Pattern Detection Engine
           → Case Assignment
           → Investigator Queue
```

### Spectrum Analyzer Adaptation

Card 5 will use a **modified lights system** (different from Card 4):
- **Coherence Level:** Overall fraud risk (single light: green=low, yellow=medium, red=high)
- **Case Breakdown:** Open cases by severity, stage, entity type
- **Pattern Strength:** Confidence in detected patterns

Details TBD pending Card 1-3 lights system modifications.

---

## Success Criteria

**Immediate (Pre-GA):**
- [ ] Can ingest signals from all 4 upstream cards
- [ ] Pattern detection achieves 85%+ precision on known fraud patterns
- [ ] Evidence chain is immutable (0 gaps in audit trail)
- [ ] Investigator can search cases, view evidence, log actions
- [ ] All 6 test queries (analogous to Card 4) pass

**Post-GA (30-day validation):**
- [ ] OMIG investigator validates usefulness of cases
- [ ] Actionable fraud identified and referred
- [ ] Investigation time reduced vs. manual process
- [ ] False positive rate < 15%
- [ ] System stability (99%+ uptime)

---

## Testing Strategy

### 6 Core Test Queries (Investigator Perspective)

1. **"What fraud cases are open right now?"** → List with status/risk
2. **"Show me all cases involving Provider ABC"** → Network analysis
3. **"What's the evidence for case #12345?"** → Evidence chain display
4. **"Any high-risk cases in the last 7 days?"** → Filtered case list
5. **"Analyze billing patterns for this provider network"** → Pattern visualization
6. **"Give me a complete fraud summary"** → Full system status report

### QA Checkpoints

- Signal ingestion works for all 4 upstream cards
- Pattern detection doesn't miss known fraud (sensitivity check)
- False positive rate acceptable (specificity check)
- Evidence trail is complete and immutable
- Investigator can take actions and have them logged
- Elaborations provide sufficient detail for decision-making

---

## Deployment Timeline

| Phase | Duration | Deliverable | Status |
|-------|----------|-------------|--------|
| Design & Planning | 1 week | This document | ✅ DONE |
| Core Infrastructure | 1-2 weeks | Backend, database, APIs | 🔜 NEXT |
| Pattern Detection | 1-2 weeks | Detection engine, accuracy tuning | 📋 PLANNED |
| Investigator Interface | 1 week | Chat UI, queries, elaborations | 📋 PLANNED |
| Integration Testing | 1 week | End-to-end validation | 📋 PLANNED |
| GA Deployment | 1 week | Live on Railway, training | 📋 PLANNED |
| **Total Estimated** | **6 weeks** | **Full Card 5 System** | 🎯 TARGET |

---

## Dependencies & Blockers

**Hard Dependencies:**
- Card 4 must be locked & validated (✅ DONE 2026-04-25)
- Signal schema from Cards 1-4 must be stable
- Database infrastructure ready (Railway Postgres)

**Soft Dependencies:**
- OMIG stakeholder availability for QA testing
- Investigator requirements clarification (UX design)
- Pattern library (known fraud patterns for ML training)

---

## Notes for Implementation

- **Immutability First:** Every action by investigators becomes immutable audit trail. Deletion is never allowed; only "case closed" or "case superseded by case X"
- **Confidence in Patterns:** Don't just flag anomalies; explain why they're suspicious (Z-score, network density, temporal clustering, etc.)
- **Evidence Presentation:** Make it easy for investigators to follow the chain. "Here's signal X, here's why it matters, here's what other signals correlate"
- **No Single-Signal Cases:** Require at least 2 independent signals before opening a case. Reduces false positives.
- **Elaboration is Key:** Like Card 4, every response includes the lights + ability to elaborate. Investigators need to understand *why* the system flagged something.

---

## Success Message

Card 5 is successful when:
1. OMIG investigator can find fraud cases through natural language queries
2. Evidence is presented clearly with full audit trail
3. System detects fraud faster than manual review
4. False positive rate is low enough to be actionable
5. Every investigator action is immutable and auditable

**Then:** Move to Cards 1, 2, 3 enhanced implementations with their modified lights systems.

