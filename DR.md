# DOMINION REPUBLISH (DR) LOG
**Purpose:** Personal accountability log for all changes made to TORQ-e, from microscopic to massive. Append-only record of decisions, rationale, and impact.

---

## [2026-04-24] Session: Enrollment Gate Architecture & Tutorial Cleanup

### Change 1: Enhanced login-card1.html
**Scope:** MAJOR ARCHITECTURAL  
**What:** Added toggle-based enrollment gate logic to member login page  
**Why:** Moved qualification logic from pre-login (qualifier-card1.html) to post-identification. More logical: if someone already has a UMID, they've already qualified. Only ask about enrollment status if they don't have credentials.  
**How:** 
- Added toggle: "I have a Member ID" vs "I don't have an ID"
- If have ID: normal login flow (username/email)
- If no ID: branch to "Are you enrolled?"
  - YES: ask for UMID
  - NO: direct to signup-info-card1.html
- JavaScript handles all state management and routing  
**Files Modified:** login-card1.html  
**Impact:** Removes unnecessary pre-qualification gatekeeping. Respects existing members' time.

---

### Change 2: Enhanced login-card2.html
**Scope:** MAJOR ARCHITECTURAL  
**What:** Added toggle-based enrollment gate logic to provider login page  
**Why:** Same rationale as Change 1 but for providers. Providers with NPIs have already proven eligibility/enrollment.  
**How:**
- Toggle: "I have a Provider ID" vs "I don't have an ID"
- If have ID: normal login (NPI/email)
- If no ID: branch to "Are you enrolled?"
  - YES: ask for NPI
  - NO: direct to signup-info-card2.html
- JavaScript mirrors member logic structure  
**Files Modified:** login-card2.html  
**Impact:** Eliminates redundant pre-qualification. Streamlines onboarding for existing providers.

---

### Change 3: Updated landing.html Navigation
**Scope:** MEDIUM (STRUCTURAL)  
**What:** Changed Card 1 & Card 2 links from qualifier pages to login pages directly  
**Why:** Qualifiers now redundant. Enrollment gate logic moved inside login pages. Direct routing is cleaner, faster, respects user intent.  
**How:**
- Card 1: `qualifier-card1.html` → `login-card1.html`
- Card 2: `qualifier-card2.html` → `login-card2.html`
**Files Modified:** landing.html  
**Impact:** Removes one layer of navigation. Qualifiers can be archived (still exist but unreferenced).

---

### Change 4: Cleaned tutorial-card1.html
**Scope:** MINOR (CONTENT/ACCURACY)  
**What:** Three specific refinements based on recent system changes  
**Why:**
1. **Removed synonym list** - User explicitly removed all synonyms for "Member". Old language: "Whether you're a Member, Client, Recipient, or Beneficiary" was now wrong.
2. **Added phone support number** - signup-info-card1.html includes 1-855-355-5777. Tutorial support section should match.
3. **Linked enrollment limitation** - Instead of saying "can't enroll you," now says "can't enroll you, but here's our guide."
**How:**
- Line 186: Changed to "As a Member, TORQ-e is here..."
- Line 206: Added link to signup-info-card1.html
- Support section: Added phone number
**Files Modified:** tutorial-card1.html  
**Impact:** Maintains consistency with recent rebranding decisions and user guidance architecture.

---

### Change 5: Cleaned tutorial-card2.html
**Scope:** MINOR-TO-MEDIUM (CONTENT/EMPHASIS)  
**What:** Four refinements to provider tutorial  
**Why:**
1. **Fixed enrollment language** - Providers don't "enroll in Medicaid," they "enroll as providers." Old language was member-focused.
2. **Linked enrollment guidance** - Connected "can't enroll" to signup-info-card2.html with eMedNY reference.
3. **Elevated fraud detection** - River Path algorithm is a key differentiator for providers. Was buried. Now prominent with "confidence scoring" emphasis.
4. **Added eMedNY link** - Support section now directs providers to enrollment portal.
**How:**
- Line 208: Changed "enroll you in Medicaid" to "enroll you as a provider" + signup link
- Features section: Rewrote bullets to emphasize fraud detection, River Path algorithm, and confidence scoring
- Support section: Added eMedNY.ny.gov link
**Files Modified:** tutorial-card2.html  
**Impact:** Better differentiates provider value proposition. Aligns language with provider workflows.

---

### Summary of Session
- **Total Changes:** 5 (2 architectural, 1 structural, 2 content refinements)
- **Files Modified:** 5 (login-card1.html, login-card2.html, landing.html, tutorial-card1.html, tutorial-card2.html)
- **Lines Changed:** ~150 total
- **Architectural Impact:** MODERATE - Moved logic from pre-login to post-identification. Streamlined user journey for both personas.
- **Rationale Theme:** Eliminate redundant gatekeeping. Respect users' time. Self-sort by role identification.

---

### Change 6: Removed alias explanation from login-card1.html
**Scope:** MICROSCOPIC (POLISH)
**What:** Removed "Also known as: Client, Recipient, or Beneficiary" from Member identifier box
**Why:** User instruction to remove hedging language. "Member" is the universal term. No alternatives needed. Cleaner, clearer frame.
**How:** Removed 1 line from aliases div in login-card1.html
**Files Modified:** login-card1.html
**Impact:** Visual/semantic clarity. No functional change.

---

---

## [2026-04-24] Session: UPID Provider Enrollment Reference & FAQ (DOH-Recognized Entities Only)

### Change 7: Created upid-reference.html
**Scope:** MAJOR (NEW SYSTEM)  
**What:** Built searchable, interactive provider enrollment reference website (UPID) displaying DOH-recognized provider entities only  
**Why:** 
- Provider definition clarity: Any entity recognized by NY Department of Health as a distinct health care/well-being service provider
- Data structure corrected: 14 provider entities (not 15-20 with overlapping services)
- Critical insight applied: 3 pharmacy types (Community, Hospital, LTC) with services offered within those types, not separate provider enrollments
- Single physician entity with enrollment options (FFS, MCO, OPRA), not duplicate provider types
- Specialty drugs, compounding, home infusion are services—not provider type distinctions

**How:**
- Google Desktop search-style interface with real-time filtering
- Category filters: Individual Practitioners (5 types), Pharmacy (3 types), Facilities (3 types), Services & Equipment (3 types)
- For each entity: Core requirements, enrollment options, services offered, critical notes, common issues
- Expandable cards for clean UX
- Search functionality across entity names, requirements, services, timelines

**Provider Entities Included:**
- **Individual Practitioners:** Physician, Nurse Practitioner, Registered Nurse, Clinical Social Worker, Psychologist
- **Pharmacy (DOH-recognized as distinct entities):** Community Pharmacy, Hospital Pharmacy, Long-Term Care Pharmacy
- **Facilities:** Hospital/Acute Care, Long-Term Care Facility (Nursing Home)
- **Services & Equipment:** DME Supplier, Clinical Laboratory, Vision Care Provider, Non-Emergency Medical Transportation (NEMT)

**Files Created:** upid-reference.html  
**Impact:** Single authoritative reference for provider entity types; eliminates confusion about services vs. entities; directly addresses user's need for "provider type" clarity.

---

### Change 8: Created upid-faq.html
**Scope:** MAJOR (NEW SYSTEM)  
**What:** Built searchable FAQ addressing 110+ common enrollment questions, organized by DOH-recognized provider entity  
**Why:** 
- FAQ data directly maps to cleaned provider entity structure (no redundancy)
- Specific answers for each entity type (no conflicting information about "is X a separate provider type?")
- Searchable across Q&A to answer both factual and conceptual questions
- Eliminates the "Specialty Pharmacy" confusion by answering directly: "Is Specialty Pharmacy separate? No. Here are the 3 pharmacy types. Here's what services they can offer."

**How:**
- 110+ Q&A pairs grouped by provider entity (General, Individual Practitioners, Pharmacy, Facilities, Services)
- Expandable Q&A format (collapsed for clean UX, expandable for answers)
- Real-time search across questions and answers
- Category filtering matches upid-reference.html organization
- Rich HTML answers with lists, emphasis, and formatting

**Topics Covered:**
- Entity vs. service distinctions (NPI, OIG, credentials per type)
- Enrollment options and timelines per entity
- Services each entity can offer
- Critical requirements and common enrollment blockers
- Specific Q&A for each of 14 provider types

**Files Created:** upid-faq.html  
**Impact:** Clean data structure for knowledge base; answers both "what" and "why" questions; supports provider self-service enrollment preparation.

---

### Summary of Session
- **Total Changes:** 2 (2 new systems)
- **Files Created:** 2 (upid-reference.html, upid-faq.html)
- **Lines of Code:** ~2,100 total (both files combined)
- **Architectural Impact:** MAJOR - New searchable provider enrollment reference system following DOH entity definitions
- **Rationale Theme:** Correct aperture on provider entities (not services). Eliminate data redundancy. Create single authoritative reference aligned with regulatory language.

### Critical Insight
The user (via Carol's feedback) clarified that eMedNY recognizes only 3 pharmacy provider types, not 7. The others (specialty, compounding, home infusion) are services or prescription types offered within those entities. This required complete restructuring of the provider data:
- **Before:** 15+ "provider types" mixing entities and services
- **After:** 14 DOH-recognized provider entities; services clearly separated as "what this entity can offer"

This cleaner structure makes the data far more suitable for searchable FAQs and reduces confusion about provider enrollment.

---

---

## [2026-04-24] Session: System Prompt Formatting & Clarity (All 5 Personas)

### Change 9: Reformatted chat.py System Prompts for Visual Clarity
**Scope:** MEDIUM (CONTENT/PRESENTATION)  
**What:** Updated all 5 persona system prompts in chat.py to enforce clean, visual response formatting  
**Why:**
- User feedback: Responses were walls of text, hard to scan and read
- Solution: Instruct Claude to use markdown formatting, bullet points, headers, tables, spacing
- Impact: Chat responses now display with visual hierarchy (bold, bullets, tables, sections)
- Goal: Make TORQ-e responses "shine" with professional formatting

**How:**
- Added base formatting instruction to all 5 personas
- Each persona now includes specific formatting rules for their domain
- Base instruction covers: headers, bullets, tables, whitespace, callouts, links, code blocks
- Per-persona customization: Clinical terms for Provider, Data terms for Analyst, etc.

**Base Formatting Rules Applied:**
```
- Clear section headers (use **bold** for headers)
- Bullet points with ✓, ✗, →, | symbols for visual hierarchy
- Tables for comparing options
- Short paragraphs with breathing room
- Action items clearly marked
- Links in markdown format: [Text](URL)
- Code blocks with syntax highlighting
- Numbered steps for processes
- Callout boxes for important notes
```

**Persona-Specific Updates:**

1. **Card 1: UMID (Member)**
   - Core Principles: Empathetic, clear, actionable, honest about limits
   - Formatting: Plain English, checklists, contact info emphasized
   - Tone: Like talking to a family member

2. **Card 2: UPID (Provider)**
   - Core Principles: Technical, specific, solution-focused, direct
   - Formatting: Tables for enrollment options, claim codes, NPI verification steps
   - Tone: Clinical/billing language, actionable troubleshooting

3. **Card 3: UHWP (Plan Admin)**
   - Core Principles: Data-driven, comparative, forward-looking, executive-ready
   - Formatting: KPIs first, tables for benchmarks, trend analysis
   - Tone: Dashboard-level summaries with drill-down capability

4. **Card 4: USHI (Government Stakeholder)**
   - Core Principles: Compliant, aggregate, accountable, official
   - Formatting: Regulatory citations, policy language, aggregate metrics
   - Tone: Official with compliance focus, policy-aligned

5. **Card 5: UBADA (Data Analyst)**
   - Core Principles: Technical, detailed, skeptical, evidence-based
   - Formatting: Statistical language, confidence intervals, before/after comparisons
   - Tone: Precise data analysis with probability-based risk assessment

**Files Modified:** chat.py (get_system_prompt function)  
**Impact:** All 5 chat personas now produce professionally formatted, visually clear responses with proper hierarchy and readability.

---

## Next Session: Provider Side Build-Out
- Wire UPID reference into login-card2.html navigation
- Create provider-specific onboarding journey
- Test full Card 2 path from landing → login → enrollment gate → signup → UPID reference → chat
