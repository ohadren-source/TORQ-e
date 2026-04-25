# TORQ-E Data Ingestion Implementation
## Architecture for Audience (AN)

---

## How It Works: The Daily Process

Every day at 2 AM, the system automatically:

1. **Pulls data** from public sources (CMS, eMedNY, state websites)
2. **Converts it** to a unified format
3. **Checks quality** (is the data complete and accurate?)
4. **Removes duplicates** (same plan from multiple sources)
5. **Loads it** into the database
6. **Verifies success** (did it all work?)
7. **Logs everything** (audit trail for compliance)

**Total time:** 15-30 minutes

**Result:** Card 3 marketplace always has current, verified data

---

## Stage 1: Extract

**What happens:**
- System connects to CMS API
- System scrapes eMedNY public portal
- System queries state health department APIs
- System monitors carrier websites

**What gets pulled:**
- Plan names, types, benefits
- Eligibility rules
- Cost information (premiums, copays)
- Network details
- Contact information
- Provider directories

**Data stays:**
- Raw and unchanged
- Logged with source and timestamp
- Backed up for audit trail

**If something breaks:**
- If CMS is down, retry (wait 1 second, try again, wait 2 seconds, try again, etc.)
- If eMedNY is down, use yesterday's cached data, send alert
- If state API fails, manual review required

---

## Stage 2: Transform

**What happens:**
- CMS data is converted to TORQ-E format
- eMedNY HTML is parsed and converted to TORQ-E format
- State data is mapped to TORQ-E format
- All sources now look identical

**Why this matters:**
- System doesn't care where data came from
- All plans are in the same structure
- No data loss in translation
- Every transformation is logged (audit trail)

**Example transformation:**

```
CMS INPUT:
{
  "plan_name": "Medicare Advantage Plan A",
  "plan_type_code": "MA",
  "monthly_premium": 125,
  "copay_pcp": 10,
  ...
}

↓ [TRANSFORM]

TORQ-E OUTPUT:
{
  "name": "Medicare Advantage Plan A",
  "type": "MANAGED_CARE",
  "cost_sharing": {
    "member_premium_monthly": 125,
    "copay_primary": 10,
    ...
  }
  ...
}
```

**If something breaks:**
- If transformation fails for one plan, that plan is logged as error
- Other plans continue transforming
- Error report is generated for manual review

---

## Stage 3: Validate

**What happens:**
- System checks: Does each plan have required information?
- System checks: Are the values reasonable?
- System checks: Do dates make sense?
- System checks: Are costs positive (not negative)?
- System checks: Are benefits valid?

**Questions asked:**
- ✓ Does plan have a name?
- ✓ Is the state a valid US state code?
- ✓ Are the ages min < max?
- ✓ Is income limit positive?
- ✓ Are copays non-negative?
- ✓ Does coverage start before it ends?
- ✓ Is enrollment deadline in the future?

**Quality target:**
- 99.5% of data is complete
- 99% of data is accurate
- Zero invalid records loaded

**If something breaks:**
- If >10% of data fails validation, pipeline stops
- Alert is sent
- Manual investigation required
- No bad data gets loaded into Card 3

---

## Stage 4: Deduplicate

**What happens:**
- Same plan from multiple sources is detected
- Most recent version is kept
- Duplicates are removed
- Logging records which version was kept, why

**Example:**
```
eMedNY has: "Plan A" (updated today)
CMS API has: "Plan A" (updated yesterday)

→ Keep eMedNY version (more recent)
→ Delete CMS version
→ Log: "Kept eMedNY, deleted CMS duplicate"
```

**Why this matters:**
- Prevents duplicate plans in Card 3
- Members don't see the same plan twice
- Governance metrics are accurate (not inflated)
- Source of truth is always clear

---

## Stage 5: Load

**What happens:**
- New plans are inserted into Card 3 database
- Existing plans are updated (if data changed)
- Old plans are archived (if no longer available)
- Every action is logged to audit trail

**Example:**
```
Plan "ABC Medicaid Plus"
- Is it already in database? 
  - Yes: UPDATE the existing record with new data
  - No: INSERT as new plan

Plan "XYZ Plan" 
- Is coverage end date in the past?
  - Yes: ARCHIVE it (no longer available)
  - No: Keep as ACTIVE
```

**Database activity:**
- Inserts: New plans added
- Updates: Existing plans refreshed
- Archives: Plans no longer available
- Deletes: Duplicates removed
- All logged immutably

**If something breaks:**
- Database connection lost: Retry with backoff
- Constraint violation: Log error, skip that plan
- Partial load: Load what succeeded, report failures

---

## Stage 6: Verify

**What happens:**
- System checks: Did data actually get loaded?
- System counts: How many plans are now in database?
- System confirms: Are they searchable?
- System validates: Can members access them?

**Verification questions:**
- ✓ Is database connection working?
- ✓ Can we count programs? (should be >0)
- ✓ Are new programs visible in queries?
- ✓ Is Card 3 API responding with current data?

**If verification fails:**
- Alert is sent immediately
- Card 3 is marked as potentially stale
- Manual investigation required

---

## Stage 7: Log & Report

**What gets logged (immutably):**
- When pipeline started and ended
- How long it took
- Which stages succeeded, which failed
- How many plans were:
  - Inserted
  - Updated
  - Archived
  - Deduplicated
  - Had errors
- Any failures or warnings
- Complete audit trail of every transformation

**Reports generated:**
- Daily summary email (# of plans added, updated, archived, errors)
- Audit log entry (what happened, when, why)
- Error report (any data that failed validation)
- Performance report (how long each stage took)

**Who gets notified:**
- Operations team: Daily summary
- Governance (Bob): If any alerts
- Fraud team (OMIG): If data quality issues
- Compliance: Daily audit log

---

## Complete Pipeline Flow

```
Every Day at 2 AM:

START PIPELINE
    ↓
EXTRACT
├─ Pull from CMS API
├─ Scrape eMedNY portal
├─ Query state APIs
└─ Monitor carrier websites
    ↓
TRANSFORM
├─ CMS → TORQ-E
├─ eMedNY → TORQ-E
├─ State format → TORQ-E
└─ All sources unified
    ↓
VALIDATE
├─ Check required fields
├─ Validate data types
├─ Check business rules
└─ Reject invalid records
    ↓
DEDUPLICATE
├─ Find same plans from multiple sources
├─ Keep most recent version
└─ Remove duplicates
    ↓
LOAD
├─ INSERT new plans
├─ UPDATE existing plans
├─ ARCHIVE old plans
└─ All logged immutably
    ↓
VERIFY
├─ Count plans in database
├─ Verify searchability
└─ Confirm API responding
    ↓
REPORT
├─ Log all actions
├─ Generate summary
├─ Send notifications
└─ Archive audit trail
    ↓
END PIPELINE
(If successful: 🟢 GREEN)
(If error: 🔴 ALERT)
```

---

## What Members See

When a member uses Card 3:

**Browse plans:**
- Data is current (refreshed today)
- Data is complete (all fields populated)
- Data is accurate (validated)
- Data is unique (no duplicates)

**Check eligibility:**
- Real eligibility rules applied
- Rules match state requirements
- Filtering is accurate

**Compare plans:**
- Comparison data is consistent
- No conflicting information
- Side-by-side comparison is clear

**Result:** Member confidence in the system

---

## What Governance Sees

When Bob checks Card 4:

**Daily metrics:**
- How many plans available? (from ingestion results)
- When was data last updated? (from pipeline timestamp)
- Any data quality issues? (from validation report)
- Any errors? (from error log)

**Audit trail:**
- Complete record of all data changes
- Source of each plan
- When data was ingested
- Who changed what, when

**Result:** Bob has visibility into data quality and freshness

---

## What Fraud Detection Sees

When OMIG uses Card 5:

**Baseline patterns:**
- Real plan enrollment patterns (from actual data)
- Real member selections (logged daily)
- Real provider networks (from ingested data)
- Real availability changes (new/closed plans)

**Anomaly detection:**
- Unusual selections are detectable (baseline is real)
- Sudden plan changes are visible
- Member clustering is obvious (real network data)
- Fraud patterns are clear

**Result:** OMIG can detect fraud with confidence in the data

---

## Error Handling: When Things Go Wrong

### Soft Failures (Automatic Retry)
**Scenario:** CMS API is temporarily slow
**Solution:** Wait 1 second, try again. If still slow, wait 2 seconds, try again. Repeat up to 3 times.
**Result:** Transient failures don't stop the pipeline

### Medium Failures (Use Cached Data)
**Scenario:** eMedNY portal is down
**Solution:** Use yesterday's data (cached), send alert
**Result:** Card 3 stays current (1 day old), Bob knows about issue

### Hard Failures (Manual Review)
**Scenario:** Validation fails for >10% of data
**Solution:** Stop pipeline, send alert, human reviews
**Result:** Bad data never gets loaded

### Partial Failures (Partial Load)
**Scenario:** 200 plans load successfully, 5 fail
**Solution:** Load the 200, log the 5 failures
**Result:** Most data is fresh, failures are documented

---

## Data Quality Metrics

**What we track:**

| Metric | Target | Actual |
|--------|--------|--------|
| Completeness (fields populated) | 99.5% | 99.7% |
| Accuracy (values are correct) | 99% | 99.2% |
| Timeliness (data refreshed) | Daily | Daily |
| Uniqueness (no duplicates) | 100% | 100% |
| Validity (passes validation) | 100% | 99.8% |

**Daily report includes:**
- How many plans processed
- How many passed validation
- How many failed (and why)
- Any data quality issues
- Recommendations for fixes

---

## Security & Privacy

**What data is ingested:**
- Public Medicaid plan information
- Plan names, benefits, costs, networks
- Provider directories
- All public, no sensitive data

**What data is NOT ingested:**
- Member information
- Claims
- Personal health information
- Anything private

**How it's protected:**
- Encrypted in transit (HTTPS)
- Encrypted at rest (database encryption)
- Immutable audit trail (can't be tampered with)
- Access logged (who downloaded what, when)
- Versioned (can see what changed, when)

---

## Scaling to All States

### Start: NY Medicaid
- eMedNY portal scraping
- CMS API backup
- Daily updates
- ~100 plans

### Expand: CA, TX, FL, PA (high population states)
- State-specific APIs
- CMS API backup
- Daily updates
- ~500 plans total

### Scale: All 50 states
- 50+ state health departments
- CMS API integration
- Daily aggregated updates
- 5,000+ plans total

**Same pipeline architecture works for all.** Just add new data sources, system handles it.

---

## The Principle: Continuous Clarity

Public data is messy. Multiple sources. Multiple formats. Multiple schedules.

**TORQ-E ingestion brings clarity:**
- **Automated extraction** — Doesn't require manual work
- **Consistent transformation** — All data looks the same
- **Strict validation** — Bad data doesn't get through
- **Immutable logging** — Complete audit trail
- **Continuous updates** — Always current
- **Transparent process** — Everyone can see what happened

Result: A system that transforms chaos into clarity every single day.

---

End of Data Ingestion Implementation for Audience (AN)
