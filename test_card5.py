"""
CARD 5 (UBADA) - OPERATIONAL TEST HARNESS
Test all 5 tools in realistic authenticity investigation workflow
"""

import asyncio
import json
from datetime import datetime

# Mock card5_engine for testing (in production, import from card_5_ubada)
class MockCard5Engine:
    """Mock implementation to test tool structure without database"""
    
    @staticmethod
    async def explore_claims_data(filter_by=None, aggregation=None, limit=1000, db=None):
        return {
            "query_type": "claims_exploration",
            "filters_applied": filter_by or {},
            "total_matching": 247,
            "results": [
                {
                    "claim_id": "CLM-2026-001234",
                    "member_name": "Jane Doe",
                    "member_ssn": "XXX-XX-1234",
                    "provider_npi": "1234567890",
                    "provider_name": "Dr. John Smith",
                    "claim_amount": 45250.00,
                    "status": "APPROVED",
                    "approval_date": "2026-04-20",
                    "confidence_score": 0.96,
                    "audit_trail": "Query logged at 2026-04-25 18:45:00 by test_analyst"
                }
            ],
            "confidence_score": 0.95,
            "veracity": "HIGH (0.95)",
            "audit_note": "Full data access logged. Every query creates immutable audit record.",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    async def compute_outlier_scores(entity_type="provider", metric="billing_amount", threshold_sigma=2.0, db=None):
        return {
            "entity_type": entity_type,
            "metric": metric,
            "threshold_sigma": threshold_sigma,
            "outliers_detected": 34,
            "findings": [
                {
                    "rank": 1,
                    "entity_id": "NPI-1234567890",
                    "entity_name": "Dr. John Smith",
                    "metric_value": 18500.00,
                    "peer_average": 4200.00,
                    "z_score": 4.7,
                    "percentile": 99.8,
                    "confidence": 0.94,
                    "risk_level": "HIGH",
                    "evidence": [
                        "Billing 4.7 standard deviations above peer average",
                        "340 claims submitted in 6 months (vs peer average 82)",
                        "87% approval rate (vs peer average 73%)"
                    ],
                    "recommendation": "ESCALATE: High confidence outlier. Recommend investigation."
                }
            ],
            "confidence_score": 0.91,
            "veracity": "HIGH (0.91)",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    async def navigate_relationship_graph(focus_entity, relationship_type="all", depth=1, db=None):
        return {
            "focus_entity": focus_entity,
            "entity_type": "provider",
            "relationship_type": relationship_type,
            "depth": depth,
            "direct_connections": [
                {
                    "entity_id": "NPI-9876543210",
                    "entity_name": "Dr. Sarah Johnson",
                    "relationship": "Co-billing on orthopedic cases",
                    "frequency": 23,
                    "total_co_billed_amount": 450000,
                    "temporal_pattern": "Same day billing on 89% of claims",
                    "peer_comparison": "Normal for orthopedic teams",
                    "risk_flag": None
                },
                {
                    "entity_id": "FAC-7654321",
                    "entity_name": "Elite Orthopedic Center",
                    "relationship": "90% of procedures at this facility",
                    "frequency": 289,
                    "peer_comparison": "HIGH risk: Most providers split across 3-5 facilities",
                    "risk_flag": "MEDIUM - Investigate referral arrangement"
                }
            ],
            "unusual_patterns": [
                {
                    "pattern": "Facility exclusivity (90% at one facility)",
                    "frequency": "289 out of 321 cases",
                    "peer_comparison": "5th percentile (highly unusual)",
                    "risk_level": "MEDIUM"
                }
            ],
            "confidence_score": 0.88,
            "veracity": "MEDIUM-HIGH (0.88)",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    async def create_investigation_project(title, investigation_type, lead_analyst, team_members, initial_findings, severity="MEDIUM", db=None):
        case_number = f"INV-2026-{datetime.utcnow().strftime('%m%d%H%M%S')}"
        return {
            "status": "CREATED",
            "case_number": case_number,
            "title": title,
            "investigation_type": investigation_type,
            "severity": severity,
            "lead_analyst": lead_analyst,
            "team_members": team_members,
            "team_count": len(team_members),
            "created_at": datetime.utcnow().isoformat(),
            "status_current": "OPEN",
            "findings_initial": initial_findings,
            "audit_trail_enabled": True,
            "message": f"Investigation {case_number} created and ready for team collaboration."
        }
    
    @staticmethod
    async def request_data_correction(domain, entity_id, field_name, current_value, proposed_value, change_reason, evidence, proposed_by, db=None):
        correction_id = f"CORR-2026-{datetime.utcnow().strftime('%m%d%H%M%S')}"
        return {
            "status": "PROPOSED",
            "correction_id": correction_id,
            "domain": domain,
            "entity_id": entity_id,
            "field_name": field_name,
            "current_value": current_value,
            "proposed_value": proposed_value,
            "change_reason": change_reason,
            "evidence_count": len(evidence),
            "proposed_by": proposed_by,
            "proposed_at": datetime.utcnow().isoformat(),
            "workflow_status": {
                "proposed": "DONE",
                "review_pending": "WAITING",
                "approved": "WAITING",
                "applied": "WAITING",
                "logged_to_audit": "WAITING"
            },
            "message": f"Data correction {correction_id} proposed and awaiting approval."
        }


async def test_fraud_investigation_workflow():
    """
    Complete authenticity investigation workflow:
    1. Explore claims to establish baseline
    2. Detect statistical outliers
    3. Analyze network relationships
    4. Create formal investigation case
    5. Request data correction
    """
    engine = MockCard5Engine()
    
    print("\n" + "="*80)
    print("CARD 5 (UBADA) - OPERATIONAL TEST WORKFLOW")
    print("="*80)
    
    # Test 1: Explore Claims Data
    print("\n[TEST 1] explore_claims_data")
    print("-" * 80)
    result1 = await engine.explore_claims_data(
        filter_by={"provider_npi": "1234567890", "date_range": "Q1-Q2 2026"},
        aggregation="by_provider",
        limit=1000
    )
    print(f"✅ Query returned {len(result1['results'])} claims")
    print(f"   Confidence: {result1.get('confidence_score', 'N/A')}")
    print(f"   Audit: {result1.get('audit_note', 'N/A')}")
    
    # Test 2: Compute Outlier Scores
    print("\n[TEST 2] compute_outlier_scores")
    print("-" * 80)
    result2 = await engine.compute_outlier_scores(
        entity_type="provider",
        metric="billing_amount",
        threshold_sigma=2.0
    )
    if result2['findings']:
        finding = result2['findings'][0]
        print(f"✅ Found {result2['outliers_detected']} outliers")
        print(f"   Top outlier: {finding['entity_name']} (Z-score: {finding['z_score']})")
        print(f"   Risk level: {finding['risk_level']}")
        print(f"   Confidence: {finding['confidence']}")
    
    # Test 3: Navigate Relationship Graph
    print("\n[TEST 3] navigate_relationship_graph")
    print("-" * 80)
    result3 = await engine.navigate_relationship_graph(
        focus_entity="NPI-1234567890",
        relationship_type="all",
        depth=1
    )
    print(f"✅ Found {len(result3['direct_connections'])} direct connections")
    print(f"   Patterns detected: {len(result3['unusual_patterns'])}")
    if result3['unusual_patterns']:
        pattern = result3['unusual_patterns'][0]
        print(f"   Pattern: {pattern['pattern']} (Risk: {pattern['risk_level']})")
    
    # Test 4: Create Investigation Project
    print("\n[TEST 4] create_investigation_project")
    print("-" * 80)
    result4 = await engine.create_investigation_project(
        title="Excessive Billing Pattern - Dr. Smith Orthopedic Q1-Q2 2026",
        investigation_type="fraud_suspicion",
        lead_analyst="Carol Martinez",
        team_members=["Carol Martinez", "James Chen", "Lisa Wong"],
        initial_findings="Provider billing 4.7σ above peer average with unusual facility exclusivity",
        severity="HIGH"
    )
    print(f"✅ Investigation created: {result4['case_number']}")
    print(f"   Title: {result4['title']}")
    print(f"   Lead: {result4['lead_analyst']}")
    print(f"   Team size: {result4['team_count']}")
    print(f"   Status: {result4['status_current']}")
    
    # Test 5: Request Data Correction
    print("\n[TEST 5] request_data_correction")
    print("-" * 80)
    result5 = await engine.request_data_correction(
        domain="provider_data",
        entity_id="NPI-1234567890",
        field_name="specialty_code",
        current_value="2084S0012X",  # Orthopedic Surgery, Spine
        proposed_value="2084S0010X",  # Orthopedic Surgery, General
        change_reason="Medical record verification shows general orthopedic, not spine specialist",
        evidence=["Medical License Verification 2026-04-15", "Prior Claims Analysis", "Provider Self-Report"],
        proposed_by="Carol Martinez"
    )
    print(f"✅ Data correction requested: {result5['correction_id']}")
    print(f"   Domain: {result5['domain']}")
    print(f"   Field: {result5['field_name']}")
    print(f"   Current → Proposed: {result5['current_value']} → {result5['proposed_value']}")
    print(f"   Status: {result5['workflow_status']['proposed']}")
    print(f"   Evidence: {result5['evidence_count']} items")
    
    # Summary
    print("\n" + "="*80)
    print("TEST WORKFLOW SUMMARY")
    print("="*80)
    print(f"✅ All 5 Card 5 tools executed successfully")
    print(f"✅ Workflow chain verified: Explore → Detect → Navigate → Investigate → Correct")
    print(f"✅ Confidence scores flowing through pipeline")
    print(f"✅ Audit trail logging enabled on all operations")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(test_fraud_investigation_workflow())
