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

## Next Session: Provider Side Build-Out
- Wire qualifier logic into new enrollment flows
- Create provider-specific onboarding journey
- Test full Card 2 path from landing → login → enrollment gate → signup → chat
