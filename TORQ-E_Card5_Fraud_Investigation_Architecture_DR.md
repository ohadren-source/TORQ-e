# TORQ-E Card 5 (UBADA) - Fraud Investigation Architecture
## Design Reference (DR)

**Card Name**: UBADA (Ultimate Behavioral Anomaly Detection & Analysis)  
**Card Purpose**: Data Analyst & Fraud Investigation  
**Status**: Backend Ready, Frontend in Development  
**Audience**: Fraud investigators, compliance officers, CMS liaisons  
**Data Scope**: Cross-system fraud signals, claim patterns, network analysis  

---

## 1. Executive Summary

Card 5 provides forensic-grade fraud detection and investigation tools for Medicaid governance. It extends Card 4's aggregate signal detection into deep-dive investigation workflows, offering evidence chains, network visualization, and regulatory handoff integration.

**Key differentiator**: Card 5 is *reactive* (investigates known signals) while Card 4 is *proactive* (detects signals). Together they form a closed-loop fraud prevention system.

### Signal Flow
```
Card 4 (Detection) 
  ↓ [Fraud signal + confidence score]
  ↓
Card 5 (Investigation)
  ├─→ Create Investigation Case
  ├─→ Collect Evidence
  ├─→ Visualize Networks
  ├─→ Generate Regulatory Report
  └─→ Handoff to State/CMS
```

---

## 2. Data Models

### 2.1 DetailedFraudSignal
Initiated by Card 4's fraud detection, enriched during Card 5 investigation.

```python
class DetailedFraudSignal:
    signal_id: str                          # UUID from Card 4
    signal_type: "provider" | "member" | "claim_pattern" | "network"
    fraud_type: "billing_fraud" | "identity_fraud" | "upcoding" | "phantom_billing" | "kickback_scheme"
    fraud_confidence_score: float           # 0.0-1.0 (from Card 4 statistical model)
    
    # Entity identification
    flagged_entity_id: str                  # Provider NPI or Member ID
    flagged_entity_name: str
    flagged_entity_type: "provider" | "member"
    
    # Statistical basis
    statistical_basis: {
        anomaly_type: str                   # "outlier", "pattern_match", "network_anomaly"
        baseline_mean: float
        anomaly_value: float
        sigma_deviation: float              # How many std devs away
        p_value: float                      # Statistical significance
        percentile_rank: float              # Percentile vs cohort
    }
    
    # Evidence chain (immutable, append-only)
    evidence_chain: List[{
        evidence_id: str
        evidence_type: "claim" | "pattern" | "network" | "timing" | "behavioral"
        description: str
        weight: float                       # 0.0-1.0 (importance in case)
        verified: bool
        added_by: str                       # User/system that added
        added_timestamp: datetime
        supporting_data: Dict               # Raw evidence JSON
    }]
    
    # Pattern analysis
    patterns: {
        temporal: {
            claim_submission_timing: str    # "clustered", "uniform", "suspicious"
            processing_speed: str           # "faster_than_normal", "normal", "delayed"
            seasonal_pattern: bool
        }
        financial: {
            high_value_claims_percentage: float
            denied_claims_percentage: float
            average_claim_value: float
            total_suspicious_amount: float
        }
        behavioral: {
            claim_type_diversity: str       # "narrow", "diverse"
            provider_network_size: int
            cross_state_activity: bool
        }
    }
    
    # Network relationships
    network_graph: {
        nodes: List[{
            node_id: str
            node_type: "provider" | "member" | "billing_agent" | "location"
            node_label: str
            risk_score: float
            connected_signals: int
        }]
        edges: List[{
            source: str
            target: str
            relationship_type: "bills_to" | "referred_to" | "located_at" | "shares_address"
            strength: float                 # Connection strength 0.0-1.0
            suspicious: bool
        }]
        total_nodes: int
        total_edges: int
        clustering_coefficient: float      # Network density indicator
    }
    
    # Regulatory implications
    regulatory_impact: {
        cms_cms_relevant: bool
        state_agency_relevant: str          # "NY DOH", "NY DHHS", etc
        federal_violation_likelihood: str   # "low", "medium", "high", "critical"
        recovery_potential_usd: float
        regulatory_timeline: str            # "immediate", "90_days", "standard"
    }
    
    # Investigation tracking
    investigation_status: "open" | "under_investigation" | "closed" | "escalated"
    case_id: str                            # FK to FraudCase (null until case created)
    flagged_timestamp: datetime
    last_updated: datetime
    created_by: str                         # Card 4 system or user
    
    # Immutability marker
    is_immutable: bool = True
    audit_trail: List[str]                  # Pointers to audit log entries
```

### 2.2 FraudCase
Investigation case tracking and management.

```python
class FraudCase:
    case_id: str                            # UUID
    case_name: str                          # Human-readable: "Provider ABC Investigation"
    case_status: "open" | "under_investigation" | "closed" | "escalated_to_cms" | "escalated_to_state"
    case_severity: "low" | "medium" | "high" | "critical"
    
    # Case scope
    primary_signal_id: str                  # Link to initiating signal
    related_signal_ids: List[str]           # Other correlated signals
    case_type: "single_provider" | "network_fraud" | "member_ring" | "system_pattern"
    
    # Investigation team
    assigned_investigator: str              # User ID
    assigned_timestamp: datetime
    co_investigators: List[str]
    
    # Timeline
    case_opened: datetime
    case_closed: datetime (nullable)
    escalation_timestamp: datetime (nullable)
    
    # Evidence accumulation
    total_evidence_items: int
    total_suspicious_amount_usd: float
    affected_members: int
    affected_providers: int
    affected_claims: int
    
    # Investigation findings
    investigator_notes: str                 # Findings summary
    conclusion: str                         # Final determination
    findings_confidence: float              # 0.0-1.0 (investigator's confidence)
    
    # Regulatory handoff
    cms_referred: bool
    cms_referral_date: datetime (nullable)
    cms_referral_case_id: str (nullable)
    state_referred: bool
    state_referred_to: str (nullable)       # "NY DOH", "NY DHHS"
    state_referral_date: datetime (nullable)
    state_referral_case_id: str (nullable)
    
    # Financial impact
    identified_overpayments_usd: float
    recommended_recovery_usd: float
    actual_recovery_usd: float (nullable)
    recovery_status: "pending" | "partial" | "complete" | "abandoned"
    
    # Immutability
    is_immutable_after_close: bool = True
    audit_trail: List[str]                  # Pointers to audit log entries
```

---

## 3. Investigation Workflow

### Step 1: Signal Receipt & Triage
- Card 4 detects anomaly → FraudSignal created
- System automatically classifies fraud_type and regulatory_impact
- Confidence score determines automatic escalation rules:
  - **score ≥ 0.85**: Auto-escalate to investigator
  - **score 0.70-0.85**: Flag for review, wait for investigator assignment
  - **score < 0.70**: Archive as low-priority signal

### Step 2: Case Creation & Assignment
- Investigator reviews signal + supporting evidence
- Creates FraudCase with case_type and case_severity
- Assembles investigation team
- Defines scope: which related signals are included

### Step 3: Evidence Collection & Chain Building
- Investigator queries claims, member records, provider records
- All evidence immutably added to case's evidence_chain
- Network analysis identifies connected providers/members
- Behavioral patterns extracted (temporal, financial, network)

### Step 4: Network Visualization & Pattern Analysis
- Card 5 generates network graph showing:
  - Direct relationships (provider→member, provider→provider)
  - Indirect relationships (shared billing agents, locations)
  - Risk scoring on each node
  - Clustering coefficients to identify ring structures
- Timeline visualization shows:
  - Claim submission patterns
  - Processing anomalies
  - Temporal correlations with other cases

### Step 5: Regulatory Handoff
- Case summary + evidence package generated
- Automatic report formatting for CMS or state agencies
- Regulatory_impact fields map to jurisdiction-specific requirements
- Case status changes to escalated_to_cms or escalated_to_state
- Immutable audit trail created for compliance

---

## 4. API Endpoints

All endpoints require authentication (investigator role) and are HIPAA-compliant.

### 4.1 POST `/api/card5/analyze-claim`
**Purpose**: Initiate fraud analysis on a single claim

**Request**:
```json
{
  "claim_id": "CLM-2026-00123456",
  "provider_npi": "1234567890",
  "member_id": "MBR-2026-001",
  "analysis_depth": "quick" | "thorough",
  "compare_to_cohort": true
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "analysis_id": "ANLYS-2026-00001",
  "claim_id": "CLM-2026-00123456",
  "fraud_signal_detected": true,
  "fraud_type": "upcoding",
  "fraud_confidence_score": 0.87,
  "statistical_basis": {
    "anomaly_type": "pattern_match",
    "baseline_mean": 150.0,
    "anomaly_value": 425.0,
    "sigma_deviation": 3.2,
    "p_value": 0.001,
    "percentile_rank": 98
  },
  "patterns_found": {
    "temporal": "clustered",
    "financial": {
      "claim_value_vs_cohort_percentile": 95,
      "code_frequency_anomaly": true
    }
  },
  "recommendation": "Create investigation case",
  "analysis_timestamp": "2026-04-25T14:32:00Z"
}
```

### 4.2 POST `/api/card5/create-case`
**Purpose**: Create fraud investigation case from signal(s)

**Request**:
```json
{
  "case_name": "Provider ABC - Upcoding Investigation",
  "case_type": "single_provider",
  "case_severity": "high",
  "primary_signal_id": "SIG-2026-00456",
  "related_signal_ids": ["SIG-2026-00457", "SIG-2026-00458"],
  "assigned_investigator": "investigator_user_123",
  "co_investigators": ["investigator_user_456"]
}
```

**Response** (201 Created):
```json
{
  "status": "success",
  "case_id": "CASE-2026-00789",
  "case_name": "Provider ABC - Upcoding Investigation",
  "case_status": "open",
  "case_severity": "high",
  "assigned_investigator": "investigator_user_123",
  "case_opened": "2026-04-25T14:35:00Z",
  "primary_signal_id": "SIG-2026-00456",
  "related_signals_count": 2
}
```

### 4.3 GET `/api/card5/get-case/{case_id}`
**Purpose**: Retrieve complete case details with evidence chain

**Response** (200 OK):
```json
{
  "status": "success",
  "case": {
    "case_id": "CASE-2026-00789",
    "case_name": "Provider ABC - Upcoding Investigation",
    "case_status": "under_investigation",
    "case_severity": "high",
    "assigned_investigator": "investigator_user_123",
    "case_opened": "2026-04-25T14:35:00Z",
    "last_updated": "2026-04-25T15:10:00Z",
    "total_evidence_items": 23,
    "total_suspicious_amount_usd": 47500.00,
    "affected_members": 12,
    "affected_claims": 18,
    "evidence_chain": [
      {
        "evidence_id": "EV-001",
        "evidence_type": "claim",
        "description": "Claim CLM-00123456 - CPT code 99215 submitted 8x/day (vs cohort avg 2.3x/day)",
        "weight": 0.95,
        "verified": true,
        "added_by": "investigator_user_123",
        "added_timestamp": "2026-04-25T14:45:00Z",
        "supporting_data": {
          "claim_id": "CLM-2026-00123456",
          "cpt_code": "99215",
          "frequency": 8,
          "cohort_average": 2.3
        }
      }
    ],
    "network_graph": {
      "total_nodes": 5,
      "total_edges": 8,
      "clustering_coefficient": 0.67,
      "nodes": [
        {
          "node_id": "PROV-ABC",
          "node_type": "provider",
          "node_label": "Provider ABC",
          "risk_score": 0.91,
          "connected_signals": 3
        }
      ]
    },
    "investigator_notes": "Pattern suggests systematic upcoding scheme. Strong correlation with 12 members.",
    "cms_referred": false,
    "identified_overpayments_usd": 47500.00,
    "recovery_status": "pending"
  }
}
```

### 4.4 POST `/api/card5/add-evidence`
**Purpose**: Add evidence to case (immutable append)

**Request**:
```json
{
  "case_id": "CASE-2026-00789",
  "evidence_type": "network",
  "description": "Identified shared billing agent across 3 providers in ring structure",
  "weight": 0.88,
  "verified": true,
  "supporting_data": {
    "billing_agent": "BA-12345",
    "providers": ["PROV-ABC", "PROV-DEF", "PROV-GHI"],
    "relationship_type": "shares_billing_agent"
  }
}
```

**Response** (201 Created):
```json
{
  "status": "success",
  "evidence_id": "EV-024",
  "case_id": "CASE-2026-00789",
  "added_timestamp": "2026-04-25T15:30:00Z",
  "evidence_chain_length": 24,
  "audit_log_entry": "AUDIT-2026-001024"
}
```

### 4.5 GET `/api/card5/network-graph/{case_id}`
**Purpose**: Retrieve detailed network visualization data

**Response** (200 OK):
```json
{
  "status": "success",
  "case_id": "CASE-2026-00789",
  "network_visualization": {
    "nodes": [
      {
        "node_id": "PROV-ABC",
        "node_type": "provider",
        "node_label": "Provider ABC",
        "risk_score": 0.91,
        "connected_signals": 3,
        "npi": "1234567890",
        "location": "Albany, NY"
      },
      {
        "node_id": "BA-12345",
        "node_type": "billing_agent",
        "node_label": "Billing Agent 12345",
        "risk_score": 0.78,
        "connected_signals": 5,
        "agency": "BillingCorp LLC"
      }
    ],
    "edges": [
      {
        "source": "PROV-ABC",
        "target": "BA-12345",
        "relationship_type": "shares_billing_agent",
        "strength": 0.95,
        "suspicious": true,
        "claim_count": 45
      }
    ],
    "clustering_analysis": {
      "clusters_detected": 2,
      "largest_cluster_size": 8,
      "ring_structure_detected": true,
      "ring_members": ["PROV-ABC", "PROV-DEF", "PROV-GHI"]
    }
  }
}
```

### 4.6 POST `/api/card5/close-case`
**Purpose**: Close investigation case with findings

**Request**:
```json
{
  "case_id": "CASE-2026-00789",
  "conclusion": "Systematic upcoding scheme confirmed. Provider ABC and associates submitted 23 fraudulent claims totaling $47,500. Recommend referral to NY DOH and CMS for recovery.",
  "findings_confidence": 0.94,
  "escalate_to_cms": true,
  "escalate_to_state": "NY DOH",
  "recommended_recovery_usd": 47500.00
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "case_id": "CASE-2026-00789",
  "case_status": "escalated_to_cms",
  "case_closed": "2026-04-25T16:00:00Z",
  "cms_referral_case_id": "CMS-2026-45678",
  "state_referral_case_id": "NYDOH-2026-23456",
  "recommended_recovery_usd": 47500.00,
  "audit_trail_entries_created": 5,
  "note": "Case immutably closed. All evidence chain frozen for regulatory compliance."
}
```

### 4.7 GET `/api/card5/dashboard`
**Purpose**: Fraud investigator dashboard (aggregate view)

**Response** (200 OK):
```json
{
  "status": "success",
  "dashboard": {
    "cases_summary": {
      "total_open_cases": 12,
      "total_under_investigation": 8,
      "total_escalated_this_month": 3,
      "avg_case_duration_days": 14.5
    },
    "financial_impact": {
      "identified_overpayments_this_month_usd": 187500,
      "recommended_recovery_usd": 175000,
      "actual_recovery_usd": 125000,
      "recovery_rate_percent": 71.4
    },
    "signal_trends": {
      "new_signals_this_week": 28,
      "signals_by_type": {
        "billing_fraud": 12,
        "upcoding": 8,
        "phantom_billing": 5,
        "identity_fraud": 3
      }
    },
    "team_metrics": {
      "total_investigators": 5,
      "avg_caseload_per_investigator": 2.4,
      "avg_signals_resolved_per_investigator_week": 5.6
    },
    "regulatory_status": {
      "cases_pending_cms_response": 2,
      "cases_pending_state_response": 1,
      "escalations_this_quarter": 7
    }
  }
}
```

### 4.8 GET `/api/card5/health`
**Purpose**: Card 5 health check

**Response** (200 OK):
```json
{
  "status": "healthy",
  "card": "5 (UBADA)",
  "tools": 7,
  "tools_available": [
    "analyze-claim",
    "create-case",
    "get-case",
    "add-evidence",
    "network-graph",
    "close-case",
    "dashboard"
  ],
  "database_status": "connected",
  "immutability_enforcement": "active",
  "audit_trail_status": "logging"
}
```

---

## 5. Visualization Components

### 5.1 Fraud Dashboard (HTML/Chart.js)
- Real-time fraud metrics (open cases, pending escalations, recovery status)
- Signal trend chart (new signals/week by fraud type)
- Case severity distribution (pie chart: low/medium/high/critical)
- Team performance metrics (cases per investigator, resolution rate)
- Financial impact tracker (identified vs recovered amounts)

### 5.2 Network Visualizer (D3.js / Three.js)
- Interactive network graph showing:
  - Nodes: Providers, members, billing agents, locations
  - Edges: Relationships with risk indicators
  - Risk scoring via node color (green=low, yellow=medium, red=high)
  - Clustering visualization highlighting ring structures
- Hover tooltips showing connected signals
- Zoom/pan controls for large networks
- Filtering by node type or relationship strength

### 5.3 Timeline Builder (React/Recharts)
- Chronological view of:
  - Claim submission patterns
  - Case milestones (opened, evidence added, escalated, closed)
  - Regulatory interactions (CMS/state referrals)
- Interactive scrubber for temporal analysis
- Pattern annotations (clusters, anomalies)
- Export to PDF for regulatory submission

---

## 6. Testing Protocol

### Test Query 1: Single Claim Analysis
**Investigator Action**: "Analyze claim CLM-2026-00123456 for fraud"  
**Expected Response**:
- Detection of fraud signal with confidence score
- Statistical basis showing anomaly type and p-value
- Recommendation to create investigation case
- Related claims identified in network

**Success Criteria**:
- ✅ Fraud signal detected (confidence score > 0.70)
- ✅ Statistical basis accurately calculated
- ✅ Related claims identified
- ✅ Response time < 2 seconds

### Test Query 2: Case Creation & Evidence Chain
**Investigator Action**: Create case from detected signal, add 3+ evidence items  
**Expected Response**:
- Case created with case_id
- Evidence items immutably appended
- Audit trail entries created for each action
- Network graph built from related signals

**Success Criteria**:
- ✅ Case created with correct status (open)
- ✅ All evidence items stored with timestamps
- ✅ Audit trail entries present for each addition
- ✅ Network graph shows connected entities

### Test Query 3: Network Analysis
**Investigator Action**: "Show me the network around Provider ABC"  
**Expected Response**:
- Network graph with 5+ nodes
- Clustering coefficient calculated
- Ring structure detection (if applicable)
- Risk scores for each node

**Success Criteria**:
- ✅ Network nodes and edges correctly identified
- ✅ Clustering coefficient < 0.85 (for ring structures)
- ✅ Risk scores distributed (not all same)
- ✅ Relationship types accurately labeled

### Test Query 4: Case Escalation
**Investigator Action**: Close case with escalation to CMS and NY DOH  
**Expected Response**:
- Case status changed to "escalated_to_cms" and "escalated_to_state"
- Regulatory case IDs assigned
- Immutable case closure with evidence frozen
- Audit trail entries created

**Success Criteria**:
- ✅ Case status correctly updated
- ✅ Regulatory case IDs generated
- ✅ Case data immutable after closure
- ✅ Audit entries show escalation timestamp

### Test Query 5: Dashboard Metrics
**Investigator Action**: View fraud dashboard  
**Expected Response**:
- Total open cases: 12
- Financial impact: $187,500 identified this month
- Team metrics: 5 investigators, 2.4 avg caseload
- Signal trends by fraud type

**Success Criteria**:
- ✅ Dashboard loads in < 1 second
- ✅ All metrics accurate (cross-checked against database)
- ✅ No PII exposed in aggregate calculations
- ✅ Trend data matches date range

### Test Query 6: End-to-End Investigation
**Investigator Action**: Full workflow: Analyze claim → Create case → Add evidence → Build network → Escalate  
**Expected Response**:
- All steps complete with correct data flow
- No data loss or audit trail gaps
- Network visualization accurate
- Regulatory handoff package complete

**Success Criteria**:
- ✅ All 6 steps complete without errors
- ✅ Evidence chain fully immutable
- ✅ Network shows all connected entities
- ✅ CMS/state referral case IDs generated
- ✅ Total execution time < 10 seconds

---

## 7. Security & Compliance

### 7.1 Immutability Enforcement
- Evidence chain uses append-only database writes
- FraudCase.is_immutable_after_close = True prevents modification post-closure
- All evidence items timestamped and signed by user_id
- Database constraints enforce immutability at storage layer

### 7.2 Privacy Protection
- No PII exposed in network visualizations (nodes identified by ID, not names)
- Aggregate financial metrics only (no claim-level PII)
- Regulatory reports use anonymized identifiers
- Access control: Only assigned investigator + co-investigators can view case details

### 7.3 Audit Trail Integration
- Every action logged to immutable audit_log table:
  - Signal creation (by Card 4)
  - Case creation/updates (by investigator)
  - Evidence additions (immutable)
  - Escalations (with regulatory case IDs)
  - Case closures (with findings)
- Audit entries include: user_id, action_type, timestamp, justification, data_hash
- For regulatory compliance: Full audit trail exportable to CMS/state agencies

### 7.4 Regulatory Compliance
- Evidence package format compliant with CMS/state requirements
- Automatic report generation for federal/state handoff
- Case closure triggers immutable freeze + audit seal
- All findings documented with confidence scores and statistical basis

---

## 8. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Signal Detection Accuracy** | > 95% precision | Confirmed fraud / total signals |
| **Investigation Throughput** | 2.4 cases/investigator/week | Dashboard metric |
| **Case Resolution Time** | < 14 days avg | (case_closed - case_opened) |
| **Recovery Rate** | > 70% | actual_recovery_usd / recommended_recovery_usd |
| **False Positive Rate** | < 5% | Non-fraudulent cases / total escalations |
| **Audit Trail Completeness** | 100% | Evidence chain gaps = 0 |
| **Data Quality Score** | > 85% | Cross-validation with Card 4 metrics |
| **System Uptime** | > 99.9% | Availability for investigators |
| **Response Time (API)** | < 2s avg | p95 latency for analyze-claim |
| **Regulatory Handoff** | 100% compliant | CMS/state audit review |

---

## 9. Implementation Checklist

- [ ] DetailedFraudSignal model created in database
- [ ] FraudCase model created in database
- [ ] Immutability constraints enforced at DB layer
- [ ] API endpoints 1-8 implemented and tested
- [ ] Evidence chain append-only mechanism verified
- [ ] Network graph visualization built (D3.js)
- [ ] Timeline builder component created
- [ ] Dashboard metrics aggregation working
- [ ] Audit trail integration complete
- [ ] Regulatory report generation functional
- [ ] Access control enforced (investigator-only)
- [ ] Chat interface created for Card 5 (conversational fraud investigation)
- [ ] End-to-end testing protocol executed (Test Queries 1-6)
- [ ] Railway deployment configured
- [ ] Documentation complete (this DR + AN)

---

## 10. Next Steps

1. **Frontend Development**: Create chat-card5.html with conversational fraud investigation interface
2. **Backend Implementation**: Implement card_5_ubada/ routes and query_engine.py
3. **Database Setup**: Deploy FraudSignal and FraudCase tables to PostgreSQL
4. **Testing**: Execute 6 test queries with Selam (fraud investigator persona)
5. **Visualization**: Integrate D3/Three.js network and Recharts timeline
6. **Regulatory Validation**: CMS/state format review for evidence package and reports
7. **Deployment**: Push to Railway and verify end-to-end workflow
8. **Documentation Update**: Create AN (Architecture for Audience) version for non-technical stakeholders

---

## Document History

| Date | Status | Author | Changes |
|------|--------|--------|---------|
| 2026-04-25 | DRAFT | Claude | Initial comprehensive design document |
| TBD | REVIEW | Selam | QA feedback from testing protocol |
| TBD | FINAL | Ohad | Approved for implementation |
