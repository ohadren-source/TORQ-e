# TORQ-e Test Cases - Comprehensive Matrix

## Test Case Format

```
ID: [TEST-CATEGORY-###]
User Type: [umid | upid | uhwp | ushi | ubada]
User Journey: [specific flow]
Preconditions: [state before test starts]
Steps: [numbered sequence]
Expected Result: [what should happen]
Environment: [test | prod | both]
Priority: [P0 Critical | P1 High | P2 Medium | P3 Low]
```

---

## Category 1: Member (UMID) Tests

### UMID-001: New Member Tier 1 Enrollment (Digital ID - Valid)
**Priority**: P0 Critical

**Preconditions**: 
- Member has valid government-issued ID (driver's license)
- Member has not previously enrolled
- Test environment active

**Steps**:
1. User selects "Member" role on entry screen
2. System routes to UMID login card
3. User clicks "Don't have a UMID yet? Create One"
4. System presents Tier 1 vs Tier 2 selection
5. User selects "Tier 1: Digital Verification"
6. System presents government ID entry form
7. User enters: Driver's License, Number: DL-123456789, Name: John Doe, DOB: 01/15/1980
8. User clicks "Verify ID"
9. **Test mode**: System returns `verified: true, fingerprint_match: "drivers_license_john_doe_1980_01_15"`
10. System routes to 2FA enrollment
11. User downloads authenticator app, scans QR code
12. System verifies phone SMS code
13. System generates UMID and saves to UMID_RECORDS
14. System routes to member dashboard

**Expected Result**:
- UMID created and locked
- Entry in UMID_RECORDS with: umid (UUID), federal_id_hash, 2fa_enabled=true, verified_at=NOW()
- Entry in VERIFICATION_AUDIT_LOG: "tier_1_govt_id_check" = "passed"
- Member can log back in with UMID + 2FA
- Member dashboard accessible

**Data Validation**:
```sql
SELECT * FROM UMID_RECORDS WHERE federal_id_hash = SHA256('john_doe_19800115');
-- Should return: umid, verified_at IS NOT NULL, 2fa_enabled = true, is_active = true

SELECT * FROM VERIFICATION_AUDIT_LOG 
WHERE identifier_id = [umid] AND verification_step = 'tier_1_govt_id_check';
-- Should return: verification_result = 'passed', timestamp = recent
```

---

### UMID-002: Existing Member via MPI Migration
**Priority**: P0 Critical

**Preconditions**:
- Member has active Medicaid ID in existing MPI (e.g., MPI ID: LEGACY-00001)
- Member is logging in for first time via TORQ-e
- Member's MPI record has: name, DOB, household size, income

**Steps**:
1. User enters UMID login screen
2. System detects user doesn't have UMID but has MPI ID
3. System routes to: "Do you have an existing Medicaid ID?"
4. User enters MPI ID: LEGACY-00001
5. System looks up MPI record in database
6. System retrieves: name, DOB, household info
7. System displays: "Is this you? [Name] DOB [DOB]?"
8. User confirms: "Are you sure? This will be your permanent UMID."
9. System creates UMID from LEGACY-00001 (or generates new with mapping)
10. System creates entry in IDENTIFIER_MAPPINGS
11. System routes to 2FA enrollment
12. User completes 2FA
13. System locks UMID selection (preferred_umid_locked=true)

**Expected Result**:
- New UMID created (UUID or mapped from MPI)
- IDENTIFIER_MAPPINGS entry: legacy_id_type='mpi_id', legacy_id_value='LEGACY-00001', is_primary=true
- preferred_umid_locked=true with timestamp
- Member can log in with either UMID or (optionally) original MPI ID
- All historical data (eligibility, coverage, claims) attached to UMID
- Zero data loss or migration errors

**Data Validation**:
```sql
SELECT * FROM IDENTIFIER_MAPPINGS 
WHERE legacy_id_type = 'mpi_id' AND universal_id_type = 'umid';
-- Should return mapping with is_primary=true

SELECT * FROM UMID_RECORDS 
WHERE preferred_umid_locked = true AND preferred_umid_locked_at IS NOT NULL;
-- Should verify timestamp is reasonable
```

---

### UMID-003: Member Checks Eligibility (Eligible Case)
**Priority**: P0 Critical

**Preconditions**:
- Member UMID exists and is verified
- Member household: 3 people
- Member monthly income: $2,100
- Member citizenship: US Citizen
- Member state: NY

**Steps**:
1. Authenticated member logs in
2. Member navigates to "Am I eligible for Medicaid?"
3. System retrieves UMID_RECORDS: household_size=3, monthly_income_cents=210000
4. System runs NYS Medicaid MAGI eligibility algorithm
5. Algorithm checks: household_size=3 → MAGI limit ~$2,500/month
6. Algorithm result: $2,100 < $2,500 → ELIGIBLE
7. System determines category: no age constraints, not pregnant, not disabled → MAGI Non-Pregnant Adult
8. System calculates benefits_effective_date=TODAY, renewal_date=TODAY + 1 year
9. System returns eligibility response

**Expected Result**:
```json
{
  "eligible": true,
  "eligibility_category": "MAGI_Non_Pregnant_Adult",
  "benefits_effective_date": "2026-04-23",
  "renewal_date": "2027-04-23",
  "_test_mode": true,
  "_mock_reason": "Test environment - using mock eligibility algorithm"
}
```

- No database write (query only)
- Audit log: Member accessed eligibility information
- No errors

---

### UMID-004: Member Checks Eligibility (Ineligible Case)
**Priority**: P1 High

**Preconditions**:
- Member household: 2 people
- Member monthly income: $5,200
- MAGI limit for household of 2: ~$2,100/month

**Steps**:
1. Member clicks "Check Eligibility"
2. System runs eligibility algorithm
3. Algorithm: $5,200 > $2,100 → INELIGIBLE

**Expected Result**:
```json
{
  "eligible": false,
  "reason": "Income exceeds limit for household size 2",
  "your_income": "$5,200/month",
  "limit": "$2,100/month",
  "next_steps": [
    "Reapply when income drops below limit",
    "Check if you qualify for other programs (e.g., emergency assistance)",
    "Appeal if income recently decreased"
  ],
  "_test_mode": true
}
```

---

### UMID-005: Member Views Coverage Details
**Priority**: P1 High

**Preconditions**:
- Member is eligible and enrolled in plan
- Plan: Fidelis Care HMO
- Plan has published copay structure

**Steps**:
1. Member clicks "What's Covered?"
2. System retrieves: UMID → plan assignment (WHUP)
3. System retrieves: WHUP record → coverage details
4. System formats copay schedule

**Expected Result**:
```json
{
  "plan_name": "Fidelis Care HMO",
  "member_id": "FIDELIS-ABC123456",
  "coverage": [
    { "service": "Primary Care Visit", "copay": "$15", "status": "covered" },
    { "service": "Emergency Room", "copay": "$250", "status": "covered", "note": "waived if admitted" },
    { "service": "Specialist Visit", "copay": "$25", "status": "covered", "note": "requires referral" },
    { "service": "Hospital Stay", "copay": "$0", "status": "covered" },
    { "service": "Preventive Care", "copay": "$0", "status": "covered" }
  ],
  "deductible": "$0",
  "out_of_pocket_max": "$5,000/year"
}
```

---

### UMID-006: Member Requests Renewal
**Priority**: P1 High

**Preconditions**:
- Member eligibility renewal date: 30 days away
- Renewal notice already sent

**Steps**:
1. Member clicks "Renew Eligibility"
2. System checks renewal_date from UMID_RECORDS
3. System displays renewal requirement summary
4. System offers: Online renewal (nystateofhealth.ny.gov) OR phone OR mail

**Expected Result**:
```json
{
  "renewal_date": "2027-04-23",
  "days_until_renewal": 330,
  "renewal_notice_sent": true,
  "renewal_notice_date": "2027-03-24",
  "required_documents": ["income_verification", "employment_status", "household_composition"],
  "renewal_methods": {
    "online": "https://nystateofhealth.ny.gov (recommended)",
    "phone": "1-855-355-5777",
    "mail": "Complete form and return within 10 days"
  }
}
```

---

## Category 2: Provider (UPID) Tests

### UPID-001: New Individual Provider Tier 1A Enrollment (NPI Verification)
**Priority**: P0 Critical

**Preconditions**:
- Provider is licensed physician
- Provider has valid NPI: 1234567890
- Provider has no disciplinary actions
- Provider not on OIG exclusion list
- Test environment active

**Steps**:
1. Provider selects "Provider" role
2. System routes to UPID entry card
3. Provider clicks "Enroll as New Provider"
4. System presents Tier 1A vs 1B vs 2 selection
5. Provider selects "Tier 1A: Individual Licensed Provider (NPI)"
6. Provider enters: NPI=1234567890, Last Name=Smith, DOB=05/20/1965, License=NY123456
7. System routes to verification
8. **Test mode**: System queries mock CMS NPPES, state licensing, OIG exclusions
9. **Test mode**: All checks pass
10. System generates UPID
11. System routes to 2FA enrollment
12. Provider completes 2FA
13. System locks UPID selection

**Expected Result**:
- UPID created and stored in UPID_RECORDS
- All verification checks logged in VERIFICATION_AUDIT_LOG
- provider_type='individual', npi=1234567890, verified_at=NOW()
- OIG exclusion status checked and logged: "not_excluded"
- 2FA enrolled and locked
- Provider receives enrollment confirmation with UPID

**Data Validation**:
```sql
SELECT * FROM UPID_RECORDS WHERE npi = '1234567890';
-- Should return: verified_at IS NOT NULL, oig_exclusion_status='not_excluded'

SELECT COUNT(*) FROM VERIFICATION_AUDIT_LOG 
WHERE identifier_id = [upid] AND verification_step LIKE 'cms%' OR 'oig%' OR 'licensing%';
-- Should return >= 3 (at least 3 verification checks)
```

---

### UPID-002: New Organization Provider Tier 1B Enrollment (EIN Verification)
**Priority**: P0 Critical

**Preconditions**:
- Organization is healthcare clinic
- EIN: 12-3456789 (valid IRS record)
- Organization not delinquent
- Test environment

**Steps**:
1. Provider selects "Tier 1B: Organization/Facility (EIN)"
2. Provider enters: Legal Business Name="ABC Healthcare Clinic", EIN=12-3456789, Type=Clinic, Address="123 Main St, NY, NY"
3. System verifies EIN against IRS mock database
4. System verifies business registration in state system
5. **Test mode**: Verification passes
6. System prompts for "Authorized Representative" info
7. Provider enters: Name=Alice Johnson, Title=CEO, Email=alice@abc-clinic.com, Phone=555-1234
8. System routes to 2FA enrollment
9. Provider completes 2FA

**Expected Result**:
- UPID created: provider_type='organization'
- UPID_RECORDS: ein=12-3456789, legal_business_name_encrypted, authorized_rep info stored
- Both EIN and IRS verification logged as "passed"
- Authorized representative confirmed for future claims holds/escalations
- Provider enrolled in all available plan networks

---

### UPID-003: OIG Excluded Provider (Enrollment Denied)
**Priority**: P1 High

**Preconditions**:
- Provider NPI: 9876543210
- NPI is on OIG exclusion list
- Test environment

**Steps**:
1. Excluded provider attempts enrollment with NPI=9876543210
2. System queries OIG exclusion mock database
3. System finds: EXCLUDED (reason: "inauthenticity conviction")
4. System blocks enrollment

**Expected Result**:
```json
{
  "enrollment_status": "DENIED",
  "reason": "Provider is on OIG exclusion list",
  "details": {
    "exclusion_reason": "inauthenticity conviction",
    "exclusion_date": "2023-06-15",
    "status": "Active"
  },
  "next_steps": "Contact OIG if you believe this is an error. Exclusion must be lifted before enrollment."
}
```

- No UPID created
- VERIFICATION_AUDIT_LOG: verification_result='failed', verification_step='oig_exclusion_check'
- Audit trail of rejected enrollment attempt preserved

---

### UPID-004: Provider Submits Claim (Valid)
**Priority**: P0 Critical

**Preconditions**:
- Provider UPID verified and active
- Provider not on claims suspension
- Member UMID eligible on service date
- Claim format valid

**Steps**:
1. Provider logs into dashboard
2. Provider clicks "Submit Claim"
3. Provider enters:
   - Member Medicaid ID: FIDELIS-ABC123456
   - Service Date: 2026-04-20
   - Diagnosis: ICD-10 J45.9 (Asthma, unspecified)
   - Procedure: CPT 99213 (Office visit, established patient, low complexity)
   - Units: 1
   - Charge: $150.00
4. System validates:
   - Provider not OIG-excluded (UPID_RECORDS.oig_exclusion_status)
   - Member eligible on 2026-04-20 (UMID_RECORDS.verified_at <= service_date)
   - Procedure/diagnosis pair valid (no impossible combinations)
   - Charge amount reasonable
5. System generates claim ID: CLM-2026-04-23-00001234
6. **Test mode**: Returns acceptance

**Expected Result**:
```json
{
  "claim_id": "CLM-2026-04-23-00001234",
  "submission_status": "accepted",
  "submitted_date": "2026-04-23",
  "expected_processing_time_days": 15,
  "expected_payment_date": "2026-05-08",
  "_test_mode": true,
  "_mock_reason": "Test environment - no EMEDNY integration"
}
```

- Claim logged to VERIFICATION_AUDIT_LOG
- Provider can track status

---

### UPID-005: Provider Submits Claim (Denied - Provider OIG-Excluded)
**Priority**: P1 High

**Preconditions**:
- Provider is OIG-excluded
- All claim data valid

**Steps**:
1. Excluded provider submits claim
2. System checks: UPID_RECORDS.oig_exclusion_status = 'excluded'
3. System rejects claim immediately

**Expected Result**:
```json
{
  "claim_id": null,
  "submission_status": "DENIED",
  "reason": "Provider is on OIG exclusion list. No claims accepted.",
  "escalation": "Contact NYS Medicaid if you believe this is an error",
  "http_status": 403
}
```

---

### UPID-006: Provider Checks Claim Status
**Priority**: P1 High

**Preconditions**:
- Claim submitted in UPID-004
- Claim ID: CLM-2026-04-23-00001234

**Steps**:
1. Provider clicks "Check Claim Status"
2. Provider enters or selects Claim ID
3. System queries claim database

**Expected Result**:
```json
{
  "claim_id": "CLM-2026-04-23-00001234",
  "status": "approved",
  "submitted_date": "2026-04-23",
  "approved_date": "2026-05-08",
  "approved_amount": "$150.00",
  "expected_payment_date": "2026-05-15",
  "payment_method": "direct_deposit"
}
```

---

## Category 3: Plan Administrator (WHUP) Tests

### WHUP-001: Plan Admin Checks Provider Network Status
**Priority**: P1 High

**Preconditions**:
- Plan: Fidelis Care (uhwp: 44444444-4444-4444-4444-444444444444)
- Provider: Dr. Jane Smith (NPI: 1234567890) in network
- Provider credentials current

**Steps**:
1. Plan admin logs in
2. Plan admin searches for provider: "Dr. Jane Smith" or NPI: 1234567890
3. System queries IDENTIFIER_MAPPINGS for NPI → UPID
4. System retrieves UPID_RECORDS: verified status, OIG exclusion status
5. System returns provider network status

**Expected Result**:
```json
{
  "provider_status": "in_network",
  "provider_name": "Dr. Jane Smith",
  "specialty": "Pediatrics",
  "npi": "1234567890",
  "accepting_new_patients": true,
  "copay_in_network": 15,
  "requires_referral": false,
  "credentials_verified": true,
  "verification_date": "2026-01-15"
}
```

---

### WHUP-002: Plan Admin Checks Member Enrollment
**Priority**: P1 High

**Preconditions**:
- Plan has 245,000 enrolled members
- Current month: April 2026

**Steps**:
1. Plan admin navigates to enrollment dashboard
2. System aggregates member count by service county
3. System compares to prior month

**Expected Result**:
```json
{
  "total_enrolled": 245000,
  "as_of_date": "2026-04-23",
  "by_county": [
    { "county": "New York", "fips": "36061", "enrolled": 85000 },
    { "county": "Kings", "fips": "36047", "enrolled": 60000 },
    { "county": "Queens", "fips": "36081", "enrolled": 100000 }
  ],
  "prior_month_total": 239500,
  "month_over_month_change": "+2.3%"
}
```

---

### WHUP-003: Plan Admin Reviews Quality Metrics (HEDIS/CAHPS)
**Priority**: P1 High

**Preconditions**:
- Plan quality data available for 2025 measurement year
- HEDIS score: 78.5
- CAHPS score: 7.4

**Steps**:
1. Plan admin navigates to quality metrics
2. System retrieves WHUP_RECORDS: hedis_score_latest, cahps_score_latest
3. System compares to benchmarks

**Expected Result**:
```json
{
  "plan_name": "Fidelis Care HMO",
  "measurement_year": 2025,
  "hedis_score": 78.5,
  "hedis_national_benchmark": 77.2,
  "hedis_status": "above_benchmark",
  "cahps_score": 7.4,
  "cahps_national_benchmark": 7.3,
  "cahps_status": "above_benchmark",
  "top_performing_measures": ["Childhood Immunizations", "Preventive Care"],
  "improvement_opportunities": ["Diabetes Control", "Asthma Management"]
}
```

---

## Category 4: Government Stakeholder (USHI) Tests

### USHI-001: Stakeholder Checks Program Efficiency
**Priority**: P0 Critical

**Preconditions**:
- Stakeholder USHI verified and authenticated
- Authority level: Admin (full access)
- Data access scope: All NY counties, all programs

**Steps**:
1. Stakeholder logs in
2. Stakeholder navigates to "Program Efficiency"
3. Stakeholder selects year: 2026
4. System queries mock claims database
5. System aggregates spending by category
6. System calculates CPPM

**Expected Result**:
```json
{
  "reporting_period": "2026 YTD (April)",
  "total_spending": "$5,120,000,000",
  "total_members": 3200000,
  "cppm": 1334,
  "cppm_trend_vs_prior_year": "+2.8%",
  "spending_by_category": [
    { "category": "Hospital/ER", "amount": "$1,850,000,000", "percent": 36 },
    { "category": "Outpatient", "amount": "$1,230,000,000", "percent": 24 },
    { "category": "Pharmacy", "amount": "$840,000,000", "percent": 16 },
    { "category": "Long-term Care", "amount": "$720,000,000", "percent": 14 },
    { "category": "Behavioral Health", "amount": "$310,000,000", "percent": 6 },
    { "category": "Other", "amount": "$170,000,000", "percent": 4 }
  ],
  "areas_for_improvement": [
    "ED utilization (280/1000 vs target 200/1000)",
    "Pharmacy cost trend (+8% YoY)",
    "Hospital readmission rate (18% vs target 15%)"
  ]
}
```

---

### USHI-002: Stakeholder Compares States (Benchmarking)
**Priority**: P1 High

**Preconditions**:
- Stakeholder authority level: Admin
- Comparing: NY vs MA vs PA

**Steps**:
1. Stakeholder navigates to benchmarking tool
2. Stakeholder selects states to compare
3. System retrieves CPPM and quality metrics for each state

**Expected Result**:
```json
{
  "comparison_year": 2026,
  "states_compared": ["MA", "NY", "PA"],
  "cppm_comparison": [
    { "state": "Massachusetts", "cppm": 1298, "rank": 1, "difference_from_ny": "-36" },
    { "state": "New York", "cppm": 1334, "rank": 2, "difference_from_ny": "baseline" },
    { "state": "Pennsylvania", "cppm": 1456, "rank": 3, "difference_from_ny": "+122" }
  ],
  "quality_comparison": [
    { "state": "Massachusetts", "hedis": 76.0, "cahps": 7.6 },
    { "state": "New York", "hedis": 72.0, "cahps": 7.2 },
    { "state": "Pennsylvania", "hedis": 68.0, "cahps": 7.1 }
  ],
  "insights": [
    "NY has 2nd lowest CPPM (favorable)",
    "MA has higher quality metrics (opportunity for improvement)",
    "Cost-benefit analysis: MA costs slightly less, delivers better quality"
  ]
}
```

---

### USHI-003: Stakeholder Views inauthenticity Monitoring Dashboard
**Priority**: P1 High

**Preconditions**:
- Active authenticity verification running
- 47 new flags this month
- 23 active investigations

**Steps**:
1. Stakeholder navigates to inauthenticity monitoring
2. System displays flags from past 30 days
3. System shows high-risk providers

**Expected Result**:
```json
{
  "new_flags_this_month": 47,
  "new_flags_prior_month": 32,
  "flags_trend": "+47% month-over-month",
  "active_investigations": 23,
  "investigation_status_breakdown": {
    "initial_review": 8,
    "pending_documentation": 10,
    "escalated_for_investigation": 5
  },
  "top_fraud_risk_providers": [
    {
      "provider_name": "ABC Clinic",
      "npi": "1234567890",
      "risk_score": 85,
      "red_flags": 7,
      "top_red_flags": ["PO Box address", "Billing volume 2x typical", "Duplicate billing"],
      "estimated_inauthenticity": "$450,000"
    },
    {
      "provider_name": "XYZ Services",
      "npi": "9876543210",
      "risk_score": 78,
      "red_flags": 5,
      "estimated_inauthenticity": "$280,000"
    }
  ],
  "estimated_fraud_recovery_ytd": "$2,450,000"
}
```

---

### USHI-004: Stakeholder With Limited Authority (View-Only)
**Priority**: P1 High

**Preconditions**:
- Stakeholder authority level: View-Only (level 5)
- Stakeholder data access scope: NYC counties only

**Steps**:
1. View-Only stakeholder logs in
2. Stakeholder attempts to access program efficiency
3. System filters results to NYC counties only
4. Stakeholder attempts to export data
5. System denies (View-Only cannot export)

**Expected Result**:
- Stakeholder sees efficiency report but only for: New York, Kings, Queens, Bronx, Richmond counties
- Other NY counties hidden or blank
- Download button disabled
- Only view access (no modifications possible)
- Full audit trail: who accessed what, when

---

## Category 5: Data Analyst (UBADA) Tests

### UBADA-001: authenticity assessment (High-Risk Provider)
**Priority**: P0 Critical

**Preconditions**:
- Analyst UBADA verified
- Target provider: "ABC Clinic" NPI: 1234567890
- Provider should show high authenticity risk
- Test mode active

**Steps**:
1. Analyst logs into authenticity verification workspace
2. Analyst enters: Assessment type = "Provider", Target = "1234567890"
3. Analyst selects: Depth = "Detailed"
4. System queries mock data sources:
   - CMS NPPES: Provider active
   - State licensing: License active
   - OIG exclusions: Not excluded
   - Claims patterns: Suspicious activity detected
5. System calculates authenticity score
6. System identifies red flags
7. System returns assessment

**Expected Result**:
```json
{
  "assessment_id": "ASS-2026-04-23-00001",
  "assessment_type": "provider_inauthenticity",
  "provider_name": "ABC Healthcare Clinic",
  "npi": "1234567890",
  "tax_id": "12-3456789",
  "fraud_risk_score": 78,
  "risk_level": "HIGH RISK",
  "red_flags": [
    { "flag": "Address is PO Box", "weight": "high", "evidence": "Address listed as PO Box 123" },
    { "flag": "Billing volume 2x typical", "weight": "high", "evidence": "340 visits/month vs expected 170" },
    { "flag": "Duplicate billing", "weight": "medium", "evidence": "0.8% of claims appear duplicated" },
    { "flag": "Billing outside hours", "weight": "medium", "evidence": "Claims billed 2 AM by 24/7 office" },
    { "flag": "Sudden claims spike", "weight": "high", "evidence": "Claims increased 300% in 3 months" }
  ],
  "green_flags": [
    { "flag": "NPI valid and active", "evidence": "Verified with CMS NPPES" },
    { "flag": "Tax ID matches registration", "evidence": "EIN verified with IRS" }
  ],
  "recommendation": "FLAG_FOR_INVESTIGATION",
  "recommended_actions": [
    "Place immediate claims hold pending review",
    "Request detailed documentation for sample of claims",
    "Schedule on-site visit to verify physical location",
    "Interview random sample of reported patients",
    "Escalate to Medicaid Inspector General"
  ],
  "analyst_notes": "High-risk profile. Multiple corroborating indicators suggest possible inauthentic operation.",
  "_test_mode": true
}
```

---

### UBADA-002: Data Quality Assessment
**Priority**: P1 High

**Preconditions**:
- Dataset: claims_2026_april
- ~3.2M records
- Various data quality issues present (duplicates, missing values, etc.)

**Steps**:
1. Analyst selects "Data Quality Check"
2. Analyst selects dataset: claims_2026_april
3. System runs automated QA checks:
   - Completeness (missing values)
   - Accuracy (valid formats, ranges)
   - Consistency (no duplicates, logical ordering)
   - Outliers (unusual values)
4. System compiles results

**Expected Result**:
```json
{
  "dataset_name": "claims_2026_april",
  "total_records": 3200000,
  "report_date": "2026-04-23",
  
  "completeness_check": {
    "score": "98.5%",
    "findings": [
      { "field": "diagnosis_code", "missing_percent": 0.2, "status": "acceptable" },
      { "field": "service_date", "missing_percent": 0.0, "status": "perfect" },
      { "field": "provider_npi", "missing_percent": 0.1, "status": "acceptable" }
    ]
  },
  
  "accuracy_check": {
    "score": "99.2%",
    "findings": [
      { "field": "date_formats", "valid_percent": 99.8, "issue": "3 records with YYYY-DD-MM instead of YYYY-MM-DD" },
      { "field": "zip_codes", "valid_percent": 99.1, "issue": "1.2% invalid ZIP formats" },
      { "field": "procedure_codes", "valid_percent": 99.3, "issue": "0.7% invalid CPT codes" }
    ]
  },
  
  "consistency_check": {
    "score": "99.8%",
    "findings": [
      { "check": "duplicate_claims", "duplicates_found": 960, "percent": 0.03, "status": "acceptable" },
      { "check": "logical_dates", "violations": 15, "percent": 0.0005, "status": "excellent" }
    ]
  },
  
  "outliers_check": {
    "score": "98.7%",
    "findings": [
      { "field": "charge_amount", "outliers": 38400, "percent": 1.2, "issue": "High-value claims (>$50K) warrant review" },
      { "field": "units_of_service", "outliers": 12800, "percent": 0.4, "issue": "Unusually high unit counts (>100 units/claim)" }
    ]
  },
  
  "overall_data_quality_score": "94.3%",
  "recommendation": "READY_FOR_ANALYSIS",
  "notes": "Dataset is clean with minor quality issues. Safe to proceed with authenticity verification analysis. Flag the 38,400 outlier claims for individual review."
}
```

---

### UBADA-003: Create Investigation Case
**Priority**: P1 High

**Preconditions**:
- authenticity assessment completed (UBADA-001)
- Risk score: 78 (high)
- Analyst decision: Escalate to investigation

**Steps**:
1. Analyst reviews authenticity assessment
2. Analyst clicks "Create Investigation Case"
3. Analyst fills form:
   - Case type: "Provider inauthenticity"
   - Provider: ABC Healthcare Clinic (NPI: 1234567890)
   - Summary: "High-risk provider with PO Box address, billing volume 2x typical, duplicate billing patterns, sudden claims spike 300%"
   - Evidence: Link to authenticity assessment ID
4. System creates case and assigns to Medicaid Inspector General
5. System automatically places provider on claims hold

**Expected Result**:
```json
{
  "case_id": "INV-2026-04-23-00001",
  "case_type": "provider_inauthenticity",
  "provider_name": "ABC Healthcare Clinic",
  "npi": "1234567890",
  "status": "open",
  "created_date": "2026-04-23",
  "created_by": "ubada-88888888-8888-8888",
  "assigned_to": "Medicaid Inspector General",
  "priority": "HIGH",
  
  "actions_taken": [
    { "action": "Claims hold placed", "status": "active", "timestamp": "2026-04-23T14:30:00Z" },
    { "action": "Notification sent to provider", "status": "pending", "details": "Letter in mail" },
    { "action": "Case assigned to investigator", "status": "assigned", "investigator": "TBD" }
  ],
  
  "next_steps": [
    "Investigator reviews case",
    "Request detailed documentation from provider",
    "Schedule on-site visit",
    "Interview reported patients",
    "Determine if inauthenticity, waste, abuse, or legitimate"
  ]
}
```

- UPID_RECORDS updated: claim_suspension_status='suspended', claim_suspension_reason='High-risk authenticity investigation'
- VERIFICATION_AUDIT_LOG: Investigation case created and logged
- Provider cannot submit new claims while suspended

---

### UBADA-004: View authenticity patterns Reference
**Priority**: P2 Medium

**Preconditions**:
- Analyst training or reference lookup

**Steps**:
1. Analyst clicks "authenticity patterns Reference"
2. System displays known authenticity patterns and detection methods

**Expected Result**:
```json
{
  "fraud_patterns": [
    {
      "pattern_id": "DUPLICATE_BILLING",
      "name": "Duplicate Billing",
      "description": "Same service billed 2+ times for same patient",
      "detection_method": "Automatic: Claims with same patient, provider, date, code flagged",
      "threshold": "Acceptable: <1% of claims. Investigate: >2%",
      "example": "Emergency room visit billed 3 times",
      "action": "Identify duplicates and recover payment"
    },
    {
      "pattern_id": "BILLING_OUTSIDE_HOURS",
      "name": "Billing Outside Facility Hours",
      "description": "Services claimed at times facility is closed",
      "detection_method": "Automatic: Compare service time to facility hours of operation",
      "example": "Physical therapy billed 24/7 by office with posted 9am-5pm hours",
      "action": "Request verification of service delivery"
    },
    {
      "pattern_id": "UNUSUAL_COMBINATIONS",
      "name": "Unusual Service Combinations",
      "description": "Services never logically combined billed together",
      "detection_method": "Rule-based: Incompatible diagnosis-procedure code pairs",
      "example": "Spinal surgery + pediatric vaccines same visit",
      "action": "Request medical records to verify"
    },
    {
      "pattern_id": "UNBUNDLING",
      "name": "Unbundling",
      "description": "Bundled service billed as separate items",
      "detection_method": "Code combination flagging",
      "example": "Annual physical billed as 10 separate visits",
      "action": "Recover overpayment, provider education"
    },
    {
      "pattern_id": "UPCODING",
      "name": "Upcoding",
      "description": "Higher-cost service billed instead of lower",
      "detection_method": "Compare documentation vs diagnosis codes",
      "example": "Emergency room visit billed as trauma surgery",
      "action": "Review records, recover difference"
    },
    {
      "pattern_id": "PROVIDER_CHANGE",
      "name": "Sudden Provider Change",
      "description": "Dramatic billing change over short timeframe",
      "detection_method": "Volume trend analysis",
      "example": "10 claims over 5 years → 500 claims in 1 month",
      "threshold": "Volume increase >300% = investigate",
      "action": "Audit all recent claims"
    },
    {
      "pattern_id": "SHELL_PROVIDER",
      "name": "Shell Provider",
      "description": "Non-existent or inauthentic provider",
      "detection_method": "Address verification, NPI validation, site visit",
      "example": "Address is PO Box or residential address",
      "action": "Verify legitimacy, halt payments if unverified"
    }
  ],
  
  "fraud_risk_scoring": {
    "low_risk": "0-30",
    "medium_risk": "31-60",
    "high_risk": "61-85",
    "critical_risk": "86-100"
  }
}
```

---

## Category 6: Cross-User & System Tests

### CROSS-001: Member Creates UMID, Provider Creates UPID, System Links Them
**Priority**: P0 Critical

**Preconditions**:
- Fresh test environment
- No prior relationships

**Steps**:
1. **Member John Doe**:
   - Enrolls in Medicaid via UMID Tier 1
   - Gets assigned to Fidelis Care plan
   - UMID created: 00000000-0000-0000-0000-000000000001

2. **Provider Dr. Jane Smith**:
   - Enrolls in Medicaid via UPID Tier 1A (NPI)
   - Gets added to Fidelis Care network
   - UPID created: 11111111-1111-1111-1111-111111111111

3. **Member visits provider**:
   - Calls provider office
   - Office verifies member is in their network
   - Office asks for member's Medicaid ID

4. **System flow**:
   - Provider searches: "Is John Doe eligible and in my network?"
   - System queries: UMID_RECORDS + WHUP network status
   - System returns: "Yes, John Doe eligible. Covered under Fidelis Care. Copay: $15."

5. **Provider submits claim**:
   - Service date: 2026-04-20
   - Charge: $150
   - System validates: UMID eligible on 2026-04-20, UPID verified, not OIG-excluded
   - Claim accepted

**Expected Result**:
- Member and provider can reference each other (no duplicate identities)
- System maintains referential integrity (UMID → WHUP → UPID)
- Claim successfully submitted and tracked
- Audit trail shows full interaction path

---

### CROSS-002: Stakeholder Reviews Member-Provider Interaction
**Priority**: P1 High

**Preconditions**:
- Claim from CROSS-001 submitted
- Stakeholder has Admin authority

**Steps**:
1. Stakeholder searches: "How many claims from Dr. Jane Smith in April?"
2. System queries: All claims from UPID 11111111...
3. System returns: 145 claims in April, $21,750 total

4. Stakeholder searches: "Is Dr. Jane Smith seeing unusual patterns?"
5. System runs authenticity verification on provider
6. System returns: Risk score 12 (low - normal billing patterns)

**Expected Result**:
- Stakeholder can see provider activity from system-wide view
- WHUP, UMID, UPID data integrated seamlessly
- No fragmentation or duplicate records

---

### CROSS-003: Analyst Flags Provider, System Blocks Future Claims
**Priority**: P1 High

**Preconditions**:
- Analyst has assessed different provider ("ABC Clinic") as high-risk
- Investigation case created
- Claims hold activated

**Steps**:
1. Same day, new member tries to see ABC Clinic
2. Provider attempts to submit new claim for that member
3. System checks: UPID_RECORDS.claim_suspension_status = 'suspended'
4. System rejects claim

**Expected Result**:
```json
{
  "claim_submission_status": "REJECTED",
  "reason": "Provider claims suspended pending authenticity investigation",
  "case_id": "INV-2026-04-23-00001",
  "effective_date": "2026-04-23",
  "member_notification": "Member has been notified of claims hold"
}
```

- No claims accepted from suspended provider until investigation resolved
- Real-time operational protection

---

## Test Execution Summary

### Test Environment Requ