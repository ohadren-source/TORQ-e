# TORQ-E Card 3: Programs/Plans Architecture
## Internal Design Repository (DR)

---

## Overview

**Card 3** is the beneficiary-facing marketplace where members discover, compare, and select Medicaid programs and plans. In NY, this is eMedNY. In CA, this is DHCS portal + Medi-Cal. In any state, it's the electronic enrollment system.

Card 3 is NOT authenticity verification. NOT governance. It's the interface between beneficiaries and the program options available to them.

**Core Principle:** Simplicity. Members should browse, understand, and enroll in <5 minutes.

---

## Data Model

### Programs/Plans Structure

```
Program {
  id: string (unique across all states)
  name: string (e.g., "Medicaid", "Managed Care Option A")
  type: enum (MEDICAID, MANAGED_CARE, SPECIAL_NEEDS, DUAL_ELIGIBLE)
  state: string (NY, CA, TX, etc.)
  eligibility_criteria: {
    age_min: number
    age_max: number
    income_limit: number
    citizenship_required: boolean
    disability_status_required: boolean
    special_conditions: string[]
  }
  benefits: {
    primary_care: boolean
    specialist_visits: boolean
    emergency: boolean
    hospitalization: boolean
    pharmacy: boolean
    mental_health: boolean
    dental: boolean
    vision: boolean
    long_term_care: boolean
    custom_benefits: string[]
  }
  coverage_start_date: date
  coverage_end_date: date (or null for ongoing)
  network_type: enum (HMO, PPO, FFS, CAPITATED)
  cost_sharing: {
    member_premium_monthly: number
    copay_primary: number
    copay_specialist: number
    copay_emergency: number
    deductible: number
  }
  provider_directory_url: string
  contact_info: {
    phone: string
    website: string
    support_hours: string
  }
  enrollment_deadline: date
  status: enum (ACTIVE, PENDING, CLOSED, ARCHIVED)
  audit_trail: {
    created_at: timestamp
    updated_at: timestamp
    last_modified_by: string (system or user)
    change_log: string[]
  }
}

Beneficiary_Program_Selection {
  id: string
  beneficiary_id: string (masked/hashed)
  program_id: string
  selected_at: timestamp
  selection_effective_date: date
  enrollment_status: enum (PENDING, CONFIRMED, ACTIVE, TERMINATED)
  termination_reason: string (optional)
  audit_trail: immutable
}
```

### Beneficiary View (Card 3 ↔ Card 1)

Card 3 does NOT store beneficiary data. It queries Card 1 for:
- Member eligibility status
- Current program selection
- Enrollment history

This is a one-way flow: Card 1 → Card 3 (read-only for program display)

---

## User Workflows: "A Day in the Life"

### Beneficiary Journey

**Tuesday, 10:00 AM:** Maria (beneficiary) logs into eMedNY

1. **Landing Page** - "What coverage do you need?"
   - Simple question, not overwhelming
   - Three paths:
     - "I need new coverage"
     - "I already have Medicaid, changing plans"
     - "I'm just browsing"

2. **Eligibility Check** - "Are you eligible?"
   - Pre-filled from Card 1 (if logged in)
   - Or quick questionnaire (age, income, citizenship)
   - Real answer: "Yes, you qualify for X, Y, Z programs"

3. **Program Browse** - "Which program works for you?"
   - Shows only programs she qualifies for
   - Card display:
     - Plan name
     - Cost (premium + copays)
     - Network (HMO/PPO)
     - Key benefits (checkmarks)
     - "Click to compare"
   - NO detail clutter. Clean. Simple.

4. **Plan Compare** - "How do these differ?"
   - Side-by-side comparison of 2-3 plans
   - Key differences highlighted
   - Cost breakdown
   - Network differences
   - "Expand details" for deep dive (collapsed by default)

5. **Plan Detail (Collapsed)** - "Tell me more"
   - Full benefits list
   - Provider directory link
   - Customer service contact
   - Enrollment deadline
   - Terms and conditions (expandable)
   - Audit note: "You viewed this plan at 10:15 AM"

6. **Enrollment** - "Ready to enroll?"
   - One-click confirmation (or "Review my choice")
   - Handoff to Card 1 (enrollment processing)
   - Confirmation: "You're enrolled. Coverage starts [date]."

**Total time:** 3-5 minutes for decision, 1 minute to enroll

---

## Technical Architecture

### Frontend (Member-Facing)

**Stack:** React, TypeScript, responsive design (mobile-first)

**Key Components:**
- Program Browse (filterable list, card view)
- Plan Comparison (side-by-side, collapsible detail)
- Benefit Detail (progressive disclosure)
- Selection Confirmation (one-click or review)

**Design Principles:**
- Simplicity first (desktop and mobile identical in UX)
- Progressive disclosure (expand for detail)
- One action per screen (no overwhelm)
- Clear call-to-action (next button obvious)
- Help available but hidden (tooltip, "?" icon)
- Real-time eligibility feedback

**Performance:**
- Program list: <1s load
- Plan comparison: <500ms
- Detail expansion: instant (all data pre-loaded)
- Mobile: responsive at all breakpoints

### Backend (Card 3 API)

**Endpoints:**

```
GET /api/card3/programs
  - Query: state, program_type, status
  - Returns: [Program]
  - Rate limit: 100 req/sec (public data)

GET /api/card3/programs/{id}
  - Returns: Program (full detail)
  - Includes audit trail (who viewed, when)

GET /api/card3/eligible-programs
  - Query: beneficiary_id (from Card 1 auth token)
  - Returns: [Program] (filtered to member's eligibility)
  - Real-time eligibility check against Card 1

POST /api/card3/programs/{id}/compare
  - Query: program_ids (array of 2-3 IDs)
  - Returns: comparison_data (cost, benefits diff, network diff)

POST /api/card3/enroll
  - Payload: {beneficiary_id, program_id, selection_date}
  - Returns: confirmation + handoff token to Card 1
  - Triggers: audit log entry (immutable)

GET /api/card3/beneficiary-selection
  - Query: beneficiary_id
  - Returns: current program selection + history
  - Card 1 can query this for status
```

**Data Freshness:**
- Program list: updated daily (batch from state data source)
- Member eligibility: real-time (queried from Card 1 on demand)
- Audit trails: immutable (write-once, never delete)

### Database Schema

```sql
CREATE TABLE programs (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  type ENUM (MEDICAID, MANAGED_CARE, SPECIAL_NEEDS, DUAL_ELIGIBLE),
  state VARCHAR(2) NOT NULL,
  eligibility_criteria JSONB NOT NULL,
  benefits JSONB NOT NULL,
  cost_sharing JSONB NOT NULL,
  network_type ENUM (HMO, PPO, FFS, CAPITATED),
  status ENUM (ACTIVE, PENDING, CLOSED, ARCHIVED),
  coverage_start_date DATE,
  coverage_end_date DATE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
  INDEX idx_state (state),
  INDEX idx_type (type),
  INDEX idx_status (status)
);

CREATE TABLE beneficiary_selections (
  id UUID PRIMARY KEY,
  beneficiary_id UUID NOT NULL, -- hashed, not plaintext
  program_id UUID NOT NULL REFERENCES programs(id),
  selected_at TIMESTAMP NOT NULL,
  selection_effective_date DATE NOT NULL,
  enrollment_status ENUM (PENDING, CONFIRMED, ACTIVE, TERMINATED),
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  audit_trail JSONB NOT NULL, -- immutable
  FOREIGN KEY (program_id) REFERENCES programs(id),
  INDEX idx_beneficiary_id (beneficiary_id),
  INDEX idx_program_id (program_id),
  INDEX idx_enrollment_status (enrollment_status)
);

CREATE TABLE program_views_audit (
  id UUID PRIMARY KEY,
  beneficiary_id UUID NOT NULL, -- hashed
  program_id UUID NOT NULL,
  action ENUM (BROWSE, COMPARE, DETAIL_VIEW, ENROLL),
  viewed_at TIMESTAMP NOT NULL,
  device_type ENUM (DESKTOP, MOBILE, TABLET),
  session_id VARCHAR(255),
  IMMUTABLE -- write-once table
);
```

---

## Integration Points

### Card 3 ↔ Card 1 (Beneficiary)
- **Direction:** One-way read (Card 3 → Card 1)
- **Query:** Get member eligibility, current selection, history
- **Update:** Card 3 sends selection to Card 1 for enrollment processing
- **Auth:** OAuth token from Card 1 used for Card 3 API calls

### Card 3 ↔ Card 4 (Governance)
- **Direction:** One-way report (Card 3 → Card 4)
- **Data:** Aggregate selection metrics (how many members choosing each plan)
- **Frequency:** Daily batch
- **Privacy:** Aggregated only, no member details
- **Purpose:** Bob monitors program popularity and enrollment health

### Card 3 ↔ Card 5 (inauthenticity)
- **Direction:** One-way report (Card 3 → Card 5)
- **Data:** Suspicious selection patterns (e.g., rapid plan switches, unusual timing)
- **Frequency:** Real-time anomaly detection
- **Purpose:** OMIG flags potential benefits inauthenticity

---

## Security & Privacy

### PII Handling
- Member names: never displayed to anyone except member themselves
- Member IDs: hashed in all audit logs
- Income/citizenship: used only for eligibility filtering, never stored in selection records
- All PII access logged immutably

### Data Access
- Public data (program list): no auth required
- Member selections: encrypted in transit, requires member auth token
- Audit trails: accessible to Card 4 (governance) and Card 5 (inauthenticity) with proper role access

### Immutability
- Once a member selects a program, that record is immutable
- Changes (e.g., switching programs) create new records, never delete old
- Audit trail captures every view, compare, and selection action
- Timestamps are server-side, not client-side (tamper-proof)

---

## Performance & Scalability

### Load Expectations
- Peak enrollment season: 500K-1M concurrent members browsing
- Daily program views: 5-10M page loads
- Peak time: 9-11 AM (people browsing before work)

### Caching Strategy
- Program list: cached for 24 hours (changes rare)
- Member eligibility: no caching (must be real-time)
- Comparison data: cached for 1 hour (static data)
- Session data: in-memory, 30-minute TTL

### Database Optimization
- Indexes on state, type, status (program browsing)
- Indexes on beneficiary_id, enrollment_status (member history)
- Partition beneficiary_selections by state (scales across 50 states)
- Archive old selections to cold storage after 2 years

---

## Error Handling

**What can go wrong:**

1. **Eligibility changes mid-enrollment** - Member qualifies, then doesn't
   - Solution: Re-check eligibility at enrollment (real-time Card 1 query)
   - If ineligible: show message, suggest eligible programs

2. **Program closes between browse and enroll** - Program is discontinued
   - Solution: Validate program status at enrollment
   - If closed: show message, suggest similar programs

3. **System unavailability** - eMedNY goes down
   - Solution: Graceful degradation (show cached program list, enroll offline, batch-process later)
   - Timeout: 5 seconds (then show "Try again" message)

4. **Data sync failures** - Card 3 program list out of sync with state source
   - Solution: Automated reconciliation (daily, nightly batch)
   - Fallback: use state-of-record if sync fails

---

## Metrics & Monitoring

**What we measure:**

- Program discovery: which programs are viewed most?
- Program selection: which programs are enrolled in most?
- Abandonment: how many members browse but don't enroll?
- Comparison usage: what % use side-by-side compare?
- Mobile vs. desktop: where do members enroll from?
- Time to enroll: average session duration?
- Error rates: where do members get stuck?
- Geographic patterns: differences by state or region?

**Dashboard (for Card 4):**
- Daily enrollments by program
- Program popularity trends
- Geographic enrollment patterns
- Mobile vs. desktop engagement
- Abandonment funnel (browse → compare → enroll)
- Error/timeout rates

---

## Audit Trail (Immutable)

Every action in Card 3 is logged:

```json
{
  "timestamp": "2026-04-25T10:15:00Z",
  "beneficiary_id": "hash(12345)",
  "action": "PROGRAM_VIEWED",
  "program_id": "prog-123",
  "session_id": "sess-abc",
  "device": "mobile",
  "location": "hashed_ip",
  "duration_ms": 45000
}

{
  "timestamp": "2026-04-25T10:18:00Z",
  "beneficiary_id": "hash(12345)",
  "action": "PROGRAMS_COMPARED",
  "program_ids": ["prog-123", "prog-456"],
  "session_id": "sess-abc"
}

{
  "timestamp": "2026-04-25T10:20:00Z",
  "beneficiary_id": "hash(12345)",
  "action": "PROGRAM_ENROLLED",
  "program_id": "prog-123",
  "enrollment_status": "PENDING",
  "handoff_token": "tok-xyz",
  "session_id": "sess-abc"
}
```

These records are:
- Written to immutable append-only log
- Never modified or deleted
- Queryable by Card 4 (governance audit)
- Queryable by Card 5 (authenticity investigation)
- Visible to member on request ("View my activity")

---

## Future Enhancements

1. **Program Recommendations** - AI-powered suggestions based on member profile
2. **Comparison Engine** - Cost calculators (how much will I pay for care?)
3. **Real-time Network Search** - Search for specific providers within chosen plan
4. **Enrollment Support** - Live chat, call center integration
5. **Mobile App** - Native iOS/Android app for enrollment
6. **Accessibility** - VoiceOver, screen reader optimization, language support (Spanish, etc.)

---

## "Know Your Audience" Application

**Member perspective:** I need to find and enroll in a plan. I don't care about data architecture, audit trails, authenticity verification. I care about: What will it cost? Will my doctor be covered? How long does this take?

**Card 3 answers these questions. That's it. That's the job.**

No complexity. No options. No theory. Just: browse → compare → enroll → done.

Everything else (audit trail, authenticity verification, governance) is hidden. It exists, but the member never sees it.

---

End of Card 3 Architecture (DR)