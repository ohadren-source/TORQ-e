# TORQ-e Medicaid Identity Database

## Overview

The TORQ-e database is the persistent store for all five universal identifier systems (UMID, UPID, WHUP, USHI, UBADA) and their mappings to legacy Medicaid identifiers. The design prioritizes identity persistence (identifiers never change despite name/address/ownership changes), audit traceability, and support for fragmented data source integration.

**Design Philosophy:** Use existing identifiers where they exist (MPI for members, provider IDs for providers, government credentials for stakeholders/analysts). Never force data migration. For new entities without existing records, generate new universal IDs through tiered verification.

---

## Core Principles

1. **Identifier Immutability**: Once assigned, a universal ID never changes. All historical data attaches to that identifier.
2. **Verification Traceability**: Every verification event is logged with timestamps, data sources, and pass/fail outcomes.
3. **Encryption**: All PII (SSN, phone, authenticator secrets) stored encrypted at rest.
4. **Legacy Integration**: Support parallel operation with existing systems (EMEDNY, MPI, state licensing boards, CMS databases).
5. **Audit Compliance**: Full audit trail of all record creation, modification, access, and verification events.

---

## Database Design Standards

- **Normalization**: Third Normal Form (3NF) to eliminate data redundancy
- **Primary Keys**: UUIDs (v4) for all universal identifiers; auto-increment for transactional logs
- **Foreign Keys**: Referential integrity enforced at database level
- **Timestamps**: All records include `created_at`, `updated_at`, `verified_at` in UTC
- **Soft Deletes**: Deactivation flags rather than hard deletes to preserve audit trail
- **Encryption**: AES-256 for PII at rest; TLS 1.3 for data in transit
- **Indexing**: Covering indexes on frequently queried paths (identifier lookup, legacy ID mapping, audit log filtering)

---

## Tables

### 1. UMID_RECORDS (Member Identities)

Stores all member-related identity data and verification state.

```
Column Name                     Type              Constraints
─────────────────────────────────────────────────────────────
umid                           UUID              PRIMARY KEY
mpi_id                         VARCHAR(50)       UNIQUE, NULLABLE
federal_id_hash                CHAR(64)          NULLABLE (SHA-256 of SSN)
first_name_encrypted           BYTEA             
last_name_encrypted            BYTEA             
dob_encrypted                  BYTEA             
household_size                 INTEGER           NULLABLE
monthly_income_cents           BIGINT            NULLABLE (encrypted)
citizenship_status             VARCHAR(50)       NULLABLE (citizen, permanent_resident, etc.)
current_employment_status      VARCHAR(50)       NULLABLE
verification_tier              ENUM              (tier_1_digital, tier_2_inperson)
verified_at                    TIMESTAMP         NULLABLE (when verification completed)
tier_1_id_type                 VARCHAR(50)       NULLABLE (drivers_license, passport, state_id)
tier_1_id_number_hash          CHAR(64)          NULLABLE
tier_2_appointment_code        VARCHAR(50)       NULLABLE
2fa_enabled                    BOOLEAN           DEFAULT false
2fa_secret_encrypted           BYTEA             NULLABLE (authenticator secret)
2fa_phone_encrypted            BYTEA             NULLABLE
2fa_backup_codes_encrypted     BYTEA             NULLABLE (JSON array, encrypted)
2fa_verified_at                TIMESTAMP         NULLABLE
is_active                      BOOLEAN           DEFAULT true
preferred_umid_locked          BOOLEAN           DEFAULT false (true when member confirms selection)
preferred_umid_locked_at       TIMESTAMP         NULLABLE
created_at                     TIMESTAMP         DEFAULT NOW()
updated_at                     TIMESTAMP         DEFAULT NOW()
created_by_umid                UUID              NULLABLE (if created via another user)
data_source                    VARCHAR(100)     (legacy_mpi, new_enrollment, recovered, etc.)

INDEXES:
- PRIMARY KEY on umid
- UNIQUE on mpi_id
- INDEX on federal_id_hash (searches by SSN)
- INDEX on verification_tier (filtering for reports)
- INDEX on is_active, verified_at (finding active verified members)
```

**Notes:**
- `mpi_id` maps to existing Medicaid member database when available
- `federal_id_hash` is salted SHA-256 for privacy; never stores plaintext SSN
- PII columns (`first_name`, `last_name`, `dob`, `2fa_phone`) encrypted at rest using application key management
- `preferred_umid_locked` prevents accidental changes after member confirms selection

---

### 2. UPID_RECORDS (Provider Identities)

Stores provider identity, verification status, and credentials.

```
Column Name                     Type              Constraints
─────────────────────────────────────────────────────────────
upid                           UUID              PRIMARY KEY
provider_type                  ENUM              (individual, organization)
npi                            VARCHAR(10)       NULLABLE (individuals only, UNIQUE if present)
ein                            VARCHAR(9)        NULLABLE (organizations only, UNIQUE if present)
first_name_encrypted           BYTEA             NULLABLE (individuals)
last_name_encrypted            BYTEA             
dob_encrypted                  BYTEA             NULLABLE (individuals)
legal_business_name_encrypted  BYTEA             (organizations)
primary_address_encrypted      BYTEA             
state_license_number_encrypted BYTEA             NULLABLE
state_license_state            VARCHAR(2)        NULLABLE
license_verified_at            TIMESTAMP         NULLABLE
verification_tier              ENUM              (tier_1a_npi, tier_1b_ein, tier_2_inperson)
npi_verified_against_cms       BOOLEAN           DEFAULT false (passed NPPES lookup)
npi_verification_timestamp     TIMESTAMP         NULLABLE
ein_verified_against_irs       BOOLEAN           DEFAULT false
ein_verification_timestamp     TIMESTAMP         NULLABLE
oig_exclusion_checked          BOOLEAN           DEFAULT false
oig_exclusion_status           VARCHAR(50)       (not_excluded, excluded)
oig_check_timestamp            TIMESTAMP         NULLABLE
state_licensing_verified       BOOLEAN           DEFAULT false
malpractice_check_completed    BOOLEAN           DEFAULT false
malpractice_findings           TEXT              NULLABLE (encrypted if contains sensitive data)
2fa_enabled                    BOOLEAN           DEFAULT false
2fa_secret_encrypted           BYTEA             NULLABLE
2fa_phone_encrypted            BYTEA             NULLABLE
2fa_verified_at                TIMESTAMP         NULLABLE
is_active                      BOOLEAN           DEFAULT true
preferred_upid_locked          BOOLEAN           DEFAULT false
preferred_upid_locked_at       TIMESTAMP         NULLABLE
claim_suspension_status        VARCHAR(50)       (none, pending_review, suspended)
claim_suspension_reason        TEXT              NULLABLE
created_at                     TIMESTAMP         DEFAULT NOW()
updated_at                     TIMESTAMP         DEFAULT NOW()
verified_at                    TIMESTAMP         NULLABLE
created_by_umid                UUID              NULLABLE
data_source                    VARCHAR(100)      (legacy_medicaid, npi_registry, new_enrollment, etc.)

INDEXES:
- PRIMARY KEY on upid
- UNIQUE on npi (where provider_type = 'individual')
- UNIQUE on ein (where provider_type = 'organization')
- INDEX on is_active, verified_at
- INDEX on oig_exclusion_status
- INDEX on claim_suspension_status
- COMPOSITE INDEX on (provider_type, verification_tier)
```

**Notes:**
- Supports both individual practitioners (NPI-based) and organizations (EIN-based)
- `preferred_upid_locked` prevents duplicate UPID selection if provider has multiple legacy IDs
- `oig_exclusion_checked` ensures excluded providers are blocked from receiving claims
- `claim_suspension_status` allows immediate operational response (halt payments) while investigation continues

---

### 3. WHUP_RECORDS (Plan Identities)

Stores managed care plan metadata and performance metrics.

```
Column Name                     Type              Constraints
─────────────────────────────────────────────────────────────
uhwp                           UUID              PRIMARY KEY
plan_name_encrypted            BYTEA             
parent_ein                     VARCHAR(9)        INDEX
ny_state_plan_id               VARCHAR(50)       UNIQUE
cms_plan_id                    VARCHAR(50)       UNIQUE
plan_type                      ENUM              (hmo, ppo, mltc, prepaid)
network_provider_count         INTEGER           
member_enrollment_count        INTEGER           
service_counties               JSONB             (array of FIPS codes)
hedis_score_latest             NUMERIC(5,2)      NULLABLE
hedis_measurement_year         INTEGER           NULLABLE
cahps_score_latest             NUMERIC(5,2)      NULLABLE
cahps_measurement_year         INTEGER           NULLABLE
network_adequacy_verified      BOOLEAN           DEFAULT false
quality_plan_submission_ready  BOOLEAN           DEFAULT false
is_active                      BOOLEAN           DEFAULT true
created_at                     TIMESTAMP         DEFAULT NOW()
updated_at                     TIMESTAMP         DEFAULT NOW()

INDEXES:
- PRIMARY KEY on uhwp
- UNIQUE on ny_state_plan_id
- UNIQUE on cms_plan_id
- INDEX on parent_ein (bulk lookups by parent organization)
- INDEX on is_active, plan_type
```

**Notes:**
- Plans are pre-existing contracts; no enrollment flow needed
- `service_counties` stored as JSONB for flexible querying
- Performance metrics updated periodically from state reporting systems
- No 2FA or personal verification needed; operational identity only

---

### 4. USHI_RECORDS (Government Stakeholder Identities)

Stores government employee identities with role-based access control.

```
Column Name                     Type              Constraints
─────────────────────────────────────────────────────────────
ushi                           UUID              PRIMARY KEY
gov_employee_id_encrypted      BYTEA             UNIQUE (their existing credential)
first_name_encrypted           BYTEA             
last_name_encrypted            BYTEA             
agency_code                    VARCHAR(20)       (e.g., NYS_DOH, CMS, OIG)
authority_level                INTEGER           CONSTRAINT (0-5)
                                                 0=Super Admin, 1=Admin, 2=Investigator,
                                                 3=Auditor, 4=Analyst, 5=View-Only
data_access_scope              JSONB             {
                                                   "counties": [fips_codes],
                                                   "programs": [medicaid, chip],
                                                   "data_types": [claims, enrollment, quality],
                                                   "read_write": "read" or "read_write"
                                                 }
2fa_enabled                    BOOLEAN           DEFAULT true (mandatory)
2fa_secret_encrypted           BYTEA             
2fa_phone_encrypted            BYTEA             
2fa_verified_at                TIMESTAMP         
annual_reauth_required         BOOLEAN           DEFAULT true
annual_reauth_due              DATE              
last_reauth_completed_at       TIMESTAMP         NULLABLE
is_active                      BOOLEAN           DEFAULT true
created_at                     TIMESTAMP         DEFAULT NOW()
updated_at                     TIMESTAMP         DEFAULT NOW()
last_access_at                 TIMESTAMP         NULLABLE
created_by_ushi                UUID              NULLABLE (who provisioned this account)

INDEXES:
- PRIMARY KEY on ushi
- UNIQUE on gov_employee_id_encrypted
- INDEX on authority_level (filtering by role)
- INDEX on is_active, annual_reauth_due (finding users needing reauth)
- INDEX on agency_code
```

**Notes:**
- Uses existing government employee ID as source of truth (no duplicate IDs created)
- Authority levels map to 6-tier RBAC (Super Admin → View-Only)
- `data_access_scope` enforced at query layer (reading engine only returns data user is authorized for)
- Annual re-authorization required for compliance
- 2FA mandatory (no exception)

---

### 5. UBADA_RECORDS (Analyst Identities)

Stores data analyst and fraud analyst identities with performance tracking.

```
Column Name                     Type              Constraints
─────────────────────────────────────────────────────────────
ubada                          UUID              PRIMARY KEY
analyst_type                   ENUM              (fraud, business, research)
skill_level                    ENUM              (junior, senior, lead)
gov_employee_id_encrypted      BYTEA             UNIQUE
first_name_encrypted           BYTEA             
last_name_encrypted            BYTEA             
certifications                 JSONB             [
                                                   {
                                                     "name": "Fraud Detection Cert",
                                                     "issued_date": "2024-01-15",
                                                     "expiry_date": "2026-01-15",
                                                     "issuer": "CBER"
                                                   }
                                                 ]
2fa_enabled                    BOOLEAN           DEFAULT true (mandatory)
2fa_secret_encrypted           BYTEA             
2fa_phone_encrypted            BYTEA             
2fa_verified_at                TIMESTAMP         
performance_metrics            JSONB             {
                                                   "cases_reviewed_count": 234,
                                                   "fraud_cases_confirmed": 18,
                                                   "false_positive_rate": 0.08,
                                                   "avg_case_resolution_days": 12,
                                                   "fraud_recovery_total_cents": 2450000
                                                 }
is_active                      BOOLEAN           DEFAULT true
created_at                     TIMESTAMP         DEFAULT NOW()
updated_at                     TIMESTAMP         DEFAULT NOW()
last_case_reviewed_at          TIMESTAMP         NULLABLE
created_by_ushi                UUID              NULLABLE

INDEXES:
- PRIMARY KEY on ubada
- UNIQUE on gov_employee_id_encrypted
- INDEX on analyst_type, skill_level
- INDEX on is_active, certifications (finding active certified analysts)
```

**Notes:**
- Maps to existing government analyst credential (no duplicate ID system)
- Certifications tracked with expiry dates for compliance
- Performance metrics used for analyst evaluation and workload balancing
- 2FA mandatory

---

### 6. IDENTIFIER_MAPPINGS (Legacy ID → Universal ID)

Links legacy identifiers to universal identifiers, supporting multiple legacy IDs per entity.

```
Column Name                     Type              Constraints
─────────────────────────────────────────────────────────────
mapping_id                     BIGINT            PRIMARY KEY AUTO_INCREMENT
universal_id_type              ENUM              (umid, upid, uhwp, ushi, ubada)
universal_id                   UUID              FOREIGN KEY (matches appropriate table)
legacy_id_type                 VARCHAR(100)      (medicaid_id, plan_member_id, medicare_id,
                                                  chip_id, npi, ein, state_plan_id, cms_plan_id,
                                                  gov_employee_id, etc.)
legacy_id_value_encrypted      BYTEA             (the actual old ID)
legacy_id_hash                 CHAR(64)          UNIQUE (SHA-256 for deduplication)
is_primary                     BOOLEAN           DEFAULT false (which one is "preferred")
mapping_created_at             TIMESTAMP         DEFAULT NOW()
source_system                  VARCHAR(100)      (mpi, emedny, npi_registry, state_licensing, etc.)
verified                       BOOLEAN           DEFAULT false

INDEXES:
- PRIMARY KEY on mapping_id
- UNIQUE on legacy_id_hash
- COMPOSITE INDEX on (universal_id_type, universal_id)
- INDEX on (legacy_id_type, legacy_id_hash) for legacy system lookups
- INDEX on is_primary (finding active mappings)
```

**Notes:**
- Allows member/provider with multiple legacy IDs to select "preferred" UMID/UPID
- Once `is_primary` locked, prevents accidental switching
- `source_system` tracks which system the legacy ID came from (for validation)

---

### 7. VERIFICATION_AUDIT_LOG (Verification Events)

Complete audit trail of all identity verification, authentication, and authorization events.

```
Column Name                     Type              Constraints
─────────────────────────────────────────────────────────────
log_id                         BIGINT            PRIMARY KEY AUTO_INCREMENT
identifier_type                ENUM              (umid, upid, uhwp, ushi, ubada)
identifier_id                  UUID              
verification_step              VARCHAR(100)      (tier_1_govt_id_check, tier_2_inperson,
                                                  2fa_enrollment, 2fa_login_success,
                                                  2fa_login_failure, cms_npi_verification,
                                                  irs_ein_verification, oig_exclusion_check,
                                                  state_licensing_check, etc.)
verification_result            ENUM              (passed, failed, pending, manual_review)
data_checked_against           VARCHAR(100)      (cms_nppes, irs, state_dmv, state_licensing,
                                                  oig_exclusions, payment_processor, etc.)
details                        TEXT              NULLABLE (encrypted if contains sensitive data)
ip_address_hash                CHAR(64)          NULLABLE (SHA-256 of client IP)
user_agent_hash                CHAR(64)          NULLABLE
timestamp                      TIMESTAMP         DEFAULT NOW()
completed_by_ushi              UUID              NULLABLE (which stakeholder/admin did this)
outcome_action                 VARCHAR(100)      NULLABLE (record_created, record_updated,
                                                  access_granted, access_denied, escalated, etc.)

INDEXES:
- PRIMARY KEY on log_id
- COMPOSITE INDEX on (identifier_type, identifier_id, timestamp)
- INDEX on verification_step (finding all instances of specific check)
- INDEX on timestamp (range queries for reports)
- INDEX on verification_result (finding failures/reviews)
```

**Notes:**
- Immutable append-only log (no updates, only inserts)
- Retention: 7 years minimum (HIPAA compliance)
- Used for compliance audits, security investigations, and fraud detection

---

## Data Access Patterns

### Frequent Queries (Optimized with Indexes)

1. **Member Login**: `SELECT * FROM UMID_RECORDS WHERE umid = ? AND is_active = true`
2. **Provider Verification**: `SELECT * FROM UPID_RECORDS WHERE upid = ? AND verified_at IS NOT NULL`
3. **Plan Lookup**: `SELECT * FROM WHUP_RECORDS WHERE cms_plan_id = ?`
4. **Legacy ID Resolution**: `SELECT universal_id FROM IDENTIFIER_MAPPINGS WHERE legacy_id_hash = ? AND is_primary = true`
5. **Access Control Check**: `SELECT data_access_scope FROM USHI_RECORDS WHERE ushi = ? AND authority_level <= ?`
6. **OIG Exclusion Status**: `SELECT oig_exclusion_status FROM UPID_RECORDS WHERE upid = ?`
7. **Audit Trail**: `SELECT * FROM VERIFICATION_AUDIT_LOG WHERE identifier_type = ? AND identifier_id = ? ORDER BY timestamp DESC LIMIT 100`

---

## Encryption Strategy

### At-Rest Encryption
- **Storage Engine**: PostgreSQL with PGCrypto or envelope encryption
- **Algorithm**: AES-256-CBC
- **Key Management**: Separate master key (in AWS Secrets Manager or HashiCorp Vault)
- **Encrypted Fields**: All PII (names, SSN, phone, addresses, authenticator secrets)
- **Non-Encrypted**: Identifiers (UUIDs, NPI, EIN), system codes, timestamps

### In-Transit Encryption
- **Protocol**: TLS 1.3 for all API endpoints
- **Certificate**: Public CA (not self-signed in production)
- **HSTS**: Enforced (Strict-Transport-Security header)

---

## Backup & Recovery

- **Backup Frequency**: Continuous replication to standby database; daily snapshots
- **Retention**: 30-day rolling retention for point-in-time recovery
- **Recovery RTO**: <15 minutes
- **Recovery RPO**: <5 minutes
- **Testing**: Monthly recovery drill to alternate environment
- **Audit Log Archival**: Annual rotation to cold storage (S3 Glacier)

---

## Performance Considerations

- **Connection Pooling**: PgBouncer or HikariCP (max pool: 50 connections)
- **Query Optimization**: All indexes covering frequent query paths; EXPLAIN ANALYZE on new queries
- **Partitioning**: VERIFICATION_AUDIT_LOG partitioned by month (for retention management)
- **Caching Layer**: Redis for session state (2FA verification tokens, auth cache)
- **Monitoring**: Prometheus metrics on query latency, index hits, connection pool utilization

---

## Migration Strategy

### Phase 1: Shadow Mode (Week 1-2)
- Run TORQ-e in parallel with existing systems
- All writes go to both old and new systems
- No data returned from TORQ-e yet
- Validate data consistency

### Phase 2: Read-Only Pilot (Week 3-4)
- Limited users (100-200) read from TORQ-e
- Still writing to both systems
- Monitor for issues
- Gather feedback

### Phase 3: Full Cutover (Week 5)
- All new identities created in TORQ-e only
- Legacy identifiers mapped to TORQ-e identifiers
- EMEDNY integration live
- Full audit logging enabled

### Phase 4: Decommission (Month 3+)
- Legacy systems remain operational for read-only access during transition period
- Archive legacy data to cold storage
- Final sunset after 6 months (compliance retention period)

---

## Security Matrix

| Data Type | At Rest | In Transit | Access Control | Audit Log |
|-----------|---------|-----------|-----------------|-----------|
| PII (Names, DOB, SSN) | AES-256 | TLS 1.3 | Need-to-know RBAC | All access logged |
| Authenticator Secrets | AES-256 | Never transmitted | User only | Access denied logs only |
| Identifiers (UUID, NPI, EIN) | Plaintext | TLS 1.3 | Role-based | All queries logged |
| Legacy IDs | AES-256 | TLS 1.3 | RBAC + purpose | Mapping queries logged |
| Audit Logs | Plaintext | TLS 1.3 | RBAC, append-only | N/A (immutable) |
| Performance Metrics | Plaintext | TLS 1.3 | RBAC | Modifications logged |

---

## Compliance

- **HIPAA**: Encryption, access controls, audit logs meet BAA requirements
- **PCI-DSS**: N/A (no payment processing; payment processing separate)
- **GDPR**: N/A (US-only system) but principles applied (data minimization, retention limits)
- **FTC Safeguards Rule**: Encryption, monitoring, incident response plan in place
- **State Medicaid Requirements**: Follows NYS DOH IT security policy

---

## Database Maintenance

| Task | Frequency | Owner | Notes |
|------|-----------|-------|-------|
| VACUUM & ANALYZE | Daily (off-peak) | DBaaS automation | Reclaim space, update statistics |
| Index Fragmentation Check | Weekly | DBA | Rebuild if >30% fragmented |
| Backup Verification | Daily | DBA | Restore to test environment |
| Audit Log Retention Check | Monthly | Compliance | Delete logs older than 7 years |
| Capacity Planning | Quarterly | DevOps | Monitor growth, project scaling needs |
| Security Audit | Quarterly | Security | Review access logs, check for anomalies |

---

## Contact & Escalation

- **Schema Questions**: [Architect]
- **Performance Issues**: [DBA]
- **Compliance/Audit**: [Security Officer]
- **Production Incidents**: [On-Call DBA]

