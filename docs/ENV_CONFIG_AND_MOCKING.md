# TORQ-e Environment Configuration & Test/Prod Switch

## Environment Variable

```bash
TORQUE_ENV=test    # or "prod"
```

Set at deployment time. All API calls check this variable before executing.

---

## Architecture Pattern

Every endpoint follows this pattern:

```python
@app.route('/member/eligibility', methods=['GET'])
def get_member_eligibility():
    umid = request.args.get('umid')
    
    if os.getenv('TORQUE_ENV') == 'test':
        return _mock_member_eligibility(umid)
    else:  # prod
        return _real_member_eligibility(umid)

def _mock_member_eligibility(umid):
    """Test mode: Return deterministic dummy data"""
    return {
        'eligible': True,
        'eligibility_category': 'MAGI_Non_Pregnant_Adult',
        'benefits_effective_date': '2026-05-01',
        'renewal_date': '2027-04-30',
        '_test_mode': True,
        '_mock_reason': 'Test environment - no real data sources connected'
    }

def _real_member_eligibility(umid):
    """Prod mode: Call actual reading engine"""
    # Query UMID_RECORDS
    # Run eligibility algorithm
    # Return real result
    pass  # Stub - implement when connecting to prod systems
```

---

## Test Mode Behavior

### All Endpoints Return Mock Data

Test responses include:
1. **Valid structure** (matches prod response schema)
2. **Realistic values** (appropriate for testing)
3. **`_test_mode: true`** flag (indicates mock response)
4. **`_mock_reason`** field (explains why it's mocked)

### Example Test Responses

```json
// POST /member/verify-identity (Tier 1 - Digital ID)
{
  "verified": true,
  "fingerprint_match": "drivers_license_john_doe_1980_01_15",
  "_test_mode": true,
  "_mock_reason": "Test environment - no state DMV integration"
}

// POST /provider/verify-credentials (Tier 1A - NPI)
{
  "verified": true,
  "fingerprint_match": "npi_1234567890_smith_1965_05_20",
  "_test_mode": true,
  "_mock_reason": "Test environment - no CMS NPPES integration"
}

// GET /stakeholder/program-efficiency
{
  "total_spending_cents": 5120000000000,
  "total_members": 3200000,
  "cppm": 133400,
  "spending_by_category": [
    { "category": "Hospital/ER", "amount_cents": 1850000000000, "percent": 36 },
    { "category": "Outpatient", "amount_cents": 1230000000000, "percent": 24 },
    { "category": "Pharmacy", "amount_cents": 840000000000, "percent": 16 }
  ],
  "_test_mode": true,
  "_mock_reason": "Test environment - no EMEDNY claims integration"
}

// POST /analyst/inauthenticity-assessment
{
  "assessment_id": "ASS-2026-04-23-00001",
  "provider_name": "ABC Healthcare Clinic (TEST)",
  "npi": "1234567890",
  "fraud_risk_score": 78,
  "assessment_level": "HIGH RISK",
  "red_flags": [
    "address_is_po_box",
    "billing_volume_2x_typical",
    "duplicate_billing_same_date"
  ],
  "recommendation": "FLAG_FOR_INVESTIGATION",
  "_test_mode": true,
  "_mock_reason": "Test environment - no CMS/OIG exclusion check integration"
}
```

---

## Prod Mode Behavior (Stubs)

### All Endpoints Call Real Systems (Not Yet Implemented)

```python
def _real_member_eligibility(umid):
    """Prod mode: Call actual reading engine and database"""
    
    # Step 1: Query TORQ-e database
    umid_record = db.query(UMID_RECORDS).filter(UMID_RECORDS.umid == umid).first()
    if not umid_record:
        raise RecordNotFound(f"UMID {umid} not found")
    
    # Step 2: Extract member info
    household_size = umid_record.household_size
    monthly_income = decrypt(umid_record.monthly_income_cents) / 100
    citizenship = umid_record.citizenship_status
    
    # Step 3: Run NYS Medicaid eligibility algorithm
    eligibility = check_nys_magi_limits(
        household_size=household_size,
        monthly_income=monthly_income,
        citizenship=citizenship
    )
    
    # Step 4: Check categorical eligibility
    if eligibility['eligible']:
        category = determine_eligibility_category(
            age=umid_record.age,
            disability=umid_record.disability_status,
            pregnancy=umid_record.pregnancy_status
        )
    else:
        category = None
    
    # Step 5: Return result
    return {
        'eligible': eligibility['eligible'],
        'eligibility_category': category,
        'benefits_effective_date': eligibility['effective_date'],
        'renewal_date': eligibility['renewal_date']
    }
```

**Stub comments**: `pass  # TODO: Implement when [system] is ready`

---

## Test Data Sets

### Pre-Built Test Identifiers

For testing without creating new records:

```
TEST MEMBERS (UMID):
- umid: 00000000-0000-0000-0000-000000000001
  Name: John Doe | DOB: 1980-01-15 | MPI: TEST-00001
  Income: $2,100/month | Household: 3 | Eligible: YES
  
- umid: 00000000-0000-0000-0000-000000000002
  Name: Jane Smith | DOB: 1975-06-20 | MPI: TEST-00002
  Income: $5,000/month | Household: 2 | Eligible: NO
  
- umid: 00000000-0000-0000-0000-000000000003
  Name: Alice Johnson | DOB: 1992-03-10 | MPI: TEST-00003
  Income: $1,500/month | Household: 1 | Eligible: YES

TEST PROVIDERS (UPID):
- upid: 11111111-1111-1111-1111-111111111111
  Name: Dr. Jane Smith | NPI: 1234567890 | Type: Individual | Status: Active
  
- upid: 22222222-2222-2222-2222-222222222222
  Name: ABC Healthcare Clinic | EIN: 12-3456789 | Type: Organization | Status: Active
  
- upid: 33333333-3333-3333-3333-333333333333
  Name: XYZ inauthenticity Clinic | NPI: 9876543210 | Type: Individual | OIG Status: EXCLUDED

TEST PLANS (WHUP):
- uhwp: 44444444-4444-4444-4444-444444444444
  Name: Fidelis Care HMO | NY Plan ID: FID-001 | CMS: H1234 | Members: 245,000
  
- uhwp: 55555555-5555-5555-5555-555555555555
  Name: Anthem Managed Care | NY Plan ID: ANT-001 | CMS: H5678 | Members: 180,000

TEST STAKEHOLDERS (USHI):
- ushi: 66666666-6666-6666-6666-666666666666
  Name: Jane Johnson | Agency: NYS DOH | Authority: Admin | Access: All Counties
  
- ushi: 77777777-7777-7777-7777-777777777777
  Name: John Smith | Agency: NYS DOH | Authority: Analyst | Access: NYC Only

TEST ANALYSTS (UBADA):
- ubada: 88888888-8888-8888-8888-888888888888
  Name: Sarah Williams | Type: inauthenticity | Skill: Senior
  
- ubada: 99999999-9999-9999-9999-999999999999
  Name: Michael Chen | Type: Business | Skill: Junior
```

Use these in test mode to avoid creating new test data repeatedly.

---

## Test Mode API Usage

### Example Test Flow

```bash
# 1. Login with test UMID
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "00000000-0000-0000-0000-000000000001",
    "role_type": "umid"
  }'

Response (Test Mode):
{
  "session_token": "test_token_abc123",
  "user_profile": {
    "umid": "00000000-0000-0000-0000-000000000001",
    "name": "John Doe",
    "status": "verified"
  },
  "_test_mode": true,
  "_mock_reason": "Test environment - no 2FA verification"
}

# 2. Check eligibility
curl -X GET http://localhost:8000/member/eligibility \
  -H "Authorization: Bearer test_token_abc123" \
  -H "X-TORQUE-ENV: test"

Response (Test Mode):
{
  "eligible": true,
  "eligibility_category": "MAGI_Non_Pregnant_Adult",
  "benefits_effective_date": "2026-05-01",
  "renewal_date": "2027-04-30",
  "_test_mode": true,
  "_mock_reason": "Test environment - using mock eligibility algorithm"
}

# 3. Check provider network status
curl -X GET http://localhost:8000/plan/network-status \
  -H "Authorization: Bearer test_token_abc123" \
  -d '{"uhwp": "44444444-4444-4444-4444-444444444444", "provider_npi": "1234567890"}'

Response (Test Mode):
{
  "provider_status": "in_network",
  "provider_name": "Dr. Jane Smith",
  "specialty": "pediatrics",
  "accepting_new_patients": true,
  "copay_innetwork": 15,
  "_test_mode": true,
  "_mock_reason": "Test environment - using mock network directory"
}
```

---

## Switching to Prod

### Step 1: Verify Real Integrations

Before flipping to prod, ensure these are connected:

- [ ] TORQ-e database live with real UMID/UPID/WHUP/USHI/UBADA records
- [ ] CMS NPPES database integration (provider verification)
- [ ] State DMV/ID verification integration (member identity)
- [ ] EMEDNY claims database read access
- [ ] State licensing board APIs
- [ ] OIG exclusions list integration
- [ ] NYS Medicaid eligibility algorithm
- [ ] Plan network directories (all plans)

### Step 2: Set Environment Variable

```bash
# Docker
ENV TORQUE_ENV=prod

# Kubernetes
env:
  - name: TORQUE_ENV
    value: "prod"

# Direct (local testing)
export TORQUE_ENV=prod
```

### Step 3: Monitor Logs

All prod calls log to audit trail:

```
2026-05-15 14:30:22 | PROD | GET /member/eligibility | umid=xyz... | Result: Eligible
2026-05-15 14:31:05 | PROD | POST /provider/verify-credentials | npi=1234567890 | Result: Verified
2026-05-15 14:32:18 | PROD | POST /analyst/inauthenticity-assessment | provider=abc-clinic | Result: High Risk
```

### Step 4: Gradual Rollout

Don't flip all endpoints at once:

**Week 1-2**: Test mode for public endpoints (member eligibility, provider network lookup)
**Week 3**: Add analyst authenticity verification in prod
**Week 4**: Add stakeholder reporting
**Week 5**: Add claims submission (most critical)

---

## Logging Pattern

All endpoints log both test and prod calls:

```python
import logging

logger = logging.getLogger(__name__)

def get_member_eligibility(umid):
    env = os.getenv('TORQUE_ENV', 'test')
    
    if env == 'test':
        result = _mock_member_eligibility(umid)
        logger.info(f"TEST | GET /member/eligibility | umid={umid} | Eligible={result['eligible']}")
    else:
        result = _real_member_eligibility(umid)
        logger.info(f"PROD | GET /member/eligibility | umid={umid} | Eligible={result['eligible']}")
    
    return result
```

Test logs go to `logs/test.log`
Prod logs go to `logs/prod.log` (with audit trail backup to database)

---

## Configuration File

```yaml
# config/torque.yml

test:
  environment: "test"
  mock_all_external_calls: true
  database: "torque_test"
  log_level: "DEBUG"
  features:
    fraud_detection: true
    eligibility_check: true
    network_lookup: true
    claims_submission: true  # Returns mock claim ID

prod:
  environment: "prod"
  mock_all_external_calls: false
  database: "torque_prod"
  log_level: "INFO"
  features:
    fraud_detection: true
    eligibility_check: true
    network_lookup: true
    claims_submission: true  # Actually submits to EMEDNY
  
  integrations:
    cms_nppes: "https://npiregistry.cms.hhs.gov/api"
    oig_exclusions: "https://oig.hhs.gov/exclusions/api"
    emedny: "https://emedny.ny.gov/api"  # Not public (internal)
    state_dmv: "https://dmv.ny.gov/api"  # Internal
    medicaid_eligibility: "internal_algorithm"
```

Set via environment:

```bash
TORQUE_CONFIG_ENV=test    # Loads config/torque.yml[test]
TORQUE_CONFIG_ENV=prod    # Loads config/torque.yml[prod]
```

---

## Summary

| Aspect | Test Mode | Prod Mode |
|--------|-----------|-----------|
| Real Database | ✓ Yes (test DB) | ✓ Yes (prod DB) |
| External APIs | ✗ Mocked | ✓ Real |
| Reading Engine | �