# TORQ-E Card 5: Fraud Detection & Investigation
## Architecture for Audience (AN)

---

## What is Card 5?

**Card 5 is the fraud hunter.** It continuously scans Medicaid claims for suspicious patterns and helps investigators build prosecution-ready cases.

Card 5 does two things:

1. **Automated Detection** — Real-time scanning of every claim for fraud signals
2. **Investigation Support** — Evidence compilation, network visualization, case management

All investigators use the same system. Entry-level analyst. Experienced senior. Same tools, same data, same interface.

---

## How Fraud Gets Flagged

### The Five Fraud Dimensions

When a claim arrives, Card 5 analyzes it against five fraud indicators:

#### 1. Billing Anomaly
**The question:** Is this claim cost normal for this service?

**How it works:** Compare the claim amount to:
- The same procedure's average cost
- This member's history with this service
- This provider's typical billing

**Example:** 
- Normal CT scan: $1,200
- This CT scan: $4,800
- Flag: 400% above baseline → **HIGH RISK**

**What it catches:** Overbilling, phantom procedures, upcoding (billing for more expensive procedure than done)

#### 2. Provider Deviation
**The question:** Is this provider billing differently than their peers?

**How it works:** Compare this provider's overall billing to:
- Peer providers in same specialty
- Geographic average for same procedure
- National baseline

**Example:**
- Peer orthopedic surgeons average: 2.5 surgeries/month
- This provider: 12 surgeries/month
- Statistical deviation: 4.2 standard deviations from mean → **HIGH RISK**

**What it catches:** Unnecessary procedures, provider kickback rings, fraudulent licensing (someone billing under fake credentials)

#### 3. Member Cycling
**The question:** Is this member accessing services unusually often?

**How it works:** Compare this member's service usage to:
- Others with same diagnosis
- Frequency norms for the condition
- This member's own history

**Example:**
- Typical patient with back pain: 4-6 physical therapy visits
- This member: 32 visits in 2 months
- Abnormality: 5x above normal → **MEDIUM RISK**

**What it catches:** Member falsifying symptoms to access drugs/services, member participating in fraud ring (deliberately getting billed for unnecessary care)

#### 4. Network Clustering
**The question:** Are suspicious entities connected in unusual ways?

**How it works:** Detect relationship patterns:
- Provider → Lab (do they work together a lot?)
- Provider → Member (too many claims between specific pairs?)
- Lab → Pharmacy (are they clustered?)
- All three together (classic fraud ring: provider orders unnecessary tests from specific lab, lab results drive unnecessary drugs from specific pharmacy)

**Example:**
- Provider A normally works with 47 different labs
- Provider A exclusively uses Lab B for 95% of tests
- Lab B exclusively works with Provider A for 87% of referrals
- Member M exclusively uses Provider A and Lab B combination
- Network anomaly score: 87% → **HIGH RISK**

**What it catches:** Kickback rings, shell companies, ghost testing (fake lab results), collusion networks

#### 5. Temporal Spike
**The question:** Is activity happening at abnormal times?

**How it works:** Compare activity timing to normal patterns:
- What day of week?
- What time of day?
- Weekday vs weekend?
- Holiday timing?

**Example:**
- Emergency surgery claims: Typically 2-3 per provider per week
- This provider: 8 claims on Sunday night, 7 on Saturday night
- Temporal anomaly: 400% above normal for weekend emergency surgery → **MEDIUM RISK**

**What it catches:** Phantom procedures (billed after hours when no staff present), falsified emergency claims, claims bundled fraudulently (multiple procedures claimed as simultaneous emergency)

---

## How Fraud Risk Gets Scored

Each claim is scored across all five dimensions:

```
CLAIM 12345: Total Fraud Risk = 68% (HIGH RISK - FLAG FOR REVIEW)

Breakdown:
├─ Billing Anomaly       ██████░░░░  60% (provider overbilling)
├─ Provider Deviation    ████░░░░░░  40% (slight deviation from peer)
├─ Member Cycling        ██████░░░░  65% (usage above normal)
├─ Network Clustering    ████████░░  80% (provider-lab tight relationship)
└─ Temporal Spike        ██░░░░░░░░  20% (claims within normal hours)

Final Score: 68%
├─ 25% weight: Billing Anomaly        = 15 points
├─ 25% weight: Provider Deviation     = 10 points
├─ 20% weight: Member Cycling         = 13 points
├─ 20% weight: Network Clustering     = 16 points
└─ 10% weight: Temporal Spike         = 2 points
Total:                                 = 56 points / 100 = 56% FRAUD RISK
```

**Score Thresholds:**
- **0-25%:** Low risk, logged but not flagged
- **25-50%:** Medium risk, visible but not urgent
- **50-75%:** High risk, flagged for review
- **75-100%:** Critical risk, immediate escalation

Claims scoring 50%+ are automatically flagged and appear in the investigator dashboard.

---

## A Day in the Life: Fraud Investigation Workflow

### 9:00 AM — Check Flagged Claims Dashboard

You open Card 5. You see:

```
FLAGGED CLAIMS - TODAY

🔴 CRITICAL (75%+):          2 claims
🟠 HIGH (50-75%):             8 claims
🟡 MEDIUM (25-50%):          24 claims

Total flagged today:         34 claims
Pending review:              34 claims
Under investigation:         12 cases
Awaiting coordination:        3 cases
Ready for prosecution:        1 case
```

Click any claim to see:
- Claim details
- Why it was flagged (which fraud dimensions fired)
- Evidence package pre-compiled
- Network visualization

Takes 2-5 minutes to scan and understand what's in the queue.

### 9:30 AM — Deep Dive into Top 3 Claims

**Claim 1 (Critical risk: 87%)**
- Claim: Provider bills $18,000 for imaging procedure
- Normal cost: $1,200
- Billing anomaly: 1,500% above baseline
- Provider deviation: Provider is 6 standard deviations above peer group
- Network issue: Provider exclusively uses one lab, lab exclusively uses this provider
- Verdict: "This looks like overbilling or phantom procedure. Create investigation case."

**Claim 2 (High risk: 68%)**
- Claim: Member accesses specialist 47 times in 2 months
- Member cycling: 8x above normal for diagnosis
- All visits to same provider
- Temporal spike: 60% of visits on Friday afternoons
- Verdict: "Member may be falsifying symptoms or part of fraud ring. Create investigation case."

**Claim 3 (High risk: 62%)**
- Claim: Provider-Lab-Pharmacy cluster detected
- Network clustering score: 85%
- Provider refers 94% of patients to one lab
- Lab results drive prescriptions to one pharmacy
- All three entities work together on 89% of member cases
- Verdict: "Classic kickback ring pattern. Investigate members in this cluster."

Takes 20-30 minutes to review top 3.

### 10:00 AM — Create Investigation Cases

For each flagged claim you want to investigate:

1. Click **"Create Investigation Case"**
2. System auto-populates:
   - Claim details
   - Fraud dimension breakdown
   - Evidence package (claim history, peer comparison, timeline, network)
   - Suggested next steps

3. You review and decide: Investigate further or close as false alarm

**Result:** 3 investigation cases created for the top claims

### 10:30 AM — Evidence Review for Case 1

Case 1 (Provider overbilling):

**System compiles:**

**Claim History** — All claims from this provider in last 2 years
- 47 claims total
- 23 are imaging (CT, MRI, ultrasound)
- Average imaging cost: $1,200
- This claim: $18,000
- Distribution: Most around $1,200; one cluster at $15k-$18k (suspicious)

**Peer Comparison** — How does this provider compare to peers?
- Provider's average imaging cost: $2,850
- Same specialty peer average: $1,195
- This provider bills 238% of peer average across all imaging
- Peers: None bill above $2,000
- This provider: 5 claims above $15,000

**Timeline Visualization** — When did suspicious claims happen?
- Normal claims: Spread across all months
- High-cost claims: Cluster in last 3 months
- Pattern: Escalating cost over time, suggesting intentional shift

**Network Visualization** — Who's connected to this provider?
- Provider works with 12 labs normally
- For high-cost imaging: Exclusively Lab #5
- Lab #5 exclusively works with this provider for high-cost imaging
- Lab #5 is new (started 6 months ago, coinciding with cost spike)
- Member group for high-cost claims: 15 members, tightly clustered

**Audit Trail** — Every action on these claims
- Claim created
- Claim submitted for payment
- Claim processed
- Payment issued
- Lab results attached (or missing?)

**Your Assessment:**
- Provider overbilling for imaging
- Possible phantom procedure (Lab #5 may be fake)
- Member group may be unwitting victims (billed for unnecessary procedures)
- **Recommendation:** Obtain Lab #5 credentials, interview Lab #5 staff, request medical records from members

Takes 30 minutes to review comprehensive evidence.

### 11:30 AM — Multi-State Coordination

Case shows: One member who received high-cost imaging also has claims in California and Texas.

Card 5 allows you to:
1. Click **"Request State Coordination"**
2. Specify: Which states? Which provider/lab? Which member?
3. Message: "Investigating provider overbilling ring. Have you seen claims from [Provider X] and [Lab Y]? Can you check?"
4. System routes to CA MFCU and TX MFCU

Coordination request sent. Wait for response.

### 2:00 PM — Monitor Active Cases

Card 5 shows all investigation cases in progress:

```
ACTIVE INVESTIGATION CASES

Case-001: Provider overbilling
├─ Status: Evidence gathering
├─ Created: Today 10:05 AM
├─ Days active: 0
└─ Next step: Obtain Lab #5 licensing records

Case-002: Member symptoms fraud
├─ Status: Awaiting state coordination (CA, TX)
├─ Created: Yesterday 3:15 PM
├─ Days active: 1
└─ Next step: Wait for CA/TX response on member access

Case-003: Kickback ring investigation
├─ Status: Ready for prosecution
├─ Created: 5 days ago
├─ Days active: 5
└─ Next step: Export prosecution package
```

Update notes on Case-001: "Requested Lab #5 licensing and credential verification from state board. Awaiting response."

Update Case-003: "Evidence complete, ready to escalate."

Takes 15 minutes to update cases.

### 5:00 PM — Export Prosecution Package

Case-003 is investigation-complete. Time to prepare for prosecution.

Click **"Export Prosecution Package"**

System compiles:

**Case Summary** (1 page)
- Allegations: Kickback ring (provider-lab-pharmacy conspiracy)
- Members affected: 23
- Total fraudulent claims: $347,000
- Timeframe: January—April 2026
- Recommendation: Federal referral (multi-state), prosecution

**Evidence Exhibits:**
1. Network visualization (showing provider-lab-pharmacy cluster)
2. Claim timeline (showing coordinated billing pattern)
3. Peer comparison (showing statistical deviation)
4. Member access analysis (showing clustering)
5. Lab credentials (showing possible licensing issues)
6. Financial impact (showing total fraud amount)
7. Audit trail (showing claims processing, no irregularities flagged pre-investigation)

**Exhibits Support:**
- 50 representative claims with annotation
- Peer comparison tables
- Statistical analysis (z-scores, standard deviations)
- Network relationship strength calculations
- Timeline visualization

**Package Format:** PDF, ready to send to DA or federal authorities

Exports as: `Case-003_Prosecution_Package_042526.pdf`

Takes 30 minutes to review, customize notes, and export.

---

## Card 5 Features: What You Can Do

### View Flagged Claims Dashboard
- See all flagged claims sorted by risk level
- Filter by: Risk level, fraud dimension, date range, provider, member, geography
- Click any claim for full details

### Understand Fraud Dimensions
Click any claim, then click any fraud dimension bar to understand:
- Why was this dimension flagged?
- What evidence supports the flag?
- How does this compare to normal?

Progressive disclosure: Start with "why is this flagged" and expand to detailed analysis.

### Create Investigation Case
Turn a flagged claim into a formal investigation:
1. Click **"Create Investigation Case"**
2. System asks: Which claim(s)? What's your primary suspicion? Provide optional notes.
3. System compiles evidence automatically
4. You review and decide: Proceed or false alarm?

### Review Evidence Packages
Every investigation case has pre-compiled evidence:

**Provided automatically:**
- Claim history (all related claims, visualized over time)
- Peer comparison (how does this compare to similar providers/members?)
- Timeline (when did events happen? Any pattern?)
- Network visualization (who's connected to whom? Relationship strength?)
- Audit trail (every action on these claims)
- Financial impact (how much money is at risk?)

Click to expand any section. Filter by date. Generate statistics.

### Visualize Provider/Member/Lab Networks
See relationship networks visually:
- Nodes = entities (providers, labs, members, pharmacies)
- Links = relationships (claims between them)
- Link thickness = relationship strength (how many claims?)
- Color = risk level (green = normal, yellow = suspicious, red = high risk)

Drag to explore. Click nodes to zoom into details.

### Monitor Investigation Cases
See all active cases:
- Status (evidence gathering, awaiting coordination, ready for prosecution, closed)
- Days active
- Next step
- Current owner (who's working this case?)

Click to update notes, add evidence, change status, reassign to another investigator.

### Request State Coordination
If case involves multiple states:
1. Click **"Request Coordination"**
2. Specify: Which states? Which entities? What information needed?
3. Message routes to appropriate state MFCUs
4. Track responses in case file

### Export Prosecution Package
Once investigation is complete:
1. Click **"Export Prosecution Package"**
2. System compiles:
   - Case summary (allegations, affected members, total fraud, recommendation)
   - Evidence exhibits (claims, timelines, network viz, peer comparison, financial impact)
   - Supporting documentation (audit trail, calculations, statistical analysis)
3. Export as PDF
4. Ready to send to DA or federal authorities

### Track Case Metrics
See statistics on your caseload:
- How many cases created this month?
- What's the average time to complete investigation?
- What's the typical fraud amount per case?
- Which fraud dimensions catch the most fraud?
- What's your investigation conversion rate (cases created → prosecution)?

---

## One System, All Investigators

**Key principle:** Entry-level analyst and senior investigator use the exact same system.

- Same flagged claims dashboard
- Same evidence compilation
- Same network visualization
- Same case management
- Same prosecution package export

**What differs:**
- Experience (senior knows what patterns matter most)
- Speed (senior moves faster through evidence)
- Judgment (senior catches nuance junior might miss)
- Caseload (senior handles complex multi-state cases)

But the tools are identical. The data is the same. The interface is the same.

A junior analyst can do exactly what a senior does. The system doesn't gatekeep.

---

## Data Security & Privacy

### What's Visible
- Claim details (cost, service, date, provider, member)
- Fraud signals (which dimensions fired, why)
- Evidence packages (claim history, peer comparison, network)
- Investigation notes (what you discovered)
- Audit trails (actions taken, by whom, when)

### What's NOT Visible
- Member names (replaced with hashed IDs)
- Member personal information
- Provider personal information beyond license/credentials
- Investigation strategy (until case is public)

### Access Control
**Everyone with Card 5 access sees the same data.**

If data is too sensitive to be visible, it's excluded from Card 5.

### Audit Trail
Every action is logged immutably:
- Who viewed which claim, when
- Who created which investigation case
- What evidence was reviewed
- Who exported prosecution packages
- When and why cases were closed

These records prove accountability and support prosecution (chain of custody).

---

## How Fraud Gets Caught: From Detection to Prosecution

### Phase 1: Automated Detection (Real-time)
1. Claim arrives
2. Analyzed against 5 fraud dimensions
3. Scored 0-100% risk
4. If ≥50%, flagged automatically
5. Appears in investigator dashboard

**Time: <1 second per claim**

### Phase 2: Initial Investigation (Hours to Days)
1. Investigator sees flagged claim
2. Reviews pre-compiled evidence
3. Decides: Real fraud or false alarm?
4. If real: Creates formal investigation case

**Time: 5-30 minutes per claim**

### Phase 3: Evidence Gathering (Days to Weeks)
1. Investigator compiles additional evidence
2. May request state coordination for multi-state cases
3. Interviews witnesses (optional)
4. Documents findings

**Time: 1-14 days depending on complexity**

### Phase 4: Prosecution Preparation (Hours)
1. Investigation complete
2. Export prosecution package
3. Review with supervisor (optional)
4. Send to DA or federal authorities

**Time: 1-2 hours**

### Phase 5: Prosecution
- DA / Federal authorities review
- Charges filed (if warranted)
- Court proceedings
- Conviction, restitution, sentencing

**Time: Months to years**

---

## Real-World Examples

### Example 1: Phantom Procedure (Caught by Billing Anomaly)

**Day 1:**
- Provider bills $18,000 for imaging procedure
- Billing anomaly detected: 1,500% above normal
- Claim flagged, appears in dashboard

**Day 1-2:**
- Investigator reviews claim
- Evidence shows provider bills 238% of peer average
- Investigation case created
- Lab #5 (new vendor) exclusively used for high-cost claims

**Day 3-5:**
- Investigator requests Lab #5 licensing
- Lab #5 cannot produce credentials
- Lab #5 is shell company
- Investigator confirms: No medical staff, no equipment, fake entity

**Day 6:**
- Prosecution package exported
- Sent to federal authorities
- Fraud: Provider falsified lab results, billed for phantom procedures
- Impact: $347,000 across 23 members

**Prosecution Result:** Conviction for fraud, conspiracy, money laundering

---

### Example 2: Member Cycling Fraud (Caught by Usage Anomaly)

**Day 1:**
- Member accesses specialist 47 times in 2 months
- Member cycling detected: 8x above normal
- Claim flagged

**Day 1-2:**
- Investigator reviews member access pattern
- All visits clustered on Friday afternoons
- All to same specialist
- Temporal spike also detected

**Day 3-4:**
- Investigator requests member interview
- Member admits: "I was offered $50 per visit to come get fake treatments"
- Investigator identifies other members in same ring
- Network clustering analysis reveals: 15 members, 1 provider, coordinated fraud

**Day 5-7:**
- Investigator works with member to obtain recorded conversations
- Provider-member kickback agreement documented
- Additional members identified and interviewed

**Day 8:**
- Prosecution package complete
- Federal referral for conspiracy, kickback fraud
- Impact: 15 members, 1 provider, $180,000 in fraudulent claims

**Prosecution Result:** Conviction for conspiracy, kickbacks, fraud

---

### Example 3: Kickback Ring (Caught by Network Clustering)

**Day 1:**
- Network clustering analysis detects: Provider-Lab-Pharmacy cluster
- All three entities exclusively work with each other
- Claim flagged

**Day 1-2:**
- Investigator reviews network visualization
- 89% of all claims involve all three entities together
- Pattern matches known kickback ring indicators
- Investigation case created

**Day 3-5:**
- Investigator subpoenas communications between entities
- Finds: "Send referrals to Lab #7, I'll send pharmacy referrals back"
- Explicit kickback agreements documented

**Day 6-10:**
- Multi-state coordination (CA, TX also have same entities)
- Investigator coordinates with CA MFCU and TX MFCU
- Multi-state fraud ring confirmed
- Federal authorities notified

**Day 11-14:**
- Prosecution package compiled with multi-state evidence
- Federal referral with 23 states participating

**Prosecution Result:** Multi-state federal prosecution, RICO charges, major sentencing

---

## The Principle: Automated Detection + Human Judgment

Card 5 automates the hard part: **Finding suspicious patterns in millions of claims.**

You provide the human part: **Judgment, context, decision-making, coordination.**

Machine: Flags 50 claims with 50%+ fraud risk
Human: Reviews 50, picks top 5 to investigate, applies context and experience

This combination catches fraud that either alone would miss.

---

## Getting Started

**First time using Card 5?**

1. Click **"View Flagged Claims Dashboard"**
2. Click the top flagged claim to see why it was flagged
3. Expand the fraud dimensions to understand what triggered the flag
4. Click **"Create Investigation Case"** to turn it into a formal investigation
5. Review the pre-compiled evidence package

**Experienced investigator?**

Jump straight to high-risk claims, use your judgment to triage, request state coordination as needed, export prosecution packages.

---

**Your feedback matters.** Card 5 is designed for you—the investigators, analysts, and fraud hunters who keep Medicaid honest. If something is unclear, slow, missing, or could work better, tell us.

---

End of Card 5 Architecture for Audience (AN)
