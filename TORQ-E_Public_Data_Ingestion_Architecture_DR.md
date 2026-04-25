# TORQ-E Public Data Ingestion Architecture
## Internal Design Repository (DR)

---

## Overview

**The Problem:** Medicaid plan data is scattered across dozens of public sources with no unified format. Each state publishes differently. CMS publishes differently. Healthcare.gov publishes differently. No central warehouse.

**The Solution:** Build a data ingestion pipeline that:
1. Discovers public Medicaid plan data from multiple sources
2. Transforms disparate formats into unified TORQ-E schema
3. Validates completeness and accuracy
4. Loads into Card 3 database
5. Updates continuously as sources change

**The Principle:** TORQ-E brings clarity to chaos. We prove it by organizing the messiest, most fragmented healthcare data (public sources) into a coherent system.

---

## Data Sources: Ocean of Public Information

### Source 1: CMS (Centers for Medicare & Medicaid Services)

**What they publish:**
- Medicare Advantage plan data (public API)
- Medicaid state plan amendments (public documents)
- Plan comparison datasets
- Provider network data

**Access method:**
- **API:** `https://api.cms.gov/` (requires registration, free)
- **Bulk download:** `data.cms.gov` - datasets, data dictionaries
- **Format:** JSON, CSV, XML

**Data available:**
- Plan names, IDs, type (HMO, PPO, FFS)
- Benefits (what's covered, what isn't)
- Cost sharing (premiums, copays, deductibles)
- Network type
- Enrollment periods
- Provider directory URLs

**Update frequency:** Daily to weekly depending on data type

**Coverage:** Federal programs (Medicare), some Medicaid comparative data

---

### Source 2: State Medicaid Agencies (eMedNY for NY example)

**What they publish:**
- Available plans in state (public before login)
- Plan details, benefits, costs
- Eligibility criteria
- Enrollment deadlines
- Provider network information

**Access method:**
- **Public portal:** `www.emedny.org` (NY example)
- **Web scraping:** Available plans are HTML/JavaScript-rendered
- **State data downloads:** Some states publish CSV/XML exports
- **SFTP/API:** Some states provide direct data feeds (requires request)

**Data available:**
- Complete plan catalog with all fields
- Eligibility rules
- Benefits matrices
- Cost structures
- Network provider directories
- Enrollment periods

**Update frequency:** Weekly to monthly (when plans change)

**Coverage:** NY Medicaid plans (and equivalent in each state)

---

### Source 3: Healthcare.gov

**What they publish:**
- Marketplace plan data (ACA/individual insurance, not Medicaid directly)
- Some state Medicaid comparison tools
- APIs for plan searches

**Access method:**
- **API:** `https://api.healthcare.gov/` (public)
- **Web scraping:** marketplace.cms.gov
- **Dataset downloads:** Some states' data available

**Data available:**
- Plan comparisons
- Benefits information
- Cost calculators
- Provider networks

**Update frequency:** Daily during open enrollment, less frequently otherwise

**Coverage:** Federal marketplace (supplementary, not primary Medicaid source)

---

### Source 4: State Data Repositories

**What they publish:**
- Health department websites (each state has one)
- Public datasets on Medicaid plans, enrollment, outcomes
- Provider licensing and credentials
- Claims statistics (de-identified)

**Access method:**
- **State websites:** Direct download or API access
- **National repositories:** StateData.info, DataPortals
- **SFTP:** Direct request to state agency

**Data available:**
- Medicaid program information
- Plan details
- Provider data
- Enrollment statistics
- Claims patterns (de-identified)

**Update frequency:** Varies by state (weekly to quarterly)

**Coverage:** All 50 states + DC

---

### Source 5: Plan Websites (Direct Scraping)

**What they publish:**
- Plan details on carrier websites (Aetna, UnitedHealth, etc.)
- Benefits, costs, network information
- Provider directories

**Access method:**
- **Web scraping:** Individual plan carrier websites
- **Robots.txt compliance:** Verify allowed scraping
- **User-Agent:** Identify as bot, respect rate limits

**Data available:**
- Plan-specific details
- Carrier-specific benefits
- Network provider lists
- Contact information

**Update frequency:** Real-time (as websites update)

**Coverage:** Individual carrier information

---

## Data Ingestion Pipeline

### Architecture: ETL (Extract, Transform, Load)

```
┌─────────────────────────────────────────────────────────────────┐
│ PUBLIC DATA SOURCES (Multiple Formats, Multiple Schedules)     │
├─────────────────────────────────────────────────────────────────┤
│  CMS API  │  eMedNY Portal  │  State Websites  │  Healthcare.gov │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ EXTRACT LAYER (Data Connectors)                                │
├─────────────────────────────────────────────────────────────────┤
│  API Clients  │  Web Scrapers  │  CSV Readers  │  SFTP Downloaders│
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ RAW DATA STAGING AREA (PostgreSQL temp_ingestion_stage)        │
├─────────────────────────────────────────────────────────────────┤
│  Raw data from each source, unchanged, with source metadata    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ TRANSFORM LAYER (Data Normalization)                           │
├─────────────────────────────────────────────────────────────────┤
│  - Map source fields to TORQ-E Program schema                  │
│  - Normalize data types (dates, costs, boolean flags)          │
│  - Handle missing fields with defaults                         │
│  - Deduplicate identical plans from multiple sources           │
│  - Validate data completeness and accuracy                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ VALIDATION LAYER (Quality Control)                             │
├─────────────────────────────────────────────────────────────────┤
│  - Required fields present (name, state, benefits, costs)?     │
│  - Data types correct (dates are dates, numbers are numbers)? │
│  - Cost values reasonable (premium not negative)?              │
│  - Benefits valid (matches known benefit codes)?               │
│  - Coverage dates logical (start < end)?                       │
│  - Raise errors for data quality issues                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ LOAD LAYER (Update Programs Table)                             │
├─────────────────────────────────────────────────────────────────┤
│  - INSERT new programs                                         │
│  - UPDATE existing programs (if data changed)                  │
│  - ARCHIVE programs no longer available                        │
│  - Log all changes in audit trail                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ CARD 3 PROGRAMS TABLE (Source of Truth)                        │
├─────────────────────────────────────────────────────────────────┤
│  Real Medicaid plans with complete, validated data             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation: Data Connectors

### Connector 1: CMS API Client

```javascript
// Extract from CMS API
class CMSConnector {
  async fetchMedicaidPlans(state) {
    // Call CMS API
    // Returns: plan data in CMS format
  }

  async fetchBenefitsMatrix(state) {
    // Call CMS API
    // Returns: benefits for each plan
  }

  async fetchNetworkData(planId) {
    // Call CMS API
    // Returns: provider network for plan
  }
}

// Transform CMS format to TORQ-E format
function transformCMSData(cmsProgram) {
  return {
    name: cmsProgram.plan_name,
    type: cmsProgram.plan_type, // Map to enum
    state: cmsProgram.state_code,
    eligibility_criteria: {
      age_min: 0,
      age_max: 120,
      income_limit: cmsProgram.income_threshold,
      citizenship_required: true,
      disability_status_required: false,
      special_conditions: cmsProgram.special_conditions || []
    },
    benefits: transformBenefits(cmsProgram.benefits),
    cost_sharing: {
      member_premium_monthly: cmsProgram.monthly_premium || 0,
      copay_primary: cmsProgram.copay_pcp || 0,
      copay_specialist: cmsProgram.copay_specialist || 0,
      copay_emergency: cmsProgram.copay_emergency || 0,
      deductible: cmsProgram.deductible || 0
    },
    network_type: cmsProgram.network_type, // HMO, PPO, FFS
    provider_directory_url: cmsProgram.directory_url,
    coverage_start_date: cmsProgram.effective_date,
    coverage_end_date: cmsProgram.termination_date || null,
    contact_info: {
      phone: cmsProgram.customer_service_phone,
      website: cmsProgram.website,
      support_hours: cmsProgram.service_hours || 'N/A'
    },
    enrollment_deadline: cmsProgram.enrollment_deadline,
    status: cmsProgram.is_active ? 'ACTIVE' : 'ARCHIVED'
  };
}
```

### Connector 2: eMedNY Web Scraper

```javascript
// Extract from eMedNY public portal
class EMedNYScraper {
  async scrapeAvailablePlans(state = 'NY') {
    // Navigate to eMedNY public plan list
    // Parse HTML/JavaScript-rendered content
    // Extract plan data
    // Returns: raw plan data from eMedNY
  }

  async scrapePlanDetails(planId) {
    // Scrape individual plan detail page
    // Extract benefits, costs, network info
    // Returns: detailed plan data
  }
}

// Transform eMedNY HTML to TORQ-E format
function transformEMedNYData(emednyProgram) {
  return {
    name: emednyProgram.plan_name,
    type: parseType(emednyProgram.plan_category),
    state: 'NY',
    eligibility_criteria: parseEligibility(emednyProgram.eligibility_text),
    benefits: parseBenefits(emednyProgram.benefits_html),
    cost_sharing: parseCosts(emednyProgram.cost_section),
    network_type: parseNetworkType(emednyProgram.network_description),
    provider_directory_url: emednyProgram.directory_link,
    coverage_start_date: parseDate(emednyProgram.start_date),
    coverage_end_date: parseDate(emednyProgram.end_date) || null,
    contact_info: {
      phone: emednyProgram.phone_number,
      website: emednyProgram.plan_website,
      support_hours: emednyProgram.hours || 'N/A'
    },
    enrollment_deadline: parseDate(emednyProgram.deadline),
    status: emednyProgram.is_available ? 'ACTIVE' : 'CLOSED'
  };
}
```

### Connector 3: State Data API

```javascript
// Extract from state health department APIs
class StateDataConnector {
  async fetchStateMedicaidPlans(state) {
    // Call state-specific API (varies per state)
    // Most states have REST API or SFTP access
    // Returns: plans available in that state
  }
}

// Transform state data to TORQ-E format
function transformStateData(stateProgram) {
  // Similar to above - map source fields to TORQ-E schema
}
```

---

## Validation Rules

Every program must pass validation before loading:

### Required Fields
- `name` (string, not null)
- `type` (enum: MEDICAID, MANAGED_CARE, SPECIAL_NEEDS, DUAL_ELIGIBLE)
- `state` (valid US state code)
- `eligibility_criteria` (JSONB, must have age_min, age_max, income_limit)
- `benefits` (JSONB, must have at least one benefit = true)
- `cost_sharing` (JSONB, must have all copay fields >= 0)
- `network_type` (enum: HMO, PPO, FFS, CAPITATED)
- `coverage_start_date` (valid date)
- `status` (enum: ACTIVE, PENDING, CLOSED, ARCHIVED)

### Data Quality Rules
- `age_min` >= 0 and < `age_max`
- `income_limit` > 0
- `copay_primary` >= 0
- `copay_specialist` >= 0
- `copay_emergency` >= 0
- `deductible` >= 0
- `member_premium_monthly` >= 0
- `coverage_start_date` <= `coverage_end_date` (if end_date exists)
- `enrollment_deadline` is in the future (or null)

### Deduplication
- If same plan appears from multiple sources, keep the most recently updated version
- Log which source was authoritative

---

## Update Schedule

### Continuous Updates
- CMS API: Daily check for changes
- eMedNY portal: Daily scrape for changes
- State APIs: Daily or per state schedule
- Plan websites: Weekly scrape

### Trigger Updates
- Enrollment deadline approaching: Flag plans
- Plan status change: Update immediately
- New plan added: Load immediately
- Plan terminated: Archive immediately

### Batch Schedule
- Full validation run: Nightly at 2 AM ET
- Deduplication: After each source update
- Archive check: Weekly (find plans no longer available)
- Report: Daily summary of changes

---

## Error Handling

### Soft Failures (Retry)
- API timeout: Retry 3 times with exponential backoff
- Network error: Retry next scheduled run
- Partial data missing: Load what we have, flag for manual review

### Hard Failures (Alert)
- Source completely unavailable: Send alert, investigate
- Validation fails for >10% of data: Hold load, investigate
- Data quality score drops: Alert governance team
- Duplicate plan detection conflict: Manual review required

---

## Data Lineage & Audit Trail

Every program record tracks:
- Which source it came from (CMS, eMedNY, state API, etc.)
- When it was ingested
- What was transformed
- Validation results
- Any errors during processing

```json
{
  "program_id": "prog-12345",
  "ingestion_log": [
    {
      "timestamp": "2026-04-25T02:00:00Z",
      "action": "INGESTED",
      "source": "EMEDNY_SCRAPER",
      "raw_data_hash": "sha256-abc123...",
      "validation_result": "PASSED",
      "fields_mapped": 23,
      "fields_missing": 0
    },
    {
      "timestamp": "2026-04-25T02:15:00Z",
      "action": "UPDATED",
      "source": "CMS_API",
      "changed_fields": ["cost_sharing.copay_specialist"],
      "old_value": 25,
      "new_value": 30,
      "validation_result": "PASSED"
    }
  ]
}
```

---

## Scaling: Multiple States

### NY Medicaid
- Primary source: eMedNY portal
- Backup: CMS API
- Update: Daily

### CA Medicaid
- Primary source: DHCS portal + state API
- Backup: CMS API
- Update: Daily

### TX Medicaid
- Primary source: Texas Health & Human Services
- Backup: State API
- Update: Weekly

### All States
- Fallback: CMS comparative data
- Manual addition: Programs not auto-discovered

---

## Data Quality Metrics

Monitor and report:
- **Completeness:** What % of required fields are populated?
- **Accuracy:** Do values match source of truth?
- **Timeliness:** How current is the data?
- **Consistency:** Are duplicate plans properly deduplicated?
- **Validity:** Do values pass validation rules?

Target: 99.5% completeness, 99% accuracy

---

## Security & Privacy

### Data Handling
- Public data only (no PII)
- Immutable ingestion logs (audit trail)
- Version control for transformations
- Encryption in transit (HTTPS)

### Source Authentication
- API keys stored in secure vault
- Rate limiting respected
- User-Agent headers identify scraper
- Robots.txt compliance

---

## Performance Considerations

- Parallel processing: Ingest from multiple sources simultaneously
- Batch inserts: Group updates to minimize database load
- Caching: Cache source data for 1 hour to reduce API calls
- Indexing: Fast lookups by state, type, status

---

## Future Enhancements

1. **Machine Learning** — Detect data quality issues automatically
2. **Provider Network Ingestion** — Ingest and organize provider directories
3. **Claims Data** — Integrate de-identified claims for fraud detection (Card 5)
4. **Real-time Updates** — WebSocket feeds for immediate plan changes
5. **International Healthcare** — Extend to other countries' health systems

---

## The Principle

This pipeline proves the core TORQ-E principle: **You can bring clarity to chaos.**

An ocean of fragmented public data. Multiple sources. Multiple formats. Multiple update schedules.

But with a unified schema, consistent transformation, strict validation, and immutable audit trails—that chaos becomes a coherent, trustworthy, auditable system.

No proprietary data warehouse needed. Just public data + clear principles.

---

End of Public Data Ingestion Architecture (DR)
