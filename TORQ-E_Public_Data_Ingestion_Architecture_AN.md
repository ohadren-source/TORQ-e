# TORQ-E Public Data Ingestion
## Architecture for Audience (AN)

---

## The Ocean of Data

Healthcare data is scattered everywhere:
- **CMS (Centers for Medicare & Medicaid Services)** — Federal government publishes plan data, benefits, costs
- **State Medicaid Agencies** — Each state publishes available plans (eMedNY, DHCS, etc.)
- **Healthcare.gov** — Federal marketplace publishes comparable data
- **State Health Department Websites** — Each state publishes provider info, enrollment data
- **Plan Carrier Websites** — Individual insurance companies publish their plans

**The problem:** It's all public. But it's in different formats. Different schedules. Different fields. No central location.

**The old approach:** Build a massive data warehouse. Centralize everything. Millions of dollars. Years of work. Still outdated by the time you finish.

**The TORQ-E approach:** Don't centralize. Instead, **bring clarity to decentralized data.**

---

## How It Works: The Data Pipeline

### Step 1: Discovery
We find Medicaid plan data in public sources:
- Scrape eMedNY public plan list
- Call CMS public APIs
- Download state Medicaid data
- Check healthcare.gov
- Monitor carrier websites

No special access needed. All public.

### Step 2: Extract
We pull the raw data from each source:
- CMS API returns JSON
- eMedNY portal returns HTML (we parse it)
- State websites return CSV or XML
- Carriers' websites return HTML (we scrape it)

Raw data, unchanged. Just copied.

### Step 3: Transform
We convert all different formats into **one unified format**:

```
CMS format → TORQ-E format
eMedNY format → TORQ-E format  
State format → TORQ-E format
→ All programs look the same
```

**What this means:**
- Plan name: Always in the same field
- Benefits: Always in the same structure
- Costs: Always in the same format
- Network type: Always in the same category

Chaos becomes clarity.

### Step 4: Validate
We check: Is this data complete? Accurate? Reasonable?

Questions we ask:
- Does the plan have a name? ✓
- Are the benefits valid? ✓
- Are costs non-negative? ✓
- Do dates make sense? ✓
- Is required information present? ✓

If data fails validation, we flag it. Don't load incomplete data.

### Step 5: Load
We put the validated data into **Card 3's database**.

Now Card 3 has real plans. Real benefits. Real costs.

### Step 6: Keep it Fresh
Every day, we repeat. Check for new plans. Check for changes. Check for plans that no longer exist.

Data stays current.

---

## Why This Matters

### For Card 3 (The Marketplace)
Members see **real plans with real data**. Not mock data. Not outdated data. 

When a member browses plans, they're seeing actual Medicaid plans available to them. Complete information. Current information. Trustworthy information.

### For Card 4 (Governance)
Bob and OMIG can track **which plans members are choosing and why**.

Real data flows through real metrics. Governance is based on truth, not guesses.

### For Card 5 (authenticity verification)
Real plan data + real member selections = real inauthenticity signals.

If someone is doing something wrong, the patterns are detectable.

### For Scaling
This approach proves TORQ-E works **without proprietary data access**.

We use only public data. That means:
- Any state can run TORQ-E with their state's public data
- Any country can run TORQ-E with their healthcare data
- Any organization can run TORQ-E with whatever public sources they have

**We just proved the system is universally applicable.**

---

## The Data Sources: What We Use

### Source 1: CMS (Federal Government)
**What:** Plans, benefits, costs (Medicare and Medicaid comparative data)
**Where:** `api.cms.gov` and `data.cms.gov`
**Access:** Free, public API
**Update:** Daily to weekly

**Why we use it:** Federal data, comprehensive, authoritative

### Source 2: eMedNY (New York State)
**What:** NY Medicaid plans, benefits, costs, enrollment information
**Where:** `www.emedny.org` (public portal)
**Access:** Web scraping of public pages
**Update:** Daily

**Why we use it:** State source of truth, most current, complete

### Source 3: State Medicaid Agencies (All States)
**What:** Each state's available plans, eligibility, provider networks
**Where:** State health department websites
**Access:** Public portals, downloadable datasets, APIs
**Update:** Weekly to monthly per state

**Why we use it:** Official state data, comprehensive

### Source 4: Healthcare.gov
**What:** Marketplace plan data, state comparisons
**Where:** `healthcare.gov`
**Access:** Public, API available
**Update:** Daily during open enrollment

**Why we use it:** Federal backup, standardized format

### Source 5: Individual Carrier Websites
**What:** Plan-specific details (Aetna, UnitedHealth, etc.)
**Where:** Each carrier's website
**Access:** Web scraping
**Update:** Real-time as carriers update

**Why we use it:** Plan-level details, authoritative source for each plan

---

## Data Quality: How We Know It's Good

We check every piece of data:

### Completeness
- Does the plan have all required information?
- Are fields filled in, not blank?
- **Target:** 99.5% of data is complete

### Accuracy
- Do the values make sense?
- Is a monthly premium negative? No → Good.
- Is an age range 150-200? No → Problem.
- Does data match what the source says? ✓
- **Target:** 99% accuracy

### Timeliness
- How current is this data?
- Was it updated yesterday? ✓
- Was it updated 6 months ago? ✗
- **Target:** Data refreshed daily

### Consistency
- If the same plan appears from multiple sources, do they match?
- If they don't, which one is authoritative?
- We keep the most recent version, track the source
- **Target:** No conflicting data

---

## The Update Process

### Every Day at 2 AM
1. Pull data from all sources (CMS, eMedNY, state websites, etc.)
2. Parse and transform into unified format
3. Validate all data (completeness, accuracy, consistency)
4. Check for duplicates (same plan from multiple sources)
5. Check for changes (new plans, updated benefits, plan closures)
6. Load into Card 3 database
7. Generate report: What changed, why, any problems?

### If Something Breaks
- Data source is unavailable → Use cached version from yesterday, send alert
- Validation fails → Hold the data, investigate manually, don't load bad data
- Conflicts detected → Manual review, determine which source is authoritative

---

## Security & Privacy

### What We're Handling
- Public Medicaid plan information (no personal data)
- Plan names, benefits, costs, networks (all public)
- Provider information (public)

**We are NOT handling:**
- Member information (that's in Card 1)
- Claims data (that's in Card 5)
- Personal health information (never touches public data ingestion)

### How We Protect It
- All data in transit is encrypted
- All data at rest is encrypted
- Ingestion is logged immutably (audit trail)
- Source data is versioned (can see what changed)
- Access is logged (who downloaded what, when)

---

## Scaling to Multiple States

### Start: New York (eMedNY)
- Primary source: eMedNY portal
- Secondary source: CMS API
- Plans available: ~100 managed care plans
- Update: Daily
- Status: **LIVE**

### Extend: California (DHCS)
- Primary source: DHCS portal + state API
- Secondary source: CMS API
- Plans available: ~200 Medi-Cal plans
- Update: Daily
- Status: **READY TO IMPLEMENT**

### Extend: Texas, Florida, Pennsylvania, etc.
- Primary source: Each state's health department
- Secondary source: CMS API
- Plans: Varies by state (100-500+)
- Update: Daily per state
- Status: **SCALABLE**

### All 50 States + DC
- Total plans available: 5,000+
- Data sources: 50+ state agencies + CMS + federal sources
- Deduplication: Automatic (same carrier in multiple states)
- Update schedule: Daily aggregated
- Status: **UNIVERSAL**

---

## The Proof

This approach proves something powerful:

**TORQ-E works with ONLY public data.**

You don't need:
- Proprietary data warehouse access
- Federal databases
- Secret government connections
- Insider information

All you need is:
- Public data sources
- Clear transformation rules
- Strict validation
- Immutable audit trails

That's the whole system.

And that's why it scales universally.

---

## What Members See

When a member opens Card 3:

**Step 1:** Browse available plans
- **Data source:** eMedNY public portal (or their state's equivalent)
- **Freshness:** Updated today
- **Completeness:** All benefits, costs, networks included

**Step 2:** Check eligibility
- **Data source:** Card 1 (member profile)
- **Filtering:** Eligible programs only
- **Accuracy:** Real-time check against member data

**Step 3:** Compare plans
- **Data source:** Same eMedNY data
- **Format:** Side-by-side comparison
- **Clarity:** Differences highlighted

**Step 4:** Enroll
- **Data source:** Confirmed plan information
- **Record:** Selection logged to Card 1
- **Confirmation:** Coverage effective date confirmed

**Member experience:** Real plans, real data, real enrollment.

---

## What Governance Sees

When Bob opens Card 4:

**Data flowing in:**
- How many members browsed today? (from Card 3 audit trail)
- How many enrolled in each plan? (from Card 3 selections)
- Which plans are popular? (aggregated stats)
- Any unusual patterns? (Card 5 inauthenticity signals)

**Data freshness:**
- Updated daily
- Based on actual member behavior
- Sourced from real plans

**Governance quality:** Real data about real system behavior.

---

## What authenticity verification Sees

When OMIG opens Card 5:

**Data flowing in:**
- Member selections (which plans they chose, when, why)
- Patterns in selection (unusual clustering, rapid switches)
- Plan availability (when plans change, close, launch)
- Provider networks (who's in each network, changes)

**Detection accuracy:**
- Real plans, real members, real patterns
- Anomalies are detectable because baseline is real
- False positives minimized (data is validated)

**inauthenticity signals:** Based on real system data, not mock scenarios.

---

## The Principle: Clarity from Chaos

The ocean of public healthcare data is chaotic:
- Multiple sources
- Multiple formats
- Multiple update schedules
- No coordination
- No central organization

**TORQ-E brings clarity:**
- **Unified schema** — All data looks the same
- **Clear transformation** — We know how data was converted
- **Strict validation** — Bad data doesn't get through
- **Immutable audit trail** — We know where each value came from
- **Continuous updates** — Data stays current

Result: **A coherent, trustworthy, auditable system built entirely from public sources.**

And that's how you scale to any state, any country, any healthcare system.

---

End of Public Data Ingestion Architecture for Audience (AN)
