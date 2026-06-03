# TORQ-e Technical Architecture for Engineers & Data Analysts

## System Overview

TORQ-e is a unified identity and authenticity verification platform for NY Medicaid. Core architecture:

```
┌──────────────────────────────────────────────────────────────┐
│              Frontend (Web + Mobile)                          │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐  │
│  │ Member Portal  │  │ Provider Portal│  │ Admin Dashboard│  │
│  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘  │
└───────────┼──────────────────┼──────────────────┼────────────┘
            │                  │                  │
            └──────────────────┼──────────────────┘
                               │ REST API (TLS 1.3)
                               │
┌──────────────────────────────▼──────────────────────────────┐
│              API Layer (Flask/FastAPI)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ /auth/login, /member/eligibility, /provider/submit   │  │
│  │ /plan/network-status, /stakeholder/efficiency        │  │
│  │ /analyst/inauthenticity-assessment, etc.                      │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────────┬───────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌─────────────────┐  ┌─────────────────┐  ┌──────────────────┐
│  Reading Engine │  │  Database Layer │  │  Cache Layer     │
│  (Data Source   │  │  (PostgreSQL)   │  │  (Redis)         │
│   Integration)  │  │                 │  │                  │
└─────────────────┘  └─────────────────┘  └──────────────────┘
        │                      │
        │ (1) CMS NPPES        │
        │ (2) OIG Exclusions   │ ┌─ UMID_RECORDS
        │ (3) State Licensing  │ ├─ UPID_RECORDS
        │ (4) IRS/EIN Lookup   │ ├─ WHUP_RECORDS
        │ (5) EMEDNY Claims    │ ├─ USHI_RECORDS
        │ (6) Eligibility Algo │ ├─ UBADA_RECORDS
        │ (7) authenticity patterns   │ ├─ IDENTIFIER_MAPPINGS
        │ (8) Plan Network Dir │ └─ VERIFICATION_AUDIT_LOG
        │                      │
        └──────────────────────┘

```

---

## Core Data Model

### Entity Relationship Diagram

```
UMID_RECORDS (Member)
  ├─ UUID: umid (PK)
  ├─ VARCHAR: federal_id_hash (SSN SHA256)
  ├─ BYTEA: first_name_encrypted, last_name_encrypted, dob_encrypted
  ├─ INT: household_size, monthly_income_cents
  ├─ VARCHAR: citizenship_status, current_employment_status
  ├─ ENUM: verification_tier (tier_1_digital, tier_2_inperson)
  ├─ TIMESTAMP: verified_at, created_at, updated_at
  ├─ BOOLEAN: 2fa_enabled, preferred_umid_locked, is_active
  └─ FK → IDENTIFIER_MAPPINGS (legacy_id mapping)

UPID_RECORDS (Provider)
  ├─ UUID: upid (PK)
  ├─ ENUM: provider_type (individual, organization)
  ├─ VARCHAR: npi (UNIQUE, individuals), ein (UNIQUE, organizations)
  ├─ BYTEA: first_name_encrypted, last_name_encrypted, dob_encrypted
  ├─ BYTEA: legal_business_name_encrypted, primary_address_encrypted
  ├─ VARCHAR: state_license_number_encrypted, state_license_state
  ├─ ENUM: verification_tier (tier_1a_npi, tier_1b_ein, tier_2_inperson)
  ├─ BOOLEAN: npi_verified_against_cms, ein_verified_against_irs
  ├─ BOOLEAN: oig_exclusion_checked, state_licensing_verified
  ├─ VARCHAR: oig_exclusion_status, claim_suspension_status
  ├─ TIMESTAMP: verified_at, created_at, updated_at
  └─ BOOLEAN: preferred_upid_locked, is_active

WHUP_RECORDS (Plan)
  ├─ UUID: uhwp (PK)
  ├─ BYTEA: plan_name_encrypted
  ├─ VARCHAR: parent_ein, ny_state_plan_id (UNIQUE), cms_plan_id (UNIQUE)
  ├─ ENUM: plan_type (hmo, ppo, mltc, prepaid)
  ├─ INT: network_provider_count, member_enrollment_count
  ├─ JSONB: service_counties (array of FIPS codes)
  ├─ NUMERIC: hedis_score_latest, cahps_score_latest
  ├─ BOOLEAN: network_adequacy_verified, quality_plan_submission_ready, is_active
  └─ TIMESTAMP: created_at, updated_at

USHI_RECORDS (Government Stakeholder)
  ├─ UUID: ushi (PK)
  ├─ BYTEA: gov_employee_id_encrypted (UNIQUE)
  ├─ BYTEA: first_name_encrypted, last_name_encrypted
  ├─ VARCHAR: agency_code (NYS_DOH, CMS, OIG, etc.)
  ├─ INT: authority_level (0-5: Super Admin → View-Only)
  ├─ JSONB: data_access_scope {counties[], programs[], data_types[], read_write}
  ├─ BOOLEAN: 2fa_enabled, annual_reauth_required, is_active
  ├─ DATE: annual_reauth_due
  ├─ TIMESTAMP: last_reauth_completed_at, last_access_at, created_at, updated_at
  └─ UUID: created_by_ushi (who provisioned)

UBADA_RECORDS (Data Analyst)
  ├─ UUID: ubada (PK)
  ├─ ENUM: analyst_type (inauthenticity, business, research)
  ├─ ENUM: skill_level (junior, senior, lead)
  ├─ BYTEA: gov_employee_id_encrypted (UNIQUE)
  ├─ BYTEA: first_name_encrypted, last_name_encrypted
  ├─ JSONB: certifications [{name, issued_date, expiry_date, issuer}]
  ├─ JSONB: performance_metrics {cases_reviewed, confirmed_inauthenticity, false_positive_rate, etc.}
  ├─ BOOLEAN: 2fa_enabled, is_active
  ├─ TIMESTAMP: last_case_reviewed_at, created_at, updated_at
  └─ UUID: created_by_ushi (who provisioned)

IDENTIFIER_MAPPINGS
  ├─ BIGINT: mapping_id (PK, AUTO_INCREMENT)
  ├─ ENUM: universal_id_type (umid, upid, uhwp, ushi, ubada)
  ├─ UUID: universal_id (FK to appropriate table)
  ├─ VARCHAR: legacy_id_type (mpi_id, medicaid_id, npi, ein, cms_plan_id, etc.)
  ├─ BYTEA: legacy_id_value_encrypted
  ├─ CHAR(64): legacy_id_hash (SHA256, UNIQUE)
  ├─ BOOLEAN: is_primary
  ├─ TIMESTAMP: mapping_created_at
  ├─ VARCHAR: source_system (mpi, emedny, npi_registry, etc.)
  └─ BOOLEAN: verified

VERIFICATION_AUDIT_LOG (Immutable Append-Only)
  ├─ BIGINT: log_id (PK, AUTO_INCREMENT)
  ├─ ENUM: identifier_type (umid, upid, uhwp, ushi, ubada)
  ├─ UUID: identifier_id (no FK, allows orphan references)
  ├─ VARCHAR: verification_step (tier_1_govt_id_check, cms_npi_verification, etc.)
  ├─ ENUM: verification_result (passed, failed, pending, manual_review)
  ├─ VARCHAR: data_checked_against (cms_nppes, irs, state_dmv, oig_exclusions, etc.)
  ├─ TEXT: details (encrypted if contains PII)
  ├─ CHAR(64): ip_address_hash (SHA256)
  ├─ CHAR(64): user_agent_hash (SHA256)
  ├─ TIMESTAMP: timestamp (indexed, partitioned by month)
  ├─ UUID: completed_by_ushi (who executed verification)
  └─ VARCHAR: outcome_action (record_created, access_denied, escalated, etc.)
```

---

## API Contract Specification

### Request/Response Envelope

All API responses follow standard envelope:

```json
{
  "status": "success" | "error",
  "data": { ... },           // Present if success
  "error": {                 // Present if error
    "code": "ERROR_CODE",
    "message": "Human readable",
    "details": { ... },
    "timestamp": "2026-04-23T14:30:00Z",
    "request_id": "req-uuid"
  },
  "metadata": {
    "request_id": "req-uuid",
    "timestamp": "2026-04-23T14:30:00Z",
    "environment": "test" | "prod",
    "_test_mode": true/false,  // Included if true
    "_mock_reason": "..."      // Included if test_mode
  }
}
```

### Authentication & Headers

```
POST /auth/login
Authorization: None (login endpoint)
Content-Type: application/json

Headers (subsequent authenticated requests):
Authorization: Bearer {session_token}
X-Request-ID: {uuid}
X-Client-Version: 1.0.0
```

### Pagination & Filtering

For list endpoints (claims, audit logs, etc.):

```json
GET /analyst/audit-log?page=1&limit=50&filter=verification_step:cms_npi_verification&sort=-timestamp

Response:
{
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total_records": 1247,
    "total_pages": 25,
    "has_next": true,
    "has_previous": false
  }
}
```

---

## Reading Engine Architecture

The Reading Engine is the component that fetches data from external sources and integrates it with TORQ-e:

```
┌─────────────────────────────────────────────────────────┐
│           Reading Engine (Query Dispatcher)              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Input: Query object                                   │
│  {                                                     │
│    "action": "verify_provider_npi",                    │
│    "npi": "1234567890",                                │
│    "last_name": "Smith",                               │
│    "dob": "1965-05-20"                                 │
│  }                                                     │
│                                                         │
│  Processing:                                           │
│  1. Route to appropriate data source adapter           │
│  2. Execute query (real or mock, based on ENV)         │
│  3. Validate response                                  │
│  4. Log to VERIFICATION_AUDIT_LOG                      │
│  5. Return result                                      │
│                                                         │
│  Output: Result object                                 │
│  {                                                     │
│    "verified": true,                                   │
│    "fingerprint": "npi_smith_1965_05_20",              │
│    "found_in_source": "cms_nppes",                     │
│    "verification_timestamp": "2026-04-23T14:30:00Z"    │
│  }                                                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
           │          │          │          │
           ▼          ▼          ▼          ▼
    ┌───────────┐ ┌────────┐ ┌──────────┐ ┌─────────┐
    │ CMS NPPES │ │ OIG    │ │ State    │ │ IRS/EIN │
    │ Adapter   │ │Exclus  │ │Licensing │ │Lookup   │
    │           │ │ Adapter│ │ Adapter  │ │ Adapter │
    └───────────┘ └────────┘ └──────────┘ └─────────┘
         │            │           │            │
         ▼            ▼           ▼            ▼
    CMS API      OIG Database State DB  IRS Lookup
    (Real)       (Real)        (Real)    (Real)
```

### Data Source Adapters (To Be Implemented)

```python
class ReadingEngine:
    """Main dispatcher"""
    
    def verify_provider_npi(self, npi, last_name, dob, env='test'):
        adapter = CMSNPPESAdapter(env)
        result = adapter.query(npi, last_name, dob)
        self.log_verification('upid', upid, 'cms_npi_verification', result)
        return result
    
    def check_oig_exclusion(self, npi_or_ein, provider_type, env='test'):
        adapter = OIGExclusionAdapter(env)
        result = adapter.query(npi_or_ein, provider_type)
        self.log_verification('upid', upid, 'oig_exclusion_check', result)
        return result
    
    def verify_state_license(self, license_number, state_code, env='test'):
        adapter = StateLicensingAdapter(state_code, env)
        result = adapter.query(license_number)
        self.log_verification('upid', upid, 'state_licensing_check', result)
        return result
    
    def verify_ein(self, ein, business_name, env='test'):
        adapter = IRSEINAdapter(env)
        result = adapter.query(ein, business_name)
        self.log_verification('upid', upid, 'irs_ein_verification', result)
        return result
    
    def run_eligibility_check(self, household_size, monthly_income, citizenship, env='test'):
        algo = NYSMedicaidAlgorithm(env)
        result = algo.check_eligibility(household_size, monthly_income, citizenship)
        self.log_verification('umid', umid, 'eligibility_algorithm', result)
        return result
    
    def log_verification(self, id_type, id_value, step, result):
        """Log all verification events to audit trail"""
        log_entry = VERIFICATION_AUDIT_LOG(
            identifier_type=id_type,
            identifier_id=id_value,
            verification_step=step,
            verification_result='passed' if result['verified'] else 'failed',
            data_checked_against=result.get('source'),
            details=result,
            timestamp=NOW(),
            completed_by_ushi=current_user_ushi  # who initiated check
        )
        db.session.add(log_entry)
        db.session.commit()
```

### Test Mode vs Prod Mode

```python
class CMSNPPESAdapter:
    def __init__(self, env='test'):
        self.env = env
    
    def query(self, npi, last_name, dob):
        if self.env == 'test':
            return self._mock_query(npi, last_name, dob)
        else:
            return self._real_query(npi, last_name, dob)
    
    def _mock_query(self, npi, last_name, dob):
        """Test mode: Return realistic mock data"""
        return {
            'verified': True,
            'npi': npi,
            'name': last_name,
            'dob': dob,
            'specialty': 'Pediatrics',
            'state_license': 'NY123456',
            'license_active': True,
            'source': 'cms_nppes_mock',
            '_test_mode': True
        }
    
    def _real_query(self, npi, last_name, dob):
        """Prod mode: Call real CMS API"""
        # TODO: Implement when CMS API credentials available
        response = requests.get(
            f'https://npiregistry.cms.hhs.gov/api?number={npi}',
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        
        # Validate last_name and dob match
        if data['results'][0]['basic']['last_name'] != last_name:
            return {'verified': False, 'reason': 'Name mismatch'}
        
        return {
            'verified': True,
            'npi': npi,
            'name': data['results'][0]['basic']['last_name'],
            'specialty': data['results'][0]['basic']['sole_proprietor'],
            'source': 'cms_nppes_real'
        }
```

---

## authenticity verification algorithm

### authenticity risk Scoring (0-100 Scale)

```python
class FraudDetectionEngine:
    
    def assess_provider_fraud_risk(self, upid):
        """Calculate authenticity score based on multiple signals"""
        
        provider = db.session.query(UPID_RECORDS).get(upid)
        claims = db.session.query(Claims).filter_by(provider_upid=upid).all()
        
        risk_score = 0
        red_flags = []
        green_flags = []
        
        # Signal 1: Address validation (10 points max)
        if self._is_po_box(provider.primary_address):
            risk_score += 10
            red_flags.append({
                'name': 'PO Box Address',
                'weight': 'high',
                'evidence': provider.primary_address
            })
        else:
            green_flags.append('Physical address verified')
        
        # Signal 2: Billing volume anomaly (20 points max)
        peer_avg_monthly_claims = self._get_peer_average(provider.specialty)
        provider_monthly_claims = self._count_recent_claims(upid, 30)
        
        if provider_monthly_claims > peer_avg_monthly_claims * 2.0:
            risk_score += 20
            red_flags.append({
                'name': 'Billing Volume 2x Typical',
                'weight': 'high',
                'evidence': f'{provider_monthly_claims} vs {peer_avg_monthly_claims} peer avg'
            })
        
        # Signal 3: Duplicate billing detection (15 points max)
        duplicates = self._detect_duplicate_claims(claims)
        duplicate_rate = len(duplicates) / len(claims) if claims else 0
        
        if duplicate_rate > 0.02:  # >2%
            risk_score += 15
            red_flags.append({
                'name': 'Duplicate Billing',
                'weight': 'medium',
                'evidence': f'{duplicate_rate*100:.1f}% of claims appear duplicated'
            })
        
        # Signal 4: Billing outside facility hours (15 points max)
        outside_hours = self._check_billing_hours(provider, claims)
        if outside_hours > len(claims) * 0.10:  # >10% outside hours
            risk_score += 15
            red_flags.append({
                'name': 'Billing Outside Hours',
                'weight': 'medium',
                'evidence': f'{outside_hours} claims outside operating hours'
            })
        
        # Signal 5: Unusual service combinations (10 points max)
        impossible_combos = self._detect_impossible_combos(claims)
        if impossible_combos > 0:
            risk_score += 10 * min(impossible_combos, 1)  # Cap at 10
            red_flags.append({
                'name': 'Unusual Service Combinations',
                'weight': 'medium',
                'evidence': f'{impossible_combos} impossible diagnosis-procedure pairs'
            })
        
        # Signal 6: Claims volume spike (15 points max)
        prior_3mo_avg = self._average_monthly_claims(upid, 90)
        recent_month = self._count_recent_claims(upid, 30)
        
        if prior_3mo_avg > 0 and recent_month > prior_3mo_avg * 4.0:
            risk_score += 15
            red_flags.append({
                'name': 'Claims Volume Spike (300%+)',
                'weight': 'high',
                'evidence': f'{recent_month} vs {prior_3mo_avg} prior avg'
            })
        
        # Signal 7: OIG exclusion status (25 points - automatic fail)
        if provider.oig_exclusion_status == 'excluded':
            risk_score = 100  # Maximum risk
            red_flags.append({
                'name': 'OIG Excluded',
                'weight': 'critical',
                'evidence': 'Provider on OIG exclusion list'
            })
        else:
            green_flags.append('OIG verification passed')
        
        # Normalize to 0-100
        risk_score = min(risk_score, 100)
        
        return {
            'risk_score': risk_score,
            'risk_level': self._risk_level_label(risk_score),
            'red_flags': red_flags,
            'green_flags': green_flags,
            'recommendation': self._get_recommendation(risk_score, red_flags)
        }
    
    def _risk_level_label(self, score):
        if score >= 86: return 'CRITICAL'
        if score >= 61: return 'HIGH'
        if score >= 31: return 'MEDIUM'
        return 'LOW'
    
    def _get_recommendation(self, score, flags):
        if score >= 86:
            return 'FLAG_FOR_IMMEDIATE_INVESTIGATION'
        if score >= 61:
            return 'FLAG_FOR_INVESTIGATION'
        if score >= 31:
            return 'REQUEST_DOCUMENTATION'
        return 'MONITOR'
```

---

## Access Control & Authorization

### Role-Based Access Control (RBAC)

```python
class AuthorizationEngine:
    """Enforce data access control based on user role"""
    
    AUTHORITY_LEVELS = {
        0: 'Super Admin',      # All data, all counties, all operations
        1: 'Admin',            # All data for assigned counties
        2: 'Investigator',     # Claims + inauthenticity data, no operational changes
        3: 'Auditor',          # Read-only, all data
        4: 'Analyst',          # Claims + inauthenticity data for assigned counties
        5: 'View-Only'         # Limited summary dashboard only
    }
    
    def can_access_data(self, user_ushi, data_type, county_fips):
        """Check if user can access data of given type in given county"""
        
        user = db.session.query(USHI_RECORDS).get(user_ushi)
        
        # Super Admin can access everything
        if user.authority_level == 0:
            return True
        
        # Check county authorization
        if county_fips not in user.data_access_scope['counties']:
            return False
        
        # Check data_type authorization
        allowed_types = user.data_access_scope['data_types']
        if data_type not in allowed_types:
            return False
        
        # Check operation authorization
        return user.authority_level <= self._min_level_for_operation(data_type)
    
    def filter_response_by_authorization(self, user_ushi, data):
        """Remove fields user shouldn't see"""
        
        user = db.session.query(USHI_RECORDS).get(user_ushi)
        
        if user.authority_level >= 5:  # View-Only
            # Remove: member SSN, provider address, financial details
            if 'federal_id_hash' in data:
                data['federal_id_hash'] = '[REDACTED]'
        
        if user.authority_level >= 4:  # Analyst
            # Remove: government employee personal info
            pass
        
        return data
```

---

## Performance & Scalability

### Query Optimization

```sql
-- UMID Login (frequently accessed)
CREATE INDEX idx_umid_login 
ON UMID_RECORDS(umid, is_active, verified_at DESC);

-- Legacy ID resolution
CREATE UNIQUE INDEX idx_identifier_legacy_id 
ON IDENTIFIER_MAPPINGS(legacy_id_hash) 
WHERE is_primary = true;

-- Audit log queries
CREATE INDEX idx_audit_log_range 
ON VERIFICATION_AUDIT_LOG(identifier_type, identifier_id, timestamp DESC);

-- OIG exclusion checks (frequent)
CREATE INDEX idx_upid_oig_status 
ON UPID_RECORDS(oig_exclusion_status) 
WHERE is_active = true;
```

### Connection Pooling

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'postgresql://user:pass@db:5432/torque',
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,  # Validate connections
    pool_recycle=3600    # Recycle after 1 hour
)
```

### Caching Strategy (Redis)

```python
class CacheLayer:
    """Redis cache for frequently accessed, slow-changing data"""
    
    def get_plan_network(self, uhwp, cache_ttl=3600):
        cache_key = f'plan_network:{uhwp}'
        
        # Try cache first
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Cache miss: query database
        plan = db.query(WHUP_RECORDS).get(uhwp)
        network = db.query(ProviderNetwork).filter_by(plan_id=uhwp).all()
        
        result = {
            'plan_name': plan.plan_name,
            'providers': [p.to_dict() for p in network]
        }
        
        # Store in cache
        redis_client.setex(cache_key, cache_ttl, json.dumps(result))
        
        return result
    
    def invalidate_on_update(self, uhwp):
        """Clear cache when network changes"""
        redis_client.delete(f'plan_network:{uhwp}')
```

---

## Deployment Architecture

### Multi-Environment Setup

```
┌─────────────────────────────────────────────────────────┐
│                  AWS or State Infrastructure             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐     ┌──────────────┐                 │
│  │  TEST ENV    │     │   PROD ENV   │                 │
│  ├──────────────┤     ├──────────────┤                 │
│  │ app:test     │     │ app:prod     │                 │
│  │ db:test      │     │ db:prod      │                 │
│  │ redis:test   │     │ redis:prod   │                 │
│  │ TORQUE_ENV   │     │ TORQUE_ENV   │                 │
│  │ =test        │     │ =prod        │                 │
│  └──────────────┘     └──────────────┘                 │
│                                                         │
│  Separate secrets per environment                      │
│  Separate database per environment                     │
│  Separate logging per environment                      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

ENV TORQUE_ENV=${TORQUE_ENV:-test}
ENV FLASK_APP=app.py

EXPOSE 8000

CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:8000", "--timeout=30", "app:app"]
```

---

## Monitoring & Observability

### Metrics to Track

```python
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
request_duration = Histogram(
    'torque_request_duration_seconds',
    'Request duration',
    ['endpoint', 'method', 'status']
)

request_count = Counter(
    'torque_requests_total',
    'Total requests',
    ['endpoint', 'method', 'status']
)

# Database metrics
db_query_duration = Histogram(
    'torque_db_query_duration_seconds',
    'Database query duration',
    ['query_type']
)

# authenticity verification metrics
fraud_flags_counter = Counter(
    'torque_fraud_flags_total',
    'Total inauthenticity flags raised',
    ['risk_level']
)

# Verification metrics
verification_success = Counter(
    'torque_verifications_total',
    'Verification events',
    ['verification_step', 'result']
)
```

### Logging Strategy

```python
import logging
import structlog

# Structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Usage
logger.info(
    'member_eligibility_check',
    umid='xyz...',
    household_size=3,
    income=2100,
    eligible=True,
    duration_ms=45
)
```

---

## Security Implementation

### Encryption & Key Management

```python
from cryptography.fernet import Fernet
import hvac

class EncryptionManager:
    """Handle encryption/decryption of PII"""
    
    def __init__(self):
        # Get encryption key from HashiCorp Vault
        client = hvac.Client(url='https://vault.example.com')
        secret = client.secrets.kv.read_secret_version(path='torque/encryption')
        self.key = secret['data']['data']['key'].encode()
        self.cipher = Fernet(self.key)
    
    def encrypt(self, plaintext):
        """Encrypt PII before storing"""
        return self.cipher.encrypt(plaintext.encode())
    
    def decrypt(self, ciphertext):
        """Decrypt PII when needed"""
        return self.cipher.decrypt(ciphertext).decode()
```

### SQL Injection Prevention

```python
# Always use parameterized queries
query = "SELECT * FROM UMID_RECORDS WHERE umid = %s AND is_active = %s"
result = db.execute(query, (umid, True))

# Never concatenate user input
# WRONG: f"SELECT * FROM UMID_RECORDS WHERE umid = '{umid}'"
```

### Authentication & Authorization

```python
from flask_jwt_extended import JWTManager, create_access_token, jwt_required

jwt = JWTManager(app)

@ap