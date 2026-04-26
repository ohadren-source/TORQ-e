# Current State Diagnosis: NY DOH Medicaid Update Website

**Analysis Date**: April 24, 2026  
**Analyzed Site**: NYS Department of Health - Medicaid Update  
**Method**: Five-Persona Lens Analysis (TORQ-e User Archetypes)

---

## Executive Summary

The current NY DOH Medicaid Update website is **information-broadcast only**, designed to distribute policy updates to providers. It fails to serve the operational, transactional, and analytical needs of all five TORQ-e user personas. Each persona must navigate to multiple fragmented systems to accomplish their core task.

---

## Analysis by Persona

### 🧢 CHAPEAU 1: UMID (Member) — "Am I eligible for Medicaid?"

**Primary Question Driver**: Am I eligible for Medicaid?

**What The Site Offers**: ❌ NOTHING USEFUL

**User Journey**:
1. Member arrives at NY DOH Medicaid Update homepage
2. Sees "Individuals/Families" navigation link
3. Clicks expecting member services
4. Lands on provider-focused Medicaid Update newsletter
5. Sees 200+ topics in A-Z index: drug names, billing codes, reimbursement rules
6. Realizes they're in wrong place
7. **Abandonment or extensive searching to find NY State of Health**

**Specific Pain Points**:
- Navigation link "Individuals/Families" is misleading (routes to provider content)
- No member eligibility content whatsoever
- A-Z index entirely provider/clinical jargon (no member-friendly language)
- NY State of Health link buried in footer with no context
- Member has no path to answer their primary question

**Diagnosis**: Member has zero touchpoints on this site. Completely mis-routed.

---

### 🧢 CHAPEAU 2: UPID (Provider) — "How do I enroll?" / "How do I submit a claim?"

**Primary Question Drivers**: 
- How do I enroll in Medicaid?
- How do I submit a claim?

**What The Site Offers**: ✅ PARTIALLY (but broken experience)

**User Journey - Enrollment**:
1. Provider lands on Medicaid Update homepage
2. Searches A-Z index for "Provider Enrollment"
3. Finds article reference from 2019
4. Reads outdated article
5. Not sure if process is current
6. Searches again for newer article
7. Frustrated, gives up or calls support hotline

**User Journey - Claim Submission**:
1. Provider needs to submit claim
2. Clicks on "Claims" in A-Z index
3. Gets 15 different article results spanning 20+ years
4. No clear "how to submit" article
5. Eventually finds reference to EMEDNY
6. Leaves this site, goes to EMEDNY

**Specific Pain Points**:
- **Not transactional**: Newsletter, not action portal. Can't submit claims here.
- **Fragmented**: Step-by-step enrollment/claims guidance is archived articles, not a wizard
- **Outdated**: Articles from 2019-2023. Is this current in 2026?
- **No task-oriented flow**: Must search/browse; no "Start Enrollment" button
- **Archive chaos**: 20+ years of articles on same topic; unclear which is current

**Diagnosis**: Provider has theoretical access to information but must invest significant time to find current, actionable guidance. No operational capability on the site itself.

---

### 🧢 CHAPEAU 3: WHUP (Plan Administrator) — "Is this provider in my network?"

**Primary Question Driver**: Is this provider in my network? Out of network?

**What The Site Offers**: ✅ KIND OF (minimal)

**User Journey**:
1. Plan admin needs to verify provider network status
2. Finds "Provider Directory" link on main page
3. Clicks through to "Current Provider Directory"
4. Can search for provider name/NPI
5. Finds provider (or not)
6. **Ends here. Now what?**

**What Plan Admin Actually Needs**:
- ❌ Enrollment data (member counts per provider)
- ❌ Quality metrics (HEDIS, CAHPS by provider)
- ❌ Claims trending (volume, spend, patterns)
- ❌ Network management tools (add/remove providers)
- ❌ Fraud alerts or red flags
- ❌ Performance dashboards

**Specific Pain Points**:
- **One function only**: Can look up if provider exists; can't manage network
- **No data integration**: Provider directory is siloed from everything else
- **No analytics**: Can't see performance, quality, or patterns
- **No operational tools**: Manual management, no bulk operations
- **Fragmented**: Must go elsewhere for enrollment data, quality metrics, claims info

**Diagnosis**: Plan admin has a basic lookup tool but no operational dashboard. Impossible to manage network efficiently or monitor performance from this site.

---

### 🧢 CHAPEAU 4: USHI (Government Stakeholder) — "What's the breakdown of program efficiency?"

**Primary Question Driver**: What's the breakdown of program efficiency?

**What The Site Offers**: ❌ NOTHING

**User Journey**:
1. Stakeholder needs program efficiency analysis (cost, quality, performance)
2. Visits NY DOH Medicaid Update
3. Sees newsletter about policy updates
4. Realizes this is provider-focused, not strategic
5. Goes to... **unknown location**

**What Stakeholder Actually Needs**:
- ❌ CPPM (Cost Per Member Per Month) trending
- ❌ Spending breakdown by service category
- ❌ Quality metrics (HEDIS scores, CAHPS results)
- ❌ Benchmarking vs other states
- ❌ Performance trends and forecasting
- ❌ Member/provider enrollment numbers
- ❌ Program efficiency indicators

**Site Actually Provides**:
- ✅ Policy change announcements ("New rule for Drug X")
- ❌ Nothing else related to efficiency

**Specific Pain Points**:
- **Zero performance data**: Site is not designed for strategic oversight
- **Policy-only**: Discusses rules, not results
- **Fragmented systems**: Data scattered across EMEDNY, Health Data NY, quality reporting portals
- **No dashboard**: Must manually compile data from multiple sources
- **No real-time**: Everything is historical/reported retroactively

**Diagnosis**: Stakeholder has absolutely no access to program efficiency data on this site. Must navigate to 3-4 other systems to piece together efficiency picture.

---

### 🧢 CHAPEAU 5: UBADA (Data Analyst/Fraud Investigator) — "Is this fraud? Is this provider real?"

**Primary Question Drivers**: 
- Is this fraud?
- Is this provider real?

**What The Site Offers**: ✅ INFORMATION ONLY (no tools)

**User Journey - Provider Legitimacy**:
1. Analyst needs to verify if provider is real
2. Finds A-Z index topic "Fraud"
3. Clicks through; gets articles on fraud prevention policy
4. Reads about types of fraud (helpful background)
5. **Can't verify the specific provider**
6. Goes to Provider Directory to check if NPI exists
7. That's it. Provider exists or doesn't exist.

**User Journey - Fraud Pattern Detection**:
1. Analyst needs to detect suspicious billing patterns
2. This site offers **zero pattern analysis capability**
3. No access to claims data
4. No fraud detection algorithms
5. No risk scoring
6. No red flags or alerts

**What Analyst Actually Needs**:
- ❌ Access to claims data for pattern analysis
- ❌ Fraud risk scoring (0-100 scale)
- ❌ Red flag detection (PO Box address, billing volume anomalies, duplicate claims)
- ❌ Unusual service combination detection
- ❌ Claims timeline analysis
- ❌ Provider verification against multiple databases (CMS NPPES, OIG exclusions, state licensing)
- ❌ Real-time alerts

**Site Actually Provides**:
- ✅ Educational articles on fraud types
- ✅ Provider directory (can verify existence)
- ❌ Everything else

**Specific Pain Points**:
- **Information-only**: Reading about fraud, can't detect it
- **No data access**: Can't analyze claims for patterns
- **No tools**: No algorithms, no risk scoring, no alerts
- **Fragmented verification**: Must go to multiple systems to verify provider (CMS NPPES, OIG exclusions, state licensing board)
- **Manual process**: Everything is manual lookup, no automation

**Diagnosis**: Analyst has fraud education but no fraud detection capability. Can verify basic provider existence but can't investigate suspicious patterns or calculate fraud risk.

---

## Cross-Persona Pattern Analysis

### The Fragmentation Problem

| Persona | Current System | What They Need | Must Go To | Extra Friction |
|---------|---|---|---|---|
| UMID | This site | Eligibility check | NY State of Health | Wrong place, must redirect |
| UPID | This site | Enroll/Submit claims | EMEDNY + this site | Split between systems |
| WHUP | This site | Network management | Provider Directory + claims system | Multiple login/access points |
| USHI | This site | Efficiency data | Health Data NY + EMEDNY + quality reports | 3+ separate systems |
| UBADA | This site | Fraud detection | CMS NPPES + OIG + state licensing + claims system | 4+ separate systems |

### Five Key Findings

**1. No Unified Identity**
- Member doesn't have single ID across systems
- Provider could be listed under different NPIs in different systems
- Plan admin sees providers differently than providers see themselves
- Analyst can't link provider identity across verification systems

**2. Information Broadcast, Not Transactional**
- Everything is one-way (DOH → users)
- No enrollment capability (must go elsewhere)
- No claim submission (must go to EMEDNY)
- No verification tools (must go to multiple databases)
- No analytics (must go to separate dashboards)

**3. No Real-Time Data**
- Newsletter format = historical, not current
- Articles archived from 2000-2026 (outdated mixed with new)
- Stakeholders can't see current efficiency
- Analysts can't detect fraud in real-time

**4. Task-Hostile Design**
- A-Z index is exhaustive but user doesn't know what they're looking for
- No "Start Here" flows for common tasks
- No guided workflows for enrollment, claims, verification
- Information overload (200+ topics) instead of task focus

**5. No Operational Capability**
- Members can't check eligibility
- Providers can't submit claims
- Plan admins can't manage networks
- Stakeholders can't access program data
- Analysts can't detect fraud patterns

---

## What This Reveals About the Current Medicaid System

### The Architecture of Fragmentation

```
Currently:
┌─────────────────────────────────────────────────────────┐
│ NY DOH Medicaid Update (Newsletter/Information)          │
│ ├─ Members → NOWHERE (mis-routed)                        │
│ ├─ Providers → EMEDNY (separate system, no link)         │
│ ├─ Plans → Provider Directory (lookup only, no mgmt)     │
│ ├─ Stakeholders → Health Data NY (separate portal)       │
│ └─ Analysts → CMS NPPES + OIG + State Licensing + ...    │
└─────────────────────────────────────────────────────────┘

Problem: Each persona solves their problem using a different system.
         No unified identity. No integrated data. No single source of truth.
         Each system has different update cadence, data formats, access models.
```

### Why This Matters for Fraud

- **Analyst can verify**: Provider NPI exists in CMS
- **Analyst cannot detect**: All claims from that provider in real-time
- **Analyst cannot flag**: Billing volume 2x higher than peers
- **Analyst cannot correlate**: Claims patterns across claims system, provider verification, and eligibility data
- **Result**: Fraud detection is manual, slow, incomplete

### Why This Matters for Members

- **Member cannot verify**: "Am I eligible?"
- **Member cannot see**: What services are covered
- **Member cannot check**: Which providers are in network
- **Member must call**: Support hotline or visit office
- **Result**: Enrollment friction, eligibility confusion, access delays

### Why This Matters for Providers

- **Provider cannot verify**: "Is member eligible right now?"
- **Provider cannot track**: Claim status in real-time
- **Provider cannot understand**: Why claim was denied
- **Provider must call**: Support or manually search multiple systems
- **Result**: Claims processing delays, payment friction, operational overhead

---

## Conclusion: The Case for TORQ-e

Current state = **Information broadcast across fragmented systems**

Needed state = **Unified identity, real-time verification, integrated operations, fraud detection**

**TORQ-e solves this by**:
- ✅ One identity per person (UMID, UPID, WHUP, USHI, UBADA)
- ✅ Real-time data integration (all systems connected)
- ✅ Task-oriented workflows (not information broadcast)
- ✅ Fraud detection tools (pattern analysis + risk scoring)
- ✅ Operational capability (enroll, claim, verify, analyze)
- ✅ Single source of truth (no more fragmented lookups)

---

**Analysis Prepared For**: TORQ-e Project  
**Diagnostic Purpose**: Validate problem statement and justify system redesign  
**Next Step**: Compare proposed TORQ-e architecture against this current-state diagnosis
