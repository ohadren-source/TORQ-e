# TORQ-e Architecture for Business Analysts & State Employees

## What is TORQ-e?

TORQ-e is a unified identity system for New York State Medicaid. It solves one critical problem: **one person is called different things in different systems** (Member, Client, Recipient, Beneficiary, Provider, Applicant, etc.), which makes it impossible to track them consistently and enables fraud.

**The Solution**: Give everyone a single permanent identifier that never changes, no matter what else changes about them (name, address, insurance plan, employment status).

---

## The Five Types of People in Medicaid

### 1. **Member** (Person getting healthcare)
- Wants: "Am I eligible? What's covered?"
- Gets: **UMID** (Universal Member Identifier)
- Never changes, even if they move, change plans, or lose/regain eligibility

### 2. **Provider** (Doctor, hospital, clinic getting paid)
- Wants: "How do I enroll? How do I submit a claim? When do I get paid?"
- Gets: **UPID** (Universal Provider Identifier)
- Never changes, even if they change locations, get owned by another company, or change their specialty

### 3. **Plan Administrator** (Insurance company managing benefits)
- Wants: "Is this person in my network? How many people are enrolled?"
- Gets: **UHWP** (Universal Health+Wellness Program)
- Maps to the specific plan (e.g., Fidelis Care, Anthem, EmblemHealth)

### 4. **Government Stakeholder** (State employee overseeing the program)
- Wants: "How much are we spending? Are providers committing fraud? How do we compare to other states?"
- Gets: **USHI** (Universal Stakeholder Identity)
- Maps to their existing government employee ID; full access to state-level data

### 5. **Data Analyst** (Person investigating fraud or analyzing program performance)
- Wants: "Is this provider real? What patterns indicate fraud?"
- Gets: **UBADA** (Universal Business Analyst and Data Analyst)
- Can be a government employee or contractor; different skill levels (Junior, Senior, Lead)

---

## How the System Works: The Happy Path

### Scenario: John (member) visits Dr. Smith (provider)

**Step 1: John enrolls in Medicaid**
- John goes to TORQ-e website
- Submits driver's license for verification (or visits office in person)
- System confirms John is eligible
- System assigns John to Fidelis Care plan
- John gets permanent identifier: **UMID** (never changes)

**Step 2: Dr. Smith enrolls as provider**
- Dr. Smith goes to TORQ-e provider portal
- Submits NPI (national provider number) for verification
- System confirms Dr. Smith is valid, not on fraud list
- Dr. Smith gets permanent identifier: **UPID** (never changes)
- Dr. Smith is added to Fidelis Care network

**Step 3: John visits Dr. Smith**
- John calls Dr. Smith's office: "I have Medicaid"
- Office checks TORQ-e: "Is John in our network?"
- System responds: "Yes, John is covered. Copay is $15."
- Office sees John is eligible on that date
- John visits Dr. Smith, receives care

**Step 4: Dr. Smith submits claim**
- Dr. Smith enters: "John was here April 20, office visit, $150 charge"
- System verifies:
  - Is Dr. Smith a valid provider? ✅ Yes (UPID verified)
  - Is John eligible on April 20? ✅ Yes (UMID records show eligibility)
  - Is Dr. Smith in John's plan network? ✅ Yes (Fidelis Care)
  - Is this a reasonable charge? ✅ Yes
- System accepts claim
- Claim processing begins

**Step 5: Government oversight**
- Analyst Sarah (UBADA) wants to check: "Are Dr. Smith's billing patterns normal?"
- Sarah searches TORQ-e: "Show me all claims from UPID [Dr. Smith's ID]"
- System returns: 150 claims in April, average $140, diagnosis codes reasonable
- System calculates fraud risk: 15/100 (low risk, normal provider)
- Sarah approves claims for payment

**Step 6: Payment to Dr. Smith**
- Claims processed through Fidelis Care
- 15-30 days after submission, Dr. Smith gets paid
- Payment goes to bank account on file

---

## The Fraud Protection Layer

### What Happens If Dr. Smith is Suspicious?

Same scenario, but Dr. Smith has red flags:

**Signs TORQ-e Detects**:
- Address is a PO Box (not a real office)
- Billing volume 2x higher than other doctors in area
- Same service billed multiple times same day
- Billing services at hours office is closed
- Sudden 300% increase in claims over 3 months
- Claims for impossible service combinations (surgery + pediatric vaccines same visit)

**System Response**:
1. Automatic flag: "High fraud risk - 75/100"
2. Analyst Sarah is notified
3. Sarah reviews detailed assessment
4. Sarah says: "This looks like fraud"
5. Sarah creates investigation case
6. **Immediate**: Dr. Smith's future claims are put on hold (no new payments)
7. **Ongoing**: Inspector General investigates
8. **Result**: If fraud confirmed, state recovers overpayment

---

## Data Flow: The Big Picture

### What Information Flows Where?

```
┌─────────────────────────────────────────────────────────────────┐
│                     TORQ-e SYSTEM                               │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Members    │  │  Providers   │  │    Plans     │          │
│  │   (UMID)     │  │   (UPID)     │  │   (UHWP)     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                  │                   │                │
│         └──────────────────┼───────────────────┘                │
│                            │                                    │
│                ┌───────────▼───────────┐                        │
│                │   Central Database    │                        │
│                │  (UMID, UPID, UHWP   │                        │
│                │   Records + Mappings) │                        │
│                └───────────┬───────────┘                        │
│                            │                                    │
│          ┌─────────────────┼─────────────────┐                  │
│          │                 │                 │                  │
│     ┌────▼────┐     ┌──────▼──────┐  ┌──────▼──────┐           │
│     │ Claims  │     │  Oversight  │  │   Fraud    │           │
│     │Database │     │  Dashboard  │  │  Detection │           │
│     │(EMEDNY)│     │  (USHI)     │  │  (UBADA)   │           │
│     └─────────┘     └─────────────┘  └────────────┘           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
         │                       │                      │
         ▼                       ▼                      ▼
    ┌──────────┐         ┌──────────┐          ┌──────────────┐
    │  Member  │         │  State   │          │ Investigator│
    │ Sees: Am │         │ Sees: Am │          │ Sees: Is    │
    │ I        │         │ We       │          │ this fraud? │
    │ eligible?│         │ efficient?           │             │
    └──────────┘         └──────────┘          └──────────────┘
```

---

## Benefits of TORQ-e

### For Members
- ✅ Single identifier across all systems (no confusion)
- ✅ Can check eligibility anytime
- ✅ Can see what's covered before visiting doctor
- ✅ Never loses coverage due to administrative errors

### For Providers
- ✅ Simple enrollment process
- ✅ Know immediately if member is eligible
- ✅ Faster claim approval (15-30 days, not months)
- ✅ Lower fraud detection = lower audits and hassles

### For State
- ✅ Real-time fraud detection (save millions in overpayments)
- ✅ See program efficiency (which services cost most)
- ✅ Compare to other states (benchmarking)
- ✅ Faster investigations (all data in one place)

### For Plans (Insurance Companies)
- ✅ Know network status instantly
- ✅ See member enrollment trends
- ✅ Track quality metrics (HEDIS, CAHPS)

---

## The Two Verification Tiers

### Tier 1: Digital ID Verification (Fast)
- **For**: Members and providers with government-issued ID
- **Process**: Upload/verify ID digitally (takes minutes)
- **Outcome**: Instant verification, UMID/UPID created immediately
- **Cost**: Free, automated

**Who uses it:**
- Members with driver's license, passport, or state ID
- Doctors with NPI and state license
- Organizations with Tax ID (EIN) and business registration

### Tier 2: In-Person Verification (Slower, but inclusive)
- **For**: People without digital ID or whose digital ID doesn't verify
- **Process**: Visit local Medicaid office in person
- **Outcome**: Government worker verifies you, UMID/UPID created (next day)
- **Cost**: Free, no barriers to entry

**Who uses it:**
- Undocumented residents or people without US ID
- People whose digital ID is expired or damaged
- Organizations without registered Tax ID
- Providers new to US

**Key principle**: We help everyone. Tier 2 makes sure no one is excluded; government worker takes liability of vouching for person's identity.

---

## What Information is Collected?

### For Members (UMID)
- Name, Date of Birth
- Social Security Number (if available, hashed for security)
- Address, Contact info
- Household size and income
- Citizenship status
- Employment status

**Why**: Needed to check Medicaid eligibility under federal rules. Income limits apply to household, not individual.

### For Providers (UPID)
- Name or Organization name
- NPI (if doctor) or Tax ID (if organization)
- State license number
- Address
- Phone

**Why**: Needed to verify provider is real, valid, and not on fraud lists.

### For Government Stakeholders (USHI)
- Employee ID
- Name, Title, Agency
- Access level (Admin, Analyst, Auditor, View-Only)

**Why**: Needed to control who sees what data (state employees shouldn't see other state employees' private data, for example).

---

## Data Security: How is Your Data Protected?

### Encryption
- All personal information (names, SSNs, phone numbers) encrypted
- Encryption happens automatically - you don't do anything
- Encryption key stored separately from data

### Access Control
- Only authorized people can see your data
- Members see only their own information
- Providers see only patient names (no SSNs or private health info)
- State employees see only what their job requires
- Fraud analysts see only what's needed to assess fraud risk

### Audit Trail
- Every access to data is logged
- Who accessed? When? What did they see?
- Used to catch unauthorized access (e.g., nosy employee looking at celebrity's medical records)

### No Sale or Sharing
- Your data is never sold to third parties
- Your data is only shared with providers/plans you authorize
- Only used for Medicaid administration

---

## Relationship to Existing Systems

TORQ-e doesn't replace existing systems. It **connects** them:

### Existing Systems
- **EMEDNY**: Claims processing and payment (stays)
- **MPI**: Member identification (we use as source for UMID)
- **Medicaid Provider IDs**: Provider identification (we use as source for UPID)
- **State Licensing Boards**: Verify doctors/nurses are real (we check but don't replace)
- **CMS NPPES**: National provider database (we check but don't replace)

### What TORQ-e Adds
- **Single unified identifier** mapping all those systems
- **Real-time fraud detection** on top of existing claims data
- **Program oversight dashboard** for state decision-makers
- **Immediate eligibility verification** for members and providers

---

## Implementation Timeline

### Phase 1: Test Mode (Now)
- All users see mock data
- System works end-to-end
- Gathering feedback
- **Duration**: Weeks 1-4

### Phase 2: Limited Pilot (Members & Providers)
- Real member data flows in
- Real provider enrollments
- Manual oversight during transition
- **Duration**: Weeks 5-8

### Phase 3: Full Rollout (All Users)
- All members can use system
- All providers enrolled
- Government oversight active
- Fraud detection live
- **Duration**: Weeks 9+

---

## Questions State Employees Might Ask

**Q: Does this cost money?**
A: TORQ-e is built with existing state resources. No new licensing fees. Saves money by preventing fraud ($2-5M+ annually).

**Q: Will this slow down claims?**
A: No. Claims still process through EMEDNY (15-30 days). TORQ-e speeds up eligibility verification (immediate, not days).

**Q: What if member's data is wrong?**
A: Members can update their info anytime. System validates changes against government records. If no government record, member visits office for verification.

**Q: Can providers refuse to use TORQ-e?**
A: Providers must enroll to get paid. No exception. But enrollment is free and takes 10 minutes (Tier 1) or same-day (Tier 2).

**Q: What happens if provider commits fraud?**
A: TORQ-e detects it automatically. Analyst reviews. If confirmed, provider's claims are halted immediately, overpayment recovered, case referred to prosecutor if criminal.

**Q: Is this secure?**
A: Yes. Federal HIPAA standards met. Encryption used. Access logged. Separate security key management. Regular audits.

**Q: Can other states use TORQ-e?**
A: Yes. System designed to be portable. Other states can adopt, customize for their rules, operate independently.

