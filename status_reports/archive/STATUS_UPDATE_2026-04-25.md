# TORQ-E Status Update: 2026-04-25 (Post-Card 4 Lock)

**Date:** 2026-04-25  
**Status Snapshot:** 🔒 Card 4 LOCKED | 🔧 Card 3 FIXED | ⚠️ Cards 1-2 IDENTIFIED

---

## What's ✅ DONE

### Card 4 (USHI) - Government Stakeholder Operations
- ✅ **Locked & Frozen** (v1.0.0)
- ✅ All 6 test queries validated
- ✅ Spectrum Analyzer working (traffic lights on every response)
- ✅ Elaborate buttons functional
- ✅ DR;AN documentation complete
- ✅ Release notes published
- ✅ **Status:** READY FOR QA (Carol, Selam, Bob)

### Card 3 (WHUP) - Plan Network Management
- ✅ Fixed `requestedCount` scope error (was in try block, accessed in catch)
- ✅ Fixed "(5 shown)" display bug (now shows actual count)
- ✅ **Refactored routing from question-type hardcoding to context-driven:**
  - Primary routing: Explicit user actions (show/find/enroll/etc.)
  - Secondary routing: Conversation context (lastPlansShown)
  - Fallback: Generic help only when no action/context
- ✅ Added `handleContextualQuestion()` for flexible follow-ups
- ✅ **Example:** User asks "which is best if i make 10k/anum?" → System recognizes it's about the 3 plans just shown, answers contextually
- ✅ **Status:** CHAT LOGIC REFACTORED, needs testing

### Landing Page
- ✅ Removed status banner ("Evolving Production-Ready Demonstration")
- ✅ Removed banner CSS
- ✅ **Status:** CLEAN & PRODUCTION READY

### Documentation
- ✅ Card 4 DR updated (LOCKED notation)
- ✅ Card 4 AN updated (LOCKED notation)
- ✅ Card 5 rollout strategy created (6-week build plan)
- ✅ Release notes v1.0.0 published

---

## What's ⚠️ IDENTIFIED (Needs Discussion)

### Card 1 (UMID) - Member Portal
- **Issue:** Chat asks for Member ID even when user is logged in with UMID
  - User is already authenticated
  - System already has UMID in session
  - Shouldn't ask "Are you covered by Medicaid?" if they're logged in
  - Only relevant: "Will I lose coverage if my income changes?"
- **Root Cause:** Chat logic doesn't use session context (authentication state, user identity)
- **Pattern:** Similar to Card 3 problem, but opposite direction
  - Card 3: Too much hardcoding, needs context
  - Card 1: No context usage, should use session state
- **File Location:** Unknown (not in TORQ-e folder - either in backend templates or served dynamically)
- **Status:** IDENTIFIED, location needed

### Card 2 (UPID) - Provider Claims Portal
- **Status:** Unknown - needs inspection
- **Question:** Does it have same context issue as Card 1?

---

## Architecture State

**TORQ-e v1.0.0 System Status:**

```
Card 1 (Members):       🟡 FUNCTIONAL, context usage issue
Card 2 (Providers):     ? UNKNOWN
Card 3 (Plans):         🟢 REFACTORED, context-driven routing
Card 4 (Government):    🔒 LOCKED, validated
Card 5 (inauthenticity):         📋 DESIGNED (6-week roadmap)

Deployment:             ✅ Railway
Infrastructure:         ✅ Unified substrate
Documentation:          ✅ Complete (Cards 1-5)
```

---

## The Issue Pattern

**Cards differ in conversation type:**

1. **Card 4 (Conversational, open-ended)**
   - Users ask many different questions about system health
   - Need: Context-driven routing ✅ (already has it)
   - Pattern: What's the status? → Show metrics → User asks follow-up → Answer contextually

2. **Card 3 (Conversational, contextual)**
   - Users ask about plans they're looking at
   - Need: Context-driven routing ✅ (just fixed)
   - Pattern: Show 3 plans → User asks follow-up → Answer about THOSE plans

3. **Card 1 (Constrained, state-aware)**
   - Users are already logged in with identity
   - Need: Session context usage (currently missing)
   - Problem: Asks for info it already has
   - Pattern: User logged in as UMID-12345 → Don't re-ask for ID

4. **Card 2 (Presumably constrained, state-aware)**
   - Similar to Card 1?
   - Status: TBD

---

## Next Step: Discussion Points

1. **Card 1 Chat Location:** Where is the actual chat file? (backend template? dynamic serving?)
2. **Card 1 Scope:** Should it use session identity automatically, or require re-authentication?
3. **Card 2:** What's the pattern? Same as Card 1?
4. **Priority:** Fix Cards 1-2 now, or deliver Cards 3-4 to QA first?

---

## Quick Facts

- **Status Banner:** Removed ✅
- **Card 3 Bugs:** Fixed ✅
- **Card 4:** Locked & ready for QA ✅
- **Architecture:** Context-driven (conversational) vs. session-aware (authenticated) ✅
- **Next Major Work:** Cards 1-2 session context, then Card 5 build
