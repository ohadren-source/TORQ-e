# Reading Engine Data Sources Roadmap: 1-at-a-Time Implementation Plan

## Overview

TORQ-e's Reading Engine integrates 5 external data sources. We tackle them **one at a time**: design → code → test → ship. Each source is independent; no blocking dependencies.

**Current Status**: Framework complete. Ready to implement Source 1.

---

## The Five Sources (Priority Order)

```
┌─────────────────────────────────────────────────────────┐
│  SOURCE 1: CMS NPPES (Provider Verification)            │
│  Status: TODO | Criticality: P0 | Complexity: Low       │
├─────────────────────────────────────────────────────────┤
│  • Verifies NPI numbers for individual providers        │
│  • Checks if provider actually exists                   │
│  • Validates name and other demographics                │
│  • PUBLIC API (free, easy)                              │
│  • Used by: UPID enrollment flow                        │
│  • Blocks: Provider can't enroll without this           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  SOURCE 2: OIG Exclusion List (inauthenticity Prevention)        │
│  Status: TODO | Criticality: P0 | Complexity: Low       │
├─────────────────────────────────────────────────────────┤
│  • Checks if provider is excluded from Medicare/Medicaid│
│  • inauthenticity convictions, license revocations               │
│  • PUBLIC API (free)                                    │
│  • Used by: UPID verification, claim submission         │
│  • Blocks: Excluded providers can't submit claims       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  SOURCE 3: State License Verification                   │
│  Status: TODO | Criticality: P1 | Complexity: Medium    │
├─────────────────────────────────────────────────────────┤
│  • Verifies medical/nursing/pharmacy licenses are active│
│  • Checks state licensing board databases               │
│  • VARIES BY STATE (NY, different URL per license type) │
│  • Some free, some require credentials                  │
│  • Used by: UPID verification (Tier 1A & 1B)           │
│  • Blocks: Can't verify provider without license check  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  SOURCE 4: IRS EIN Lookup (Organization Verification)   │
│  Status: TODO | Criticality: P1 | Complexity: Medium    │
├─────────────────────────────────────────────────────────┤
│  • Verifies Tax ID (EIN) for healthcare organizations   │
│  • Checks business is registered and not delinquent     │
│  • PUBLIC API (free, but limited rate) + Private DB     │
│  • Used by: UPID Tier 1B (organization enrollment)      │
│  • Blocks: Can't enroll organizations without this      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  SOURCE 5: EMEDNY Claims Integration                    │
│  Status: TODO | Criticality: P0 | Complexity: High      │
├─────────────────────────────────────────────────────────┤
│  • Integrates existing claims processing system         │
│  • Reads claims data for authenticity verification                │
│  • Submits claims on behalf of providers                │
│  • INTERNAL NYS SYSTEM (secure, requires VPN/auth)      │
│  • Used by: All claim submission, inauthenticity analysis        │
│  • Blocks: Nothing (mock in test mode); critical for go-live
└─────────────────────────────────────────────────────────┘
```

---

## Implementation Template (Repeat for Each Source)

### Phase: Design
- [ ] Document API contract (request/response)
- [ ] Identify failure modes (timeout, auth error, data mismatch)
- [ ] Plan test data set
- [ ] Define caching strategy
- [ ] Create mock response for test mode

### Phase: Code
- [ ] Write adapter class (test mode mock + prod stub)
- [ ] Implement error handling (retry logic, fallbacks)
- [ ] Add metrics/logging
- [ ] Integrate with Reading Engine dispatcher
- [ ] Create integration tests

### Phase: Test
- [ ] Unit tests (mock mode)
- [ ] Integration tests (with test data)
- [ ] Performance tests (latency, timeout handling)
- [ ] Security tests (auth, encryption)
- [ ] Regression tests (don't break other sources)

### Phase: Ship
- [ ] Code review
- [ ] Merge to main
- [ ] Deploy to test environment
- [ ] Document in runbooks
- [ ] Ready for next source

---

## Source 1: CMS NPPES (National Provider Enumeration System)

### What It Does
Verifies NPI (National Provider Number) for individual healthcare providers (doctors, nurses, etc.).

### API Details

**Endpoint**: `https://npiregistry.cms.hhs.gov/api`
**Method**: GET
**Auth**: None (public)
**Rate Limit**: 100 requests per second
**Response Time**: Usually <500ms

**Request**:
```
GET https://npiregistry.cms.hhs.gov/api?number=1234567890&enumeration_type=NPI-1
```

**Response**:
```json
{
  "result_count": 1,
  "results": [
    {
      "enumeration_type": "NPI-1",
      "number": "1234567890",
      "last_updated": "2025-01-15",
      "basic": {
        "first_name": "Jane",
        "last_name": "Smith",
        "middle_name": "Marie",
        "name_prefix": "Dr.",
        "credential_text": "MD",
        "sole_proprietor": "Y"
      },
      "addresses": [
        {
          "address_purpose": "LOCATION",
          "address_type": "DOM",
          "address_1": "123 Main Street",
          "city": "New York",
          "state": "NY",
          "zip": "10001",
          "country_code": "US",
          "country_name": "United States"
        }
      ],
      "taxonomies": [
        {
          "code": "207R00000X",
          "desc": "Physician",
          "primary": true
        }
      ]
    }
  ]
}
```

### Implementation Plan

**Step 1: Design (1 day)**
- Create mock response set (3 providers: valid, name mismatch, not found)
- Define UPID adapter class signature
- Plan error handling (timeout → fallback, 404 → not verified)
- Document in ARCHITECTURE_TECHNICAL.md

**Step 2: Code (2 days)**
```python
# /adapters/cms_nppes.py

class CMSNPPESAdapter:
    """Verify NPI against CMS NPPES database"""
    
    API_URL = "https://npiregistry.cms.hhs.gov/api"
    TIMEOUT = 5  # seconds
    
    def __init__(self, env='test'):
        self.env = env
    
    def query(self, npi, last_name, dob):
        """
        Query CMS NPPES for provider verification
        
        Args:
            npi: 10-digit National Provider Number
            last_name: Provider last name (for validation)
            dob: Provider date of birth (for validation)
        
        Returns:
            {
              'verified': bool,
              'npi': str,
              'name': str,
              'specialty': str,
              'address': str,
              'license_number': str,
              'source': str,
              'fingerprint': str,
              'timestamp': datetime
            }
        """
        
        if self.env == 'test':
            return self._mock_query(npi, last_name)
        else:
            return self._real_query(npi, last_name, dob)
    
    def _mock_query(self, npi, last_name):
        """Test mode: Return deterministic mock responses"""
        
        mock_data = {
            '1234567890': {
                'verified': True,
                'name': 'Smith',
                'first_name': 'Jane',
                'specialty': 'Pediatrics',
                'address': '123 Main St, New York, NY 10001',
                'license': 'NY123456'
            },
            '9876543210': {
                'verified': True,
                'name': 'Johnson',
                'first_name': 'John',
                'specialty': 'Family Medicine',
                'address': '456 Oak Ave, Buffalo, NY 14202',
                'license': 'NY654321'
            },
            '0000000000': {
                'verified': False,
                'reason': 'NPI not found in registry'
            }
        }
        
        result = mock_data.get(npi, {'verified': False, 'reason': 'NPI not found'})
        
        if result['verified']:
            # Validate name matches
            if last_name.upper() != result['name'].upper():
                return {'verified': False, 'reason': 'Name mismatch'}
            
            return {
                'verified': True,
                'npi': npi,
                'name': result['name'],
                'first_name': result['first_name'],
                'specialty': result['specialty'],
                'address': result['address'],
                'license_number': result['license'],
                'source': 'cms_nppes_mock',
                'fingerprint': f"npi_{npi}_{result['name']}",
                'timestamp': datetime.now()
            }
        else:
            return result
    
    def _real_query(self, npi, last_name, dob):
        """Prod mode: Call actual CMS API"""
        
        try:
            response = requests.get(
                self.API_URL,
                params={'number': npi, 'enumeration_type': 'NPI-1'},
                timeout=self.TIMEOUT
            )
            response.raise_for_status()
        except requests.Timeout:
            return {'verified': False, 'reason': 'CMS NPPES timeout'}
        except requests.RequestException as e:
            return {'verified': False, 'reason': f'CMS NPPES error: {str(e)}'}
        
        data = response.json()
        
        if data['result_count'] == 0:
            return {'verified': False, 'reason': 'NPI not found'}
        
        result = data['results'][0]
        api_last_name = result['basic']['last_name']
        api_first_name = result['basic']['first_name']
        
        # Validate name matches
        if api_last_name.upper() != last_name.upper():
            return {
                'verified': False,
                'reason': 'Name mismatch',
                'cms_name': api_last_name,
                'provided_name': last_name
            }
        
        # Extract specialty
        specialty = 'Unknown'
        if result.get('taxonomies'):
            specialty = result['taxonomies'][0].get('desc', 'Unknown')
        
        # Extract address
        address = 'Not found'
        if result.get('addresses'):
            addr = result['addresses'][0]
            address = f"{addr['address_1']}, {addr['city']}, {addr['state']} {addr['zip']}"
        
        return {
            'verified': True,
            'npi': npi,
            'name': api_last_name,
            'first_name': api_first_name,
            'specialty': specialty,
            'address': address,
            'license_number': None,  # NPPES doesn't have state license number
            'source': 'cms_nppes_real',
            'fingerprint': f"npi_{npi}_{api_last_name}_{dob}",
            'timestamp': datetime.now()
        }
```

**Step 3: Test (2 days)**

```python
# /tests/test_cms_nppes.py

import pytest
from adapters.cms_nppes import CMSNPPESAdapter

class TestCMSNPPES:
    
    def test_valid_provider_mock_mode(self):
        adapter = CMSNPPESAdapter(env='test')
        result = adapter.query('1234567890', 'Smith', '1965-05-20')
        
        assert result['verified'] == True
        assert result['npi'] == '1234567890'
        assert result['name'] == 'Smith'
        assert result['source'] == 'cms_nppes_mock'
    
    def test_name_mismatch_mock_mode(self):
        adapter = CMSNPPESAdapter(env='test')
        result = adapter.query('1234567890', 'Wrong', '1965-05-20')
        
        assert result['verified'] == False
        assert result['reason'] == 'Name mismatch'
    
    def test_npi_not_found_mock_mode(self):
        adapter = CMSNPPESAdapter(env='test')
        result = adapter.query('0000000000', 'Smith', '1965-05-20')
        
        assert result['verified'] == False
    
    def test_performance_response_time(self):
        import time
        adapter = CMSNPPESAdapter(env='test')
        
        start = time.time()
        result = adapter.query('1234567890', 'Smith', '1965-05-20')
        elapsed = time.time() - start
        
        assert elapsed < 0.1  # Should be < 100ms (mock)
        assert result['verified'] == True
```

**Step 4: Ship (1 day)**
- Code review
- Merge to main
- Update READING_ENGINE_SOURCES_ROADMAP.md (mark Source 1 COMPLETE)
- Deploy to test environment

---

## Source 2: OIG Exclusion List

### What It Does
Checks if provider is excluded from Medicare/Medicaid participation (inauthenticity, conviction, license revocation).

### API Details

**Data Source**: `https://oig.hhs.gov/exclusions/`
**Format**: CSV download + API (experimental)
**Auth**: None (public)
**Update Frequency**: Monthly
**Data**: ~100,000 excluded providers

### Implementation Plan

**Timeline**: Days 5-8 (after Source 1 ships)

**Key Differences from CMS NPPES**:
- Monthly data dump (not real-time query API)
- Need to download and cache locally
- Match on NPI OR EIN (not just name)
- Simpler: just binary excluded/not excluded

**Mock Data**:
```python
{
    '1234567890': False,  # Not excluded
    '9876543210': False,  # Not excluded
    '5555555555': True,   # Excluded (inauthenticity)
    '77777777777': True   # Excluded (license revocation)
}
```

**Prod Integration**:
- Download monthly CSV from OIG
- Parse into database table or in-memory cache
- Lookup by NPI or EIN
- Fallback if download fails: mark as "not verified" (don't deny on tech failure)

---

## Source 3: State License Verification

### What It Does
Verifies that doctor/nurse/pharmacist licenses are active in NY state.

### API Details

**State Database**: NY Department of Education, Office of Professions
**License Types**: MD, DO, RN, LPN, DDS, Pharmacist, etc.
**Auth**: None for public lookup (may need credentials for bulk queries)
**Response Time**: Variable (1-5 seconds)

### Implementation Plan

**Timeline**: Days 9-12 (after Source 2 ships)

**Key Challenge**: 
- Different URLs for different license types
- Some states have public APIs, some require credentials
- NY state may have custom integration requirements

**Design Phase**:
- Research NY licensing board API for each license type
- Determine if single endpoint or multiple
- Plan fallback (if state system down, what do we do? Allow enrollment with note?)

**Mock Data**:
```python
{
    'NY123456': {'verified': True, 'name': 'Smith', 'license_type': 'MD'},
    'NY654321': {'verified': True, 'name': 'Johnson', 'license_type': 'RN'},
    'NY999999': {'verified': False, 'reason': 'License expired'},
}
```

---

## Source 4: IRS EIN Lookup

### What It Does
Verifies Tax ID (EIN) for healthcare organizations (hospitals, clinics, etc.).

### API Details

**Data Source**: IRS EIN lookup + State business registry
**Public API**: IRS EIN Match API (limited, free)
**Auth**: Public endpoint, rate limited
**Response Time**: Usually <1 second

### Implementation Plan

**Timeline**: Days 13-16 (after Source 3 ships)

**Integration Points**:
- IRS public EIN lookup (free tier)
- NY State Business Registry (additional verification)
- Check if organization is delinquent on taxes

**Mock Data**:
```python
{
    '12-3456789': {
        'verified': True,
        'org_name': 'ABC Healthcare Clinic',
        'status': 'Active',
        'type': 'Non-profit'
    },
    '99-9999999': {
        'verified': False,
        'reason': 'EIN not found'
    },
}
```

---

## Source 5: EMEDNY Claims Integration (Largest Effort)

### What It Does
Integrates existing claims processing system. Reads historical claims for authenticity verification; submits new claims for processing.

### API Details

**System**: NY State electronic Medicaid (EMEDNY)
**Access**: Internal NYS system, requires VPN + authentication
**Endpoints**: Claims submission, eligibility verification, claim status lookup
**Auth**: Certificate-based or API key
**Response Time**: 1-10 seconds (queue-based processing)

### Implementation Plan

**Timeline**: Days 17-25 (biggest effort)

**Phases**:
1. **Design (2 days)**
   - Get VPN access to EMEDNY
   - Document API contract
   - Plan batch vs real-time submission
   - Define claim status polling strategy

2. **Code (4 days)**
   - Implement claims submission endpoint
   - Implement claim status lookup
   - Implement claims history query (authenticity verification)
   - Error handling (rejected claims, timeouts)

3. **Test (2 days)**
   - Integration test with test EMEDNY instance
   - Load test (can we submit 100 claims/min?)
   - Security test (auth, encryption)
   - Fallback test (what if EMEDNY is down?)

4. **Ship (1 day)**
   - Code review
   - Deploy
   - Monitor for issues

---

## Progress Tracking

```
COMPLETED                        IN PROGRESS              TODO
───────────────────────────────────────────────────────────────
✓ Framework Design               Source 1: CMS NPPES      Source 2: OIG Exclusion
✓ Database Schema                (Design Phase)           Source 3: State License
✓ API Specification                                       Source 4: IRS EIN
✓ Test/Prod Switch                                        Source 5: EMEDNY Claims
✓ Test Cases
✓ Business Arch Doc
✓ Technical Arch Doc
```

---

## Dependencies & Blockers

### No Hard Blockers
Each source is independent. We can implement them in any order.

**Soft Dependencies** (preferred order):
1. CMS NPPES (needed first: high frequency, simple)
2. OIG Exclusion (quick wins, inauthenticity prevention)
3. State License (medium complexity)
4. IRS EIN (medium complexity)
5. EMEDNY Claims (complex, but independent)

### Fallback Strategy
If a source fails to integrate on schedule:
- **CMS NPPES**: Revert to manual NPI verification (analyst reviews)
- **OIG Exclusion**: Allow claims through but flag for analyst review
- **State License**: Allow enrollment but require manual verification
- **IRS EIN**: Allow enrollment but require manual verification
- **EMEDNY**: Run in test mode only; no prod claim submission

---

## Communication Template (For Each Source Release)

**Example: After Source 1 Completes**

```
✅ READING ENGINE SOURCE 1 COMPLETE: CMS NPPES Verification

Status: Shipped
Timeline: Design (1d) + Code (2d) + Test (2d) + Ship (1d) = 6 days
Metrics:
- 12 unit tests (100% pass rate)
- 4 integration tests (100% pass rate)
- API response time: <100ms (mock), <500ms (real)
- Error rate: 0% on valid requests, proper handling of timeouts/not found

What Works Now:
✓ Individual providers can enroll with NPI verification (Tier 1A)
✓ System validates name matches
✓ Invalid/not-found NPIs properly rejected

Next: Source 2 (OIG Exclusion List) starting tomorrow
```

