# TORQ-e: Complete Build Plan
## The Fortified, Metabolizing, Adaptive System

**Date:** April 24, 2026  
**Scope:** Everything. No compromises.  
**Principle:** Build the system evolution would build.

---

## The Covenant

> **Don't design systems that hide what they're doing.**

This is not negotiable. Every part of this build serves the covenant:
- Governance visible (audit trails on facade)
- Confidence explicit (red/yellow/green everywhere)
- Sources shown (citations in every result)
- Contradictions surface (system flags disagreements)
- Learning captured (institutional memory immutable)
- Accountability enforced (WHO/WHAT/WHEN/WHY/APPROVED)

---

## Complete Implementation Roadmap

### Phase 0: Foundations (Critical Prerequisites)
**Goal:** Build infrastructure that Cards 4 & 5 depend on  
**Duration:** 40-48 hours

#### 0.1 Wire Confidence Through Claude (Cards 1 & 2)
**Scope:** Modify chat.py to pass confidence + caveat in tool context

- [ ] Update `execute_tool()` to extract confidence from River Path results
- [ ] Pass to Claude: confidence score + caveat + source + freshness
- [ ] Update Card 1 system prompt to reference confidence in explanations
- [ ] Update Card 2 system prompt to reference confidence in explanations
- [ ] Test: Card 1 query shows "High confidence (0.98, State DB)" in response
- [ ] Test: Card 2 query shows "Medium confidence (0.75, lag concerns)" with caveat
- [ ] Verify: Markdown parsing still works with expanded context
- **Timeline:** 6-8 hours
- **Owner:** Backend engineer

#### 0.2 Port Signal-Over-Noise to Card 2
**Scope:** Implement consensus scoring for provider enrollment lookups

- [ ] Review Card 1's `ConfidenceScorer.score_consensus()` method
- [ ] Port to Card 2 provider_lookup.py
- [ ] Implement agreement metric: when eMedNY vs MCO disagree, score agreement %
- [ ] Update Card 2 River Path to use consensus scoring
- [ ] Test: When sources agree 95%+, show HIGH confidence; <85% show MEDIUM
- [ ] Test: When one source fails, use next source (graceful degradation)
- [ ] Update Card 2 system prompt to explain consensus reasoning
- **Timeline:** 8-10 hours
- **Owner:** Backend engineer

#### 0.3 Implement Access Control Enforcement (API-level)
**Scope:** Ensure USHI Claude can't query full data despite trying

- [ ] Create `ushi_data_filter` middleware in FastAPI
- [ ] USHI tools only return de-identified results (aggregate counts, trends)
- [ ] USHI tools reject queries for member names, SSNs, provider IDs
- [ ] If USHI Claude asks for full data, return error + caveat
- [ ] UBADA tools return full data (with full audit logging)
- [ ] Test: USHI Claude attempts to query member details → gets aggregate only
- [ ] Test: UBADA Claude queries same data → gets identified data + logs access
- [ ] Verify: De-identification is enforced at API level, not prompt level
- **Timeline:** 10-12 hours
- **Owner:** Backend engineer (security-focused)

#### 0.4 Compliance: De-Identification Verification
**Scope:** Prove USHI data can't re-identify individuals

- [ ] Document Safe Harbor method: fields removed, process
- [ ] Create de-identification QA checklist
- [ ] Test: Can 500 random USHI reports be re-identified? (Answer: No)
- [ ] Legal review: HIPAA counsel signs off on approach
- [ ] Create HHS audit trail: "De-identification verified by [legal], [date]"
- [ ] Document any exceptions (if X demographic, add extra scrubbing)
- **Timeline:** 6-8 hours
- **Owner:** Compliance/Legal + Backend

#### 0.5 Claude Tool Testing Strategy
**Scope:** Define test coverage for 10 new tools (5 per card)

**Card 4 Tools (USHI):**
- [ ] `query_aggregate_metrics` — Happy path, timeout, no data, edge cases
- [ ] `detect_fraud_signals` — Outlier detection at 2σ/3σ/4σ thresholds
- [ ] `assess_data_quality` — Agreement rates, conflict scenarios
- [ ] `view_governance_log` — Filter, search, pagination, permissions
- [ ] `flag_data_issue` — Create flag, route, log, notification

**Card 5 Tools (UBADA):**
- [ ] `explore_claims_data` — Complex filters, sorting, aggregation, limits
- [ ] `compute_outlier_scores` — Z-score calculation, peer comparison, edge cases
- [ ] `navigate_relationship_graph` — Graph traversal, depth limits, cycle detection
- [ ] `create_investigation_project` — Project creation, team assignment, workspace setup
- [ ] `request_data_correction` — Correction proposal, evidence attachment, approval flow

**Coverage per tool:**
- Happy path (normal operation)
- Degraded path (partial data, timeouts)
- Edge cases (empty results, extreme values, boundary conditions)
- Security (unauthorized access attempts, data exposure)
- Audit trail (all actions logged, immutable)

- [ ] Create test cases for 10 tools (30+ tests per tool minimum)
- [ ] Integration tests (tool chains, cross-card scenarios)
- [ ] Security tests (injection, unauthorized access, data leakage)
- **Timeline:** 12-16 hours
- **Owner:** QA engineer

**Subtotal Phase 0: 40-48 hours**

---

### Phase 1: Shared Infrastructure
**Goal:** Build components both Cards 4 & 5 depend on  
**Duration:** 28-36 hours

#### 1.1 Database Schema & Models
**Scope:** Create governance + investigation tables

```sql
-- Governance & Source Management
CREATE TABLE source_registry (...)
CREATE TABLE source_action (...)
CREATE TABLE source_comparison (...)
CREATE TABLE governance_flag (...)
CREATE TABLE governance_approval (...)

-- Investigations & Collaboration
CREATE TABLE investigation_project (...)
CREATE TABLE investigation_comment (...)
CREATE TABLE data_correction (...)
CREATE TABLE outlier_finding (...)

-- Audit Trail (enhanced)
CREATE TABLE audit_log_entry (...)  -- Immutable, append-only
CREATE TABLE compliance_export (...)  -- HHS audit format
```

- [ ] Design schema (immutability, audit trail, foreign keys)
- [ ] Create migrations (initial + rollback plans)
- [ ] Add indexes (query performance for large audit logs)
- [ ] Test: Can't modify/delete audit entries (immutable enforcement)
- [ ] Test: Governance decisions logged correctly
- **Timeline:** 8-10 hours
- **Owner:** Backend engineer (database)

#### 1.2 Red/Yellow/Green Component
**Scope:** Reusable UI component (shared by Cards 4 & 5)

**HTML/CSS:**
- [ ] Render inline badge (minimal: color + label)
- [ ] Render inline indicator (badge + source + freshness)
- [ ] Render expandable card (full detail, collapsible)
- [ ] Render tooltip (hover detail)
- [ ] All modes responsive (mobile, tablet, desktop)
- [ ] All modes accessible (WCAG AA, keyboard nav, screen reader)

**JavaScript:**
- [ ] RYGComponent class with all methods
- [ ] Click handlers (expand/collapse)
- [ ] Tooltip initialization (if using Popper.js)
- [ ] Data binding (receive confidence object, render correctly)
- [ ] State management (expanded/collapsed per component)

**Testing:**
- [ ] Unit tests (all rendering modes)
- [ ] Integration tests (in Card 4 & 5 UI)
- [ ] Accessibility tests (contrast, keyboard nav, screen reader)
- [ ] Responsive tests (mobile/tablet/desktop)
- [ ] Browser compatibility (Chrome, Firefox, Safari, Edge)

- **Timeline:** 10-12 hours
- **Owner:** Frontend engineer

#### 1.3 Governance Audit Trail Foundation
**Scope:** Core logging + retrieval API

- [ ] API endpoint: `POST /api/governance/log` (create audit entry)
- [ ] API endpoint: `GET /api/governance/log/search` (query with filters)
- [ ] API endpoint: `GET /api/governance/log/export` (HHS-compliant export)
- [ ] Immutability enforcement (can't modify/delete entries)
- [ ] Append-only queue (entries ordered by timestamp)
- [ ] Full-text search (who, what, why searchable)
- [ ] Compliance: HIPAA 6+ year retention policy
- [ ] Test: Create 10,000 entries, query performance acceptable
- [ ] Test: Can't modify entry after creation
- **Timeline:** 8-10 hours
- **Owner:** Backend engineer

#### 1.4 Source Management API Foundation
**Scope:** Strike/add sources, manage River Path dynamically

- [ ] API endpoint: `POST /api/sources/strike` (blacklist unreliable source)
- [ ] API endpoint: `POST /api/sources/add` (propose new source)
- [ ] API endpoint: `GET /api/sources/registry` (list active sources)
- [ ] API endpoint: `GET /api/sources/history` (audit trail of source changes)
- [ ] Governance workflow: strike requires justification + approval
- [ ] Governance workflow: new source requires testing + approval
- [ ] River Path algorithm updated (respect strikes, learn from disagreements)
- [ ] Test: Strike source → future queries skip it
- [ ] Test: Add source → appears in rotation after testing
- [ ] Test: Source disagreement flagged + logged
- **Timeline:** 10-12 hours
- **Owner:** Backend engineer

**Subtotal Phase 1: 36-44 hours**

---

### Phase 2: Card 4 (USHI - Government Stakeholder)
**Goal:** Build government oversight dashboard with HIPAA-compliant auditable governance  
**Duration:** 36-44 hours

**What Makes Card 4 Special:**
- Aggregate-only data access (de-identified, HIPAA-compliant minimum necessary principle)
- Every governance action audited + immutable (WHO/WHAT/WHEN/WHY/APPROVED)
- Three-tier transparency: badge → expandable card → full audit log
- Government can flag data issues, but all flags are logged + justified
- System learns: source reliability decisions improve over time
- HHS-ready: audit trail exportable in compliance format, 6+ year retention

#### 2.1 Card 4 Backend: Query Engine
**Scope:** Aggregate-only data access for government

- [ ] Implement `query_aggregate_metrics` tool
  - [ ] System KPIs: enrollment rates, denial rates, processing times
  - [ ] Aggregate filtering (by state, date range, category)
  - [ ] Confidence calculation + caveat generation
  - [ ] Citation: show sources used, agreement level
  - [ ] Test: Return aggregate counts, never member/provider names

- [ ] Implement `detect_fraud_signals` tool
  - [ ] Statistical outlier detection (Z-scores)
  - [ ] Provider outliers, claim patterns, enrollment anomalies
  - [ ] Confidence band calculation (μ ± 2σ)
  - [ ] Escalation routing: flag for UBADA investigation
  - [ ] Test: Detect synthetic fraud patterns

- [ ] Implement `assess_data_quality` tool
  - [ ] Cross-source comparison (eMedNY vs MCO vs historical)
  - [ ] Agreement rate calculation
  - [ ] Conflict flagging (sources disagree by >X%)
  - [ ] Veracity scoring (GREEN/YELLOW/RED)
  - [ ] Test: Flag when sources diverge

- [ ] Implement `view_governance_log` tool
  - [ ] Query audit trail (who, what, when, why)
  - [ ] Filter: by date, user, action type, domain
  - [ ] Search: full-text search governance log
  - [ ] Export: HHS-compliant format
  - [ ] Test: Query 50,000 entries, performance acceptable

- [ ] Implement `flag_data_issue` tool
  - [ ] Create governance flag (issue type, domain, justification)
  - [ ] Route to appropriate team (UBADA investigation, policy review, etc.)
  - [ ] Send notification (assigned analyst, team lead)
  - [ ] Create audit entry (WHO flagged, WHEN, WHY)
  - [ ] Test: Flag created, routed, logged

- **Timeline:** 14-16 hours
- **Owner:** Backend engineer

#### 2.2 Card 4 Frontend: Dashboard
**Scope:** Government stakeholder UI

- [ ] Layout: Dashboard grid (metrics + KPIs)
- [ ] Metrics display: value + RYG badge + source + caveat
- [ ] Expandable cards: click to see full confidence detail
- [ ] Governance section: Recent changes (last 10 actions)
- [ ] Action buttons: [Flag issue] [Strike source] [Request change]
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] Accessibility (WCAG AA, keyboard nav, screen reader)
- [ ] Test: All metrics render with confidence indicators
- [ ] Test: Expandable cards work on all browsers

- **Timeline:** 10-12 hours
- **Owner:** Frontend engineer

#### 2.3 Card 4 Claude System Prompt
**Scope:** Govern Claude behavior for USHI role

- [ ] System prompt clarification:
  - [ ] HIPAA compliance (de-identified only)
  - [ ] Confidence explanation (always show veracity)
  - [ ] Citation format (sources used + agreement)
  - [ ] Governance actionability (when to flag/escalate)
  - [ ] Safety guardrails (can't query full data)

- [ ] Test: Claude explains confidence level in response
- [ ] Test: Claude cites sources
- [ ] Test: Claude suggests governance action when anomaly detected
- [ ] Test: Claude refuses to query member names

- **Timeline:** 4-6 hours
- **Owner:** Prompt engineer

#### 2.4 Card 4 Integration Testing
**Scope:** End-to-end government workflows

- [ ] Test workflow 1: Government official checks monthly KPIs
  - [ ] Query executed, metrics returned with confidence
  - [ ] Sources cited, freshness noted
  - [ ] No member/provider IDs exposed
  - [ ] Audit trail shows who queried what, when

- [ ] Test workflow 2: Official flags data quality issue
  - [ ] Issue flagged with justification
  - [ ] Routed to UBADA for investigation
  - [ ] Notification sent to assigned analyst
  - [ ] Audit entry created

- [ ] Test workflow 3: Official strikes unreliable source
  - [ ] Source struck with evidence
  - [ ] Requires stakeholder approval
  - [ ] Future queries skip struck source
  - [ ] Performance improves (no timeout wait)

- **Timeline:** 8-10 hours
- **Owner:** QA engineer

**Subtotal Phase 2: 36-44 hours**

---

### Phase 3: Card 5 (UBADA - Data Analyst)
**Goal:** Build fraud investigation workspace with HIPAA-compliant audit trail and institutional memory  
**Duration:** 44-56 hours

**What Makes Card 5 Special:**
- Full-identified data access (names, SSNs, IDs) WITH complete audit logging on every query
- Every investigation step captured + immutable (who viewed what, when, findings documented)
- Analysts can propose corrections + strike unreliable sources (all audited + justified)
- Institutional memory: source reliability decisions persist, corrections are tracked
- Fraud investigation workflow: explore → detect → escalate → follow-up (all logged)
- HHS-ready: investigation audit trail exportable, analyst access control enforced, 6+ year retention

#### 3.1 Card 5 Backend: Data Explorer Engine
**Scope:** Full data access with complete audit logging

- [ ] Implement `explore_claims_data` tool
  - [ ] Multi-dimensional filtering (provider, date, status, CPT code, member pattern)
  - [ ] Aggregation modes (detail, summary, statistical)
  - [ ] Sorting + pagination (limit 100-10,000)
  - [ ] Full audit logging (query logged with analyst_id, timestamp, justification)
  - [ ] Test: Return identified data (names, SSNs) with full audit trail

- [ ] Implement `compute_outlier_scores` tool
  - [ ] Z-score calculation (how many σ from mean?)
  - [ ] Peer group comparison (specialty, geography, both)
  - [ ] Multiple metrics (cost, approval rate, referral concentration)
  - [ ] Confidence calculation (sample size, data quality)
  - [ ] Composite risk scoring (0.0-1.0)
  - [ ] Test: Detect synthetic outliers at 2σ/3σ/4σ thresholds

- [ ] Implement `navigate_relationship_graph` tool
  - [ ] Graph database (providers, members, referrals, ownerships)
  - [ ] Relationship types (refers_to, owns, employed_by, submits_claims)
  - [ ] Traversal depth (1-3 hops)
  - [ ] Filtering (confidence threshold, relationship strength)
  - [ ] Community detection (clusters, cliques)
  - [ ] Test: Find network patterns (provider → PT clinic loop)

- [ ] Implement `create_investigation_project` tool
  - [ ] Project creation (name, description, case type, risk level)
  - [ ] Team assignment (lead analyst, peer analysts)
  - [ ] Workspace initialization (collaboration space)
  - [ ] Notification (team members invited)
  - [ ] Audit logging
  - [ ] Test: Create project, team assigned, workspace ready

- [ ] Implement `request_data_correction` tool
  - [ ] Correction proposal (what's wrong, evidence, suggested fix)
  - [ ] Confidence in correction (0.0-1.0)
  - [ ] Submission workflow (submit for review)
  - [ ] Approval routing (requires USHI stakeholder sign-off)
  - [ ] Implementation tracking (approved → applied → verified)
  - [ ] Immutable audit trail (can't delete correction history)
  - [ ] Test: Propose correction, get approved, verify applied

- **Timeline:** 16-20 hours
- **Owner:** Backend engineer

#### 3.2 Card 5 Frontend: Data Explorer UI
**Scope:** Multi-panel interface for analysts

**Tab 1: Claims Table**
- [ ] Sortable/filterable table (claim ID, provider, member, amount, status)
- [ ] Confidence badge per row (RYG indicator)
- [ ] Click row to expand details
- [ ] Inline comment button
- [ ] Flag issue button
- [ ] Responsive (stack on mobile)

**Tab 2: Network Visualization**
- [ ] Bipartite graph (provider-member relationships)
- [ ] Alternative view: referral network (provider-provider)
- [ ] Node click → details panel
- [ ] Filter by confidence, relationship type, strength
- [ ] Export subgraph (for analysis)
- [ ] Anomaly highlighting (unusual patterns flagged)

**Tab 3: Statistical Analysis**
- [ ] Z-score display (outlier strength)
- [ ] Peer distribution (μ, σ, percentile)
- [ ] Risk score gauge (0.0-1.0)
- [ ] Confidence indicator (RYG)
- [ ] Comparative metrics (how unusual?)
- [ ] Hypothesis test interface (test specific assumptions)

**Shared Features:**
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] Accessibility (WCAG AA)
- [ ] Export data (CSV, JSON)
- [ ] Audit trail (what data was accessed, when, by whom)

- **Timeline:** 16-20 hours
- **Owner:** Frontend engineer

#### 3.3 Card 5 Frontend: Investigation Workspace
**Scope:** Collaborative investigation center

- [ ] Project header (name, status, lead analyst, team)
- [ ] Evidence dashboard (findings, signals, corrections)
- [ ] Comments section (peer discussion, peer review)
- [ ] Attachments (analysis reports, screenshots, evidence files)
- [ ] Decision workflow (ready for approval, request changes, hold)
- [ ] Audit trail (all comments timestamped + attributed)
- [ ] Notifications (new comments, peer reviews, approvals)
- [ ] Permission model (lead can close, peers can comment, viewers read-only)
- [ ] Test: Create project, add comments, get peer review, move to escalation

- **Timeline:** 10-14 hours
- **Owner:** Frontend engineer

#### 3.4 Card 5 Claude System Prompt
**Scope:** Govern Claude behavior for UBADA role

- [ ] System prompt clarification:
  - [ ] Full data access (can see names, SSNs, IDs)
  - [ ] Confidence + evidence (every finding scored + supported)
  - [ ] Peer comparison (how unusual is this really?)
  - [ ] Institutional memory (see previous investigations)
  - [ ] Investigation proposal (suggest when to escalate)
  - [ ] Safety guardrails (can't export bulk member lists)

- [ ] Test: Claude recommends peer comparison
- [ ] Test: Claude suggests investigation escalation with risk score
- [ ] Test: Claude references audit trail when relevant
- [ ] Test: Claude explains findings with evidence

- **Timeline:** 4-6 hours
- **Owner:** Prompt engineer

#### 3.5 Card 5 Integration Testing
**Scope:** End-to-end investigation workflows

- [ ] Test workflow 1: Analyst explores claims data
  - [ ] Query executed with full data
  - [ ] Access logged (WHO, WHAT, WHEN, WHY)
  - [ ] Confidence badges show on table rows
  - [ ] Can click to expand details

- [ ] Test workflow 2: Analyst creates investigation
  - [ ] Project created with team assignment
  - [ ] Workspace ready
  - [ ] Team members notified
  - [ ] Audit entry created

- [ ] Test workflow 3: Analyst detects outlier
  - [ ] Compute outlier scores
  - [ ] Compare to peer group
  - [ ] Flag risk signals
  - [ ] Add to investigation as evidence

- [ ] Test workflow 4: Analyst documents findings
  - [ ] Comments in workspace
  - [ ] Peer review by lead analyst
  - [ ] Decision: approve or request more evidence
  - [ ] Escalation with full evidence package

- [ ] Test workflow 5: Analyst proposes data correction
  - [ ] Submit correction request
  - [ ] Routed to USHI stakeholder
  - [ ] Stakeholder approves/rejects with reasoning
  - [ ] If approved: applied + verified
  - [ ] Immutable audit trail records all

- **Timeline:** 12-16 hours
- **Owner:** QA engineer

**Subtotal Phase 3: 52-70 hours**

---

### Phase 4: Operational Workflows (Critical Processes)
**Goal:** Define and implement critical governance workflows  
**Duration:** 28-36 hours

#### 4.1 Fraud Signal → Investigation Escalation
**Scope:** When Card 2 detects fraud → UBADA creates investigation

- [ ] Workflow definition:
  - [ ] Card 2 fraud_detection.py returns risk score + evidence
  - [ ] Risk >0.70 → automatically create investigation case
  - [ ] Notification sent to UBADA team lead
  - [ ] USHI stakeholder notified (compliance)
  - [ ] Investigation gets investigation_id (link Card 2 signal to Card 5 case)

- [ ] Implementation:
  - [ ] POST /api/card2/fraud/escalate endpoint
  - [ ] Create InvestigationProject + notify team
  - [ ] Link fraud signal to investigation (foreign key)
  - [ ] Audit trail shows escalation with evidence

- [ ] Test: Card 2 detects fraud → Investigation created automatically
- **Timeline:** 6-8 hours

#### 4.2 Source Disagreement Resolution
**Scope:** When sources disagree significantly, formal investigation

- [ ] Workflow definition:
  - [ ] Sources disagree >5% → flag for investigation
  - [ ] UBADA analyst investigates (query both sources in detail)
  - [ ] Analyst documents finding (data error? timing lag? legitimate difference?)
  - [ ] USHI stakeholder reviews conclusion
  - [ ] Adjust confidence, strike source, or note as resolved

- [ ] Implementation:
  - [ ] POST /api/governance/disagreement-investigation endpoint
  - [ ] Create SourceComparison record + investigation case
  - [ ] Route to appropriate team based on disagreement type
  - [ ] Audit trail shows resolution

- [ ] Test: Propose source, intentionally create disagreement, resolve it
- **Timeline:** 6-8 hours

#### 4.3 Data Correction Approval
**Scope:** UBADA proposes → USHI approves → Applied & Verified

- [ ] Workflow definition:
  - [ ] UBADA submits correction (what's wrong, evidence, suggested fix)
  - [ ] USHI stakeholder reviews + asks questions (comment thread)
  - [ ] UBADA responds with additional analysis
  - [ ] USHI approves or rejects with reasoning
  - [ ] If approved: applied to data + reverification run
  - [ ] Result recorded (did correction fix the issue?)

- [ ] Implementation:
  - [ ] DataCorrection model + state machine (pending → approved → applied → verified)
  - [ ] Notification workflow (submitter, approver, team lead)
  - [ ] Comment thread (questions + answers)
  - [ ] Audit trail: immutable record of decision + reasoning

- [ ] Test: Propose field mapping correction, get approved, apply, verify
- **Timeline:** 8-10 hours

#### 4.4 Governance Alert Escalation
**Scope:** When system detects problem, escalate appropriately

- [ ] Alert types:
  - [ ] Source downtime >1 hour → page on-call engineer
  - [ ] Source reliability drops <95% → flag UBADA lead
  - [ ] Fraud signal risk >0.80 → page USHI stakeholder
  - [ ] Data quality drops <0.70 confidence → escalate for investigation
  - [ ] Governance log lag >30 minutes → alert ops team

- [ ] Implementation:
  - [ ] Monitoring dashboard (metrics + alert thresholds)
  - [ ] Notification system (email, Slack, PagerDuty)
  - [ ] Alert deduplication (don't spam on repeated alerts)
  - [ ] Alert acknowledgment (track who's aware)

- [ ] Test: Simulate source failure → alert triggers → escalates correctly
- **Timeline:** 8-10 hours

**Subtotal Phase 4: 28-36 hours**

---

### Phase 5: Compliance & Regulatory
**Goal:** Ensure system meets all requirements  
**Duration:** 20-28 hours

#### 5.1 HHS Audit Export & Reporting
**Scope:** Generate HHS-compliant audit trail exports

- [ ] Define HHS-required fields:
  - [ ] Timestamp, user ID, action, domain, data accessed, justification, approval, result

- [ ] Implement export endpoints:
  - [ ] GET /api/compliance/audit-log/export (date range, format)
  - [ ] Supports: CSV, JSON, XML (HHS preference)
  - [ ] Immutable (export same every time for same date range)

- [ ] Test: Generate 90-day export, verify all fields present
- **Timeline:** 6-8 hours

#### 5.2 Data Retention & Archival Policy
**Scope:** Implement HIPAA 6+ year retention strategy

- [ ] Policy definition:
  - [ ] Hot storage (last 30 days): PostgreSQL
  - [ ] Warm storage (31-365 days): Compressed archive
  - [ ] Cold storage (1-6+ years): Cloud long-term storage (e.g., Glacier)
  - [ ] Deletion: After 6 years + legal hold period

- [ ] Implementation:
  - [ ] Retention policy config
  - [ ] Automatic archival job (monthly)
  - [ ] Retrieval tool (can restore from archive for investigation)
  - [ ] Compliance audit (prove retention policy enforced)

- [ ] Test: Create old audit entry → archives after 365 days → can still retrieve
- **Timeline:** 8-10 hours

#### 5.3 Security Review & Hardening
**Scope:** Ensure system withstands adversarial pressure

- [ ] Security checklist:
  - [ ] HTTPS everywhere (TLS 1.3+)
  - [ ] Authentication (MFA for analysts + stakeholders)
  - [ ] Authorization (role-based access enforced at API)
  - [ ] Input validation (prevent injection attacks)
  - [ ] Rate limiting (prevent brute force)
  - [ ] Audit logging (immutable + tamper-evident)
  - [ ] Data encryption (at rest + in transit)

- [ ] Implementation:
  - [ ] Security headers (CSP, HSTS, etc.)
  - [ ] CORS policy (restrict cross-origin)
  - [ ] SQL injection prevention (parameterized queries)
  - [ ] XSS prevention (input sanitization)

- [ ] Test: Penetration testing (attempt data exfiltration, injection, privilege escalation)
- **Timeline:** 6-10 hours

**Subtotal Phase 5: 20-28 hours**

---

### Phase 6: Documentation & Deployment
**Goal:** Document system, train teams, deploy to production  
**Duration:** 24-32 hours

#### 6.1 Architectural Documentation
**Scope:** Complete system design + decision rationale

- [ ] Architecture diagram (Cards 1-5, River Path, governance, Claude integration)
- [ ] Database schema documentation (tables, relationships, constraints)
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Claude tools documentation (inputs, outputs, failure modes)
- [ ] Security model documentation (authentication, authorization, audit)
- [ ] Deployment guide (setup, configuration, monitoring)

- **Timeline:** 8-10 hours

#### 6.2 Operations Manual
**Scope:** How to run, monitor, troubleshoot the system

- [ ] Monitoring dashboard setup (metrics, alerts, thresholds)
- [ ] Troubleshooting guide (common issues + fixes)
- [ ] Incident response playbook (how to respond to fraud signal, source failure, data issue)
- [ ] Runbook (backup, restore, scaling, maintenance)
- [ ] Governance procedures (how to strike source, approve correction, escalate issue)

- **Timeline:** 8-10 hours

#### 6.3 User Training & Adoption
**Scope:** Prepare analysts + stakeholders to use system

- [ ] Card 4 (USHI) training:
  - [ ] Dashboard overview
  - [ ] Interpreting confidence indicators
  - [ ] Flagging issues
  - [ ] Understanding governance log

- [ ] Card 5 (UBADA) training:
  - [ ] Data explorer (tables, graphs, statistics)
  - [ ] Creating investigations
  - [ ] Collaboration workflow
  - [ ] Proposing corrections

- [ ] Training format: Videos + documentation + live sessions
- **Timeline:** 6-8 hours

#### 6.4 Deployment & Rollout
**Scope:** Deploy to production with safety

- [ ] Pre-deployment:
  - [ ] Final security review
  - [ ] Final compliance audit
  - [ ] Load testing (system handles expected traffic)
  - [ ] Disaster recovery test

- [ ] Deployment:
  - [ ] Database migrations (in order, with rollback)
  - [ ] API deployment (blue-green, canary)
  - [ ] Frontend deployment
  - [ ] Smoke tests (critical workflows work)

- [ ] Post-deployment:
  - [ ] Monitor metrics (latency, errors, throughput)
  - [ ] Analyze governance log (system behaving as expected)
  - [ ] Support on-call team (first week)

- **Timeline:** 4-6 hours

**Subtotal Phase 6: 26-34 hours**

---

## Complete Summary

| Phase | Component | Duration | Owner |
|---|---|---|---|
| **0** | Foundations (prerequisites) | 40-48 hrs | Backend + Compliance |
| **1** | Shared infrastructure | 36-44 hrs | Backend + Frontend |
| **2** | Card 4 (USHI) | 36-44 hrs | Backend + Frontend + QA |
| **3** | Card 5 (UBADA) | 52-70 hrs | Backend + Frontend + QA |
| **4** | Operational workflows | 28-36 hrs | Backend |
| **5** | Compliance & security | 20-28 hrs | Security + Compliance |
| **6** | Documentation & deployment | 26-34 hrs | Ops + Training |
| **TOTAL** | **Complete system** | **238-304 hours** | **Full team** |

---

## Team Requirements

**Estimated headcount (concurrent work):**
- 2-3 Backend engineers (40+ hours/week)
- 2 Frontend engineers (40+ hours/week)
- 1 QA engineer (40+ hours/week)
- 1 DevOps/Ops engineer (20 hours/week, ramp to 40)
- 1 Security engineer (20 hours/week for Phase 5)
- 1 Compliance/Legal (10 hours/week, critical path items)

**Timeline with full team:** 6-8 weeks

---

## The Covenant

At the end, you will have built:

✅ A system that **refuses to hide**  
✅ A system that **shows its work**  
✅ A system that **proves reliability through transparency**  
✅ A system that **metabolizes evidence** (learns from experience)  
✅ A system that **adapts without losing history** (dynamic sources, immutable audit trail)  
✅ A system that **serves the mother trying to get healthcare for her kids**, not bureaucratic convenience  

---

**This is the system evolution would build.**

**This is the system we build.**

**No compromises.**

**We do it all.**
