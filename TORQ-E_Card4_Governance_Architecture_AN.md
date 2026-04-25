# TORQ-E Card 4: System Health & Governance Dashboard
## Architecture for Audience (AN)

**Status:** ✅ LIVE & LOCKED (2026-04-25)
**Version:** 1.0.0 FROZEN  
**QA Status:** All test queries validated ✓
**Deployment:** https://torq-e-production.up.railway.app/chat-card4.html

---

## What is Card 4?

**Card 4 is the control room.** It's where the people managing Medicaid look at the system and ask: "Is everything working? Are we in compliance? Are there problems we need to fix?"

Card 4 serves everyone who needs to understand system health:
- **Bob** (Governance) — Is the system coherent and audit-ready?
- **OMIG Investigator** (Fraud) — What fraud signals are we detecting? Which need escalation?
- **User 3** (Operations) — Are claims processing smoothly? What's our stability across all systems?

**One dashboard. One system. Three ways to look at it.**

---

## The Dashboard: Coherence Level Spectrum

The core of Card 4 is the **Coherence Level Spectrum**—a visual system showing whether your Medicaid operations are "in sync" across every dimension that matters.

**"Coherence" means:** All parts of your system are working together smoothly. When coherence is high, everything aligns. When it drops, something needs attention.

### Three Views of the Same Data

All three views show the same underlying health data. Pick the one that answers your question fastest. **Each metric is clickable** to drill into data sources and calculation logic.

**All sections start collapsed (▶). Click any section header to expand (▼).**

#### **View 1: Coherence Level** (The Single Light)
```
▶ 🎯 Coherence Level  [Click to expand]

[Expanded view:]
         🟢 
        95%
     COHERENT
     
*For detailed data sources and removable 
citations, go to Stability Strength (Equalizer)*
```

**One number. One color.**
- 🟢 **GREEN (90-100%)** = System is coherent, all parts aligned
- 🟡 **YELLOW (70-89%)** = System is wavering, some parts struggling  
- 🔴 **RED (0-69%)** = System is fragmented, urgent action needed

**Fine print note:** Points you to Stability Strength section if you want to see data sources or remove them from your session.

**Use this when:** You need yes/no confidence fast. "Are we healthy?" → Click to expand, see one light.

#### **View 2: Stability Strength (The Equalizer)**

**Six vertical rectangles, one per dimension:**

```
[⚠] ENROLLMENT RATE              87.3%
    ▄▄▄▄▄▄░░ (progress bar)

[✓] CLAIMS PROCESSING             95%
    ▄▄▄▄▄▄▄░ (progress bar)

[✓] DATA QUALITY                  99%
    ▄▄▄▄▄▄▄░ (progress bar)

[✓] AUDIT TRAIL                  100%
    ▄▄▄▄▄▄▄░ (progress bar)

[✓] COMPLIANCE                    98%
    ▄▄▄▄▄▄▄░ (progress bar)

[✓] SYSTEM STABILITY              96%
    ▄▄▄▄▄▄▄░ (progress bar)
```

**Starts collapsed (▶). Click section header to expand (▼) and see all 6 metrics.**

**Layout:** Full-width rectangles stacked vertically for easy scanning
- **Left:** Traffic light (🟢/🟡/🔴)
- **Center:** Metric name + percentage value
- **Right:** Progress bar showing strength
- **Each rectangle is clickable**

**When you click a metric to expand:**
1. **Equalizer visualization** appears (5 bars representing the value strength)
2. **Real data source citations** displayed one per line with ✕ button:
   ```
   eMedNY Portal ✕
   CMS Data ✕
   State DOH ✕
   ```
3. **Session removal:** Click ✕ next to any source → "Are you sure?" confirmation
   - If yes: Source removed from this session only
   - Removed sources won't appear in future expansions (until you refresh/close tab)
4. **Calculation logic** (the exact formula used)
5. **Detailed breakdown** (specific numbers and recent activity)

**Use this when:** You need to know which specific system is struggling AND want to verify the data with full transparency. "Where's the problem and who says so?" → Click any rectangle.

**Session removal is temporary:** When you close the browser or tab, all sources are back. Want to permanently exclude a source? Contact admin directly.

#### **View 3: Combined View** (Both Together)

```
         🟢
        95%
     COHERENT

     System is COHERENT across all dimensions
     
     [⚠] ENROLLMENT RATE              87.3%
     [✓] CLAIMS PROCESSING             95%
     [✓] DATA QUALITY                  99%
     [✓] AUDIT TRAIL                  100%
     [✓] COMPLIANCE                    98%
     [✓] SYSTEM STABILITY              96%
```

**Coherence % at top + all six metrics below (same clickable rectangles)**

**Starts collapsed (▶). Click section header to expand (▼).**

**When you click a metric in Combined View:**
1. Shows **BOTH** traffic light AND equalizer visuals
2. **Real data source citations with session removal** (one URL per line with ✕ button)
   - Click ✕ → "Are you sure?" confirmation
   - Removes from session (temporary, until page refresh)
3. Full calculation logic and detailed breakdown

**Use this when:** You want the complete picture with maximum context. "Show me everything." → Combined view provides all three layers at once.

---

## What Each Dimension Measures

### Enrollment Rate
**The Question:** How many eligible members are actually enrolled in Medicaid?

**What we're tracking:**
- New members added this period
- Members who left (disenrollments)
- Transfers between plans
- Net growth/decline

**Why it matters:** Low enrollment = eligibility problem or communication gap. High volatility = system instability.

**Data comes from:** State Medicaid Database, MCO reporting systems

### Claims Processing  
**The Question:** Are we paying providers on time and smoothly?

**What we're tracking:**
- Claims processed per minute (throughput)
- Average processing time
- Number stuck in queue
- Error rate

**Why it matters:** Slow processing blocks provider payments. High errors mean payment delays and provider frustration.

**Data comes from:** eMedNY claims system, real-time processing logs

### Data Quality
**The Question:** Can we trust our data? Would it pass a CMS audit?

**What we're tracking:**
- Completeness (all required fields filled?)
- Accuracy (does data match reality?)
- Timeliness (how fresh is the data?)
- Cross-source validation (do different systems agree?)

**Why it matters:** Bad data = bad decisions. CMS audits require 95%+ quality.

**Data comes from:** Multi-source validation (State DB, MCO reports, SSA feeds)

### Audit Trail Integrity
**The Question:** Can we prove everything that happened in the system?

**What we're tracking:**
- Log completeness (nothing missing)
- Timestamp validity (all events time-stamped correctly)
- Chain integrity (unbroken sequence)
- Immutability (logs can't be altered)

**Why it matters:** Regulators demand proof. A broken audit trail = compliance failure.

**Data comes from:** Immutable append-only audit log database

### Compliance Status
**The Question:** Are we following all federal and state rules?

**What we're tracking:**
- HIPAA requirements (privacy/security)
- 42 CFR Part 431 (federal Medicaid rules)
- State-specific mandates
- Payment accuracy standards

**Why it matters:** Non-compliance = penalties, loss of federal funding, legal liability.

**Data comes from:** CMS regulatory requirements, state mandate checklists

### System Stability
**The Question:** Is the system reliable and fast?

**What we're tracking:**
- Uptime % (how often is it actually available?)
- Response time (how fast do queries run?)
- Incident-free streak (how long since last outage?)
- Infrastructure health (servers, databases, networks)

**Why it matters:** Downtime blocks all operations. Slow systems make everyone less effective.

**Data comes from:** Infrastructure monitoring, uptime tracking systems

---

## What Each Dimension Means

### Billing Patterns
**What it measures:** Are claims being billed normally?

Example patterns:
- Doctors billing for procedures they don't typically do
- Unusually high billing compared to peers
- Claims at odd times

**Why Bob cares:** Billing anomalies signal fraud or system errors
**Why OMIG cares:** Fraud starts as billing anomalies
**Why User 3 cares:** Billing problems can block payment processing

### Fraud Risk
**What it measures:** What's the overall fraud danger level?

Combines multiple fraud signals:
- Billing anomalies
- Provider deviation from peers
- Suspicious member behavior
- Network patterns (providers clustering with labs, kickback rings)
- Timing anomalies (unusual activity hours)

**Why Bob cares:** High fraud risk means governance failure
**Why OMIG cares:** This is their job—finding fraud
**Why User 3 cares:** Fraud cases can delay payment processing

### Processing Volume
**What it measures:** Are we handling claims at normal speed?

- Claims received per hour
- Claims processed per hour
- Queue depth (how many waiting)
- Processing delays

**Why Bob cares:** Operational efficiency is governance responsibility
**Why OMIG cares:** Processing bottlenecks can hide fraud signals
**Why User 3 cares:** Volume is their primary operational metric

### Compliance Status
**What it measures:** Are we following federal and state rules?

- Audit trail integrity (can we prove what happened?)
- Timeliness (are we meeting payment deadlines?)
- Data accuracy (do records match reality?)
- Documentation completeness

**Why Bob cares:** Compliance is his main job
**Why OMIG cares:** Compliance violations can expose cases
**Why User 3 cares:** Compliance failures block federal funding

### Data Quality
**What it measures:** How trustworthy is our data?

- Missing fields in claims
- Invalid values (negative numbers, future dates)
- Inconsistencies (same claim appears twice differently)
- Source data mismatches (state data doesn't match what we recorded)

**Why Bob cares:** Bad data = audit failure
**Why OMIG cares:** Bad data confuses fraud detection
**Why User 3 cares:** Bad data blocks claims payment

### System Stability
**What it measures:** Is the platform running?

- Uptime percentage
- Response time
- Database health
- Error rates

**Why Bob cares:** Stability is fundamental governance
**Why OMIG cares:** System down = no fraud detection
**Why User 3 cares:** System down = no claims processing

### And More...

The spectrum can show additional dimensions depending on what you're investigating:
- **Payment Status** — Are members being paid correctly?
- **Audit Trail Integrity** — Is the immutable log clean and complete?
- **Network Anomaly** — Are provider/member/lab clusters forming?
- **Medical Necessity** — Are claims legitimate for the diagnosis?
- **Member Access Pattern** — Are members accessing services normally?

**Pick which dimensions matter for your work.** Click to add/remove bars from the spectrum.

---

## A Day in the Life: Three Users, One System

### Bob's Morning (Governance Oversight)

**9:00 AM** — Bob opens Card 4
- Glances at traffic light: 🟢 GREEN
- Takes 10 seconds. Everything healthy.
- Moves on.

**9:15 AM** — Review overnight incidents
- Card 4 shows: "3 incidents recorded between 2-6 AM"
- Clicks to see what happened:
  - Incident 1: Brief processing delay (resolved)
  - Incident 2: Database query slow (root cause found: misconfigured index)
  - Incident 3: One state data sync failed, recovered automatically
- Takes 5 minutes. All normal. All resolved.

**9:30 AM** — Verify CMS readiness
- Clicks **"Compliance Status"** bar
- Sees: ✓ Audit trail complete, ✓ Timeliness met, ✓ Documentation complete
- Federal compliance: 100%
- Takes 3 minutes. Report to CMS: "All systems nominal."

**10:00 AM** — Move on to other work (Card 4 is fine)

---

### OMIG Investigator's Morning (Fraud Investigation)

**9:00 AM** — Scan for fraud flags
- Opens Card 4
- Looks at **"Fraud Risk"** bar: Shows 34% (YELLOW — watch this)
- Clicks to expand: "12 flagged claims in queue"
- Takes 2 minutes to review the list:
  - Claim 1: Provider billing 50% above peer average (HIGH risk)
  - Claim 2: Member accessed same ER 8 times in 2 weeks (MEDIUM risk)
  - Claim 3-5: Provider + lab network cluster detected (MEDIUM risk)
  - Claim 6-12: Billing anomalies (LOW risk)

**9:15 AM** — Decide which cases to investigate
- Top 3 high-risk flags look serious
- Clicks **"Create Investigation Case"** for each:
  - Case 1: Provider overbilling investigation
  - Case 2: Member ER fraud ring
  - Case 3: Provider-lab kickback cluster
- Takes 5 minutes.

**9:30 AM** — Deep dive into top case
- Case 1 (provider overbilling):
  - Views **"Billing Anomaly"** details: Claims 50% above peer group
  - Views **"Evidence Package"**: Last 100 claims, peer comparison, timeline
  - Views **"Provider Network"**: Who does this provider work with?
  - Sees: Provider + 3 specific labs + 15 specific members = suspicious cluster
  - Initial assessment: "This looks like a kickback ring."
- Takes 20 minutes to gather evidence.

**10:00 AM** — Coordinate with other states
- Case 3 shows: Member also has claims in California and Texas
- Clicks **"Request Coordination"** with CA MFCU and TX MFCU
- Message: "Investigating multi-state provider-lab-member network. Can you check your claims for these entities?"
- Takes 5 minutes.

**2:00 PM** — Monitor active cases
- Card 4 shows: 5 cases in progress, 2 awaiting state coordination, 1 ready for referral
- Updates case notes, marks evidence complete on the one ready for prosecution
- Takes 15 minutes.

**5:00 PM** — Prepare prosecution package
- Case that's investigation-complete: Compile final evidence summary
- Includes: Claim timeline, billing deviation analysis, network graph visualization, audit trail
- Exports as PDF for DA (District Attorney)
- Takes 30 minutes.

---

### User 3's Morning (Operations Management)

**8:00 AM** — Check operations status
- Opens Card 4
- Looks at **"Processing Volume"** bar: 📊 71% (normal)
- Looks at **"System Stability"** bar: 🟢 100% uptime
- Takes 2 minutes. Good to go.

**8:15 AM** — Review budget
- Clicks **"Payment Status"** dimension
- Sees:
  - Claims submitted: 245,000
  - Claims paid: 238,000
  - Claims in queue: 7,000
  - Budget spent: $182M of $200M allocation
- Takes 3 minutes. Budget healthy, on track.

**9:00 AM** — Investigate processing delay
- Card 4 shows: Processing time increased 15% overnight
- Clicks to investigate:
  - Volume didn't increase (so not just "more claims")
  - Database response time is normal
  - Error rate went up 3% (aha!)
  - Specific error: "Invalid provider credential in claim header"
  - Root cause: New provider batch uploaded with bad data format
- Takes 10 minutes to diagnose.

**9:20 AM** — Fix and escalate
- Sends message to provider onboarding team: "Fix the credential format in the batch—they're blocking 7,000 claims"
- Requests re-processing of bad claims
- Monitors **"Processing Volume"** bar to confirm resolution
- Takes 5 minutes to request; will verify resolution in 30 minutes.

**11:00 AM** — Routine check-in
- Processing volume back to normal
- Error rate back to baseline
- Back to work.

---

## One System, Three Perspectives

Notice: **Bob, OMIG, and User 3 are all using the same dashboard. The same dimensions. The same data.**

They're not seeing different things. They're *focusing on different things*.

- **Bob focuses on:** Compliance, stability, incidents
- **OMIG focuses on:** Fraud risk, evidence, network anomalies
- **User 3 focuses on:** Volume, budget, operational bottlenecks

But the data is the same. The system is the same. The buttons work the same.

If a junior OMIG analyst wants to see what an experienced OMIG senior sees, they open the same dashboard. They see the same spectrum. They can click the same buttons.

If Bob wants to understand fraud signals, he clicks on **"Fraud Risk"** and learns.

If User 3 needs to understand a compliance issue, they click on **"Compliance Status"** and see what Bob sees.

**One system. Universal functionality. Different uses.**

---

## Core Features: What You Can Do

### View System Spectrum
Click any dimension to expand and understand what's happening.

**Examples:**
- Click "Fraud Risk" → See all flagged claims with risk scores
- Click "Processing Volume" → See queue depth, processing speed, bottlenecks
- Click "Compliance Status" → See audit trail integrity, documentation completeness

### View Incidents
Card 4 automatically logs every problem:
- System outages
- Processing delays
- Data inconsistencies
- Unusual patterns

Click **"Incidents"** to see full history with timestamps and resolutions.

### Create Investigation Cases
If you see something suspicious (high fraud risk, unusual network cluster, billing anomaly), create a case:

1. Click **"New Investigation Case"**
2. Select: Which claim(s)? Which fraud dimension? What's your suspicion?
3. System compiles: Evidence package, peer comparisons, timeline, network visualization
4. You review the pre-compiled evidence
5. You make the call: Investigate further or close as false alarm

### View Evidence Packages
Every investigation case has pre-compiled evidence:
- Claim history (full record of all claims involved)
- Peer comparison (how does this compare to similar providers/members?)
- Timeline visualization (when did events happen?)
- Network graph (who is connected to whom?)
- Audit trail (every change to these records, who made it, when)

Click to expand or collapse sections. Filter by date range.

### Monitor Active Cases
See all investigation cases in progress:
- Which ones are waiting for state coordination?
- Which ones are ready for prosecution?
- Which ones need additional evidence?

Click any case to update notes, add evidence, change status.

### Request Coordination
If a case involves multiple states, request coordination:
- Specify which states
- Specify which entities (providers, members, labs)
- Specify what information you need
- System routes request to appropriate state MFCUs

### Export Prosecution Package
Once investigation is complete:
- Compile final evidence summary
- Export as PDF or document
- Include: allegations, evidence, timeline, supporting documentation
- Ready to send to DA (District Attorney) or federal authorities

---

## How Data Is Displayed

### Option 1: Traffic Light (Simple)
🟢 GREEN / 🟡 YELLOW / 🔴 RED

One indicator. Is the system healthy? Yes/No.

### Option 2: Spectrum Analyzer (Detailed)
Multiple bars, each showing 0-100% signal strength with color coding.

### Option 3: Tabular (Detailed Numbers)
Raw data in table format:
- Dimension name
- Value (0-100 or specific metric)
- Color
- Change from previous hour/day/week
- Threshold

### Option 4: Timeline (Temporal)
How has each dimension changed over time?
- Last hour
- Last 24 hours
- Last 7 days
- Last 30 days

Line graph showing trends.

**Choose the view you want. Switch anytime.**

---

## Data Sources

Card 4 pulls data from:
- **Claims system** — Every claim as it's processed
- **Member database** — Eligibility, enrollment, benefit access
- **Provider credentials** — Who's licensed, what they bill for
- **Audit trail** — Every action in the system, immutable
- **State data source** — Official program and plan information
- **Error logs** — Every system problem, automatically captured

**Everything is live or near-live.** You're not looking at yesterday's data; you're looking at now.

---

## Security & Privacy

### What Data Is Visible
- Aggregated metrics (volume, timing, statistics)
- Pattern information (network clusters, billing deviation)
- Individual claims (when needed for investigation)
- Audit trails (who did what, when)

### What Data Is NOT Visible
- Member names (replaced with hashed IDs)
- Member personal information
- Provider personal information
- Sensitive investigation details (before prosecution)

### Access Control
**Everyone with access to Card 4 can see the same data.** No gatekeeping.

If something is too sensitive to be visible, it's not in Card 4 at all.

### Audit Trail of Audit Trail
Every action you take in Card 4 is logged:
- Who viewed what, when
- Who created which investigation case
- Who exported which prosecution package
- When you exported it
- What you exported

This audit trail is immutable and queryable by oversight agencies.

---

## Immutable Audit Trail

Every action in Card 4 is permanently recorded:

```json
{
  "timestamp": "2026-04-25T09:15:00Z",
  "user_id": "hash(OMIG_investigator_123)",
  "action": "INVESTIGATION_CASE_CREATED",
  "case_id": "case-789",
  "allegations": "Provider overbilling",
  "system": "Card4"
}

{
  "timestamp": "2026-04-25T09:30:00Z",
  "user_id": "hash(OMIG_investigator_123)",
  "action": "EVIDENCE_PACKAGE_VIEWED",
  "case_id": "case-789",
  "evidence_type": "BILLING_ANOMALY",
  "system": "Card4"
}

{
  "timestamp": "2026-04-25T17:45:00Z",
  "user_id": "hash(OMIG_investigator_123)",
  "action": "PROSECUTION_PACKAGE_EXPORTED",
  "case_id": "case-789",
  "exported_to": "DA_Office_File",
  "system": "Card4"
}
```

These records:
- Cannot be modified
- Cannot be deleted
- Are queryable by auditors
- Prove what happened and when

---

## The Principle: Unified, Transparent, Accountable

Card 4 operates on three principles:

1. **Unified System** — One dashboard, one interface, one set of data. No hidden features or gatekeeping.

2. **Transparent** — All signals visible. All data accessible. If something is too sensitive, it doesn't go in the system.

3. **Accountable** — Every action is logged immutably. You can prove who did what, when, and why.

An entry-level operations analyst can use Card 4 the same way Bob uses it. They might focus on different dimensions, but the system is the same.

---

## Getting Started

**First time using Card 4?**

1. Click **"Traffic Light"** view to see overall system health
2. If something's yellow or red, click it to see the spectrum analyzer and understand the dimension
3. Click **"Recent Incidents"** to see what issues the system has detected
4. If you need to investigate something, click **"New Investigation Case"** — the system will guide you

**Experienced user?**

Click **"Full Spectrum"** view and jump straight to the dimensions you care about.

---

**Your feedback matters.** Card 4 is designed for you—Bob, OMIG, User 3, and anyone else managing Medicaid. If something is unclear, slow, confusing, or missing, tell us.

---

End of Card 4 Architecture for Audience (AN)
