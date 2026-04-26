# TORQ-e: What IS vs. What AUGHT To Be

**Date:** April 24, 2026  
**Purpose:** Audit of signal-over-noise veracity framework across all 5 cards before Card 5 design  
**Critical Finding:** Confidence scoring exists partially, but red/yellow/green veracity visualization doesn't exist anywhere. This is foundational. Cannot ship without it.

---

## SUMMARY: IS vs. AUGHT

| Component | Card 1 | Card 2 | Card 3 | Card 4 | Card 5 |
|-----------|--------|--------|--------|--------|--------|
| **Backend Logic** | ✅ YES | ✅ YES | ❌ NO | ❌ NO | ❌ NO |
| **Confidence Scoring** | ✅ FULL | ⚠️ BASIC | ❌ NO | ❌ NO | ❌ NO |
| **Signal/Noise Framework** | ✅ YES | ❌ NO | ❌ NO | ❌ NO | ❌ NO |
| **Consensus Logic** | ✅ YES | ❌ NO | ❌ NO | ❌ NO | ❌ NO |
| **Caveat Generation** | ✅ YES | ❌ NO | ❌ NO | ❌ NO | ❌ NO |
| **Red/Yellow/Green Veracity** | ❌ NO | ❌ NO | ❌ NO | ❌ NO | ❌ NO |
| **Chat Tools** | ✅ YES | ✅ YES | ❌ EMPTY | ❌ EMPTY | ❌ EMPTY |
| **HTML Interface** | ✅ WORKING | ✅ WORKING | ⚠️ STUB | ⚠️ STUB | ⚠️ STUB |

---

## CARD 1 (UMID - Member): ~85% Complete

### What IS:
✅ **Backend:** Full river_path.py implementation with 3-attempt cascading lookup  
✅ **Confidence Framework:** `card_1_umid/confidence.py` with:
  - `score_river_path_result()` — Quality × Completeness × Age formula
  - `score_eligibility_determination()` — Multi-factor confidence scoring
  - `score_consensus()` — Signal-over-noise weighting (60% avg_score + 40% agreement)
  - `generate_caveat()` — Transparent warnings when confidence < 0.85
  - `TieredConfidenceReporting` — Different detail levels for different users
✅ **HTML Chat:** chat-card1.html with streaming + markdown rendering  
✅ **Tools:** lookup_member, check_eligibility, check_recertification

### What AUGHT (But Isn't):
❌ **Veracity Visualization:** No red/yellow/green indicators in the UI  
❌ **Confidence Display:** Frontend doesn't show confidence scores to member  
❌ **Signal Transparency:** Member doesn't see why confidence might be medium vs. high  
⚠️ **Caveat Clarity:** Caveats are generated but unclear if they're shown in chat response  

### Impact:
Card 1 has the foundation but doesn't expose veracity to members (correct, per your spec). However, Claude doesn't receive confidence data in tool results to include in explanations.

---

## CARD 2 (UPID - Provider): ~60% Complete

### What IS:
✅ **Backend:** Full provider_lookup.py with River Path across eMedNY → MCO → NPI  
✅ **Basic Confidence:** Three-tier scoring:
  - 0.95 for eMedNY success (authoritative)
  - 0.85 for MCO aggregator (fallback)
  - 0.70 for NPI database (worst case)
  - Flags added for warnings ("Provider found but NOT enrolled")
✅ **HTML Chat:** chat-card2.html with streaming + markdown rendering  
✅ **Tools:** lookup_provider, check_enrollment, validate_claim  
✅ **Response Schema:** ProviderIdentityResponse includes `confidence_score: float`

### What AUGHT (But Isn't):
❌ **Signal-Over-Noise Framework:** No `score_consensus()` like Card 1  
❌ **Caveat Generation:** No formal caveat mechanism; just flags added to list  
❌ **Veracity Visualization:** No red/yellow/green for providers  
❌ **Multi-Source Conflict Handling:** If eMedNY and MCO disagree, no consensus logic  
⚠️ **Claude Integration:** Confidence score returned but unclear if Claude uses it in explanations  

### Impact:
Card 2 returns confidence but lacks the sophisticated signal-over-noise weighting that Card 1 has. This means when sources disagree, there's no principled way to combine their scores.

---

## CARD 3 (WHUP - Plan Admin): 0% Complete

### What IS:
❌ **Backend:** No card_3_uhwp directory exists  
⚠️ **HTML:** chat-card3.html exists but displays "Under development" message  
❌ **Tools:** Empty (CARD_3_TOOLS = [])

### What AUGHT:
✅ **Backend System** with River Path for:
  - Plan member roster lookup
  - Provider directory queries
  - Network adequacy calculations
✅ **Confidence Scoring** for network data (which plans overlap, member counts, adequacy metrics)  
✅ **Signal-Over-Noise:** Multi-source plan data with consensus scoring  
✅ **Veracity Layer:** Red/yellow/green for data reliability (NOT VISIBLE TO PLAN ADMIN)  
✅ **Chat Integration:** Tools wired to Claude with confidence context

### Impact:
Card 3 doesn't exist yet. This is fine for MVP, but when built, MUST include confidence framework from the start.

---

## CARD 4 (USHI - Government Stakeholder): 0% Complete + Missing Spec

### What IS:
❌ **Backend:** No card_4_ushi directory  
⚠️ **HTML:** chat-card4.html exists but is a stub  
❌ **Tools:** Empty (CARD_4_TOOLS = [])  
❌ **Red/Yellow/Green Veracity Layer:** Does not exist

### What AUGHT (Critical):
✅ **Backend System** with River Path for:
  - Aggregate claims data
  - Provider performance metrics
  - Member enrollment trends
  - Compliance dashboards
✅ **Confidence Scoring:** Same framework as Cards 1-3  
✅ **Red/Yellow/Green Veracity Visualization** — Card 4 IS THE ONLY CARD THAT SHOWS THIS  
  - 🟢 **GREEN:** Confidence ≥ 0.85 (HIGH - trust this data)
  - 🟡 **YELLOW:** Confidence 0.60-0.84 (MEDIUM - use with caution)
  - 🔴 **RED:** Confidence < 0.60 (LOW/CRITICAL - escalate or get manual verification)
✅ **Signal Breakdown:** Show:
  - Average confidence from sources
  - Agreement level between sources
  - Which sources were used
  - Why confidence might be below threshold
  - Recommendations for data verification

### Impact:
**This is missing entirely.** The red/yellow/green system doesn't exist anywhere, and Card 4's entire purpose is to expose data reliability to government stakeholders. This MUST be designed before Card 5.

---

## CARD 5 (UBADA - Data Analyst): 0% Complete + Awaiting Card 4 Spec

### What IS:
❌ **Backend:** No card_5_ubada directory  
⚠️ **HTML:** chat-card5.html exists but is a stub  
❌ **Tools:** Empty (CARD_5_TOOLS = [])  
❌ **Data Explorer:** Interactive tables/charts don't exist  
❌ **Collaboration Workspace:** Not implemented  
❌ **Red/Yellow/Green Veracity:** Depends on Card 4 implementation first

### What AUGHT:
✅ **Backend System** with full River Path for:
  - Claims data with outlier detection (z-scores, IQR)
  - Provider performance analytics
  - Member cohort analysis
  - Relationship mapping (provider ↔ member networks)
✅ **Confidence Scoring:** Same framework as Cards 1-4  
✅ **Red/Yellow/Green Visualization** — Like Card 4, but with MORE detail:
  - Data explorer showing confidence per data row
  - Outlier flags with statistical justification
  - Source reliability metrics
  - Data freshness indicators
✅ **Signal-Over-Noise:** Full consensus scoring across multiple data sources  
✅ **Chat Integration:** Claude helps interpret what analysts are seeing  
✅ **Collaboration:** Shared investigations, peer review, commented findings  

### Impact:
Card 5 design is blocked until Card 4's red/yellow/green veracity layer is designed and specified. They share the same visualization patterns; Card 4 is simpler, Card 5 is more detailed.

---

## THE MISSING PIECE: Red/Yellow/Green Veracity Visualization

This system should exist in:
- **Card 4:** Government stakeholder sees reliability of all system data
- **Card 5:** Data analyst sees granular confidence on every data point

### Current State:
- No frontend component exists
- No CSS/HTML for color-coded confidence indicators
- No mapping of numeric confidence scores (0.0-1.0) to color + label
- No documentation in DR.md or architectural protocol

### Aught Design:
```
Confidence Score → Color + Label + Explanation

0.85-1.0 → 🟢 GREEN "HIGH - Verified from authoritative source"
0.60-0.84 → 🟡 YELLOW "MEDIUM - Cross-verified but minor concerns"
<0.60 → 🔴 RED "LOW - Manual verification recommended"

Plus indicator showing:
- Primary data source (state, federal, MCO, etc.)
- Data age (real-time, <24h, <7d, etc.)
- Completeness (all fields, missing some, etc.)
- Agreement level (sources align, partial conflict, major conflict)
```

---

## BLOCKING ISSUES

1. **Card 4 spec doesn't exist** in DR.md or TORQ_E_ARCHITECTURAL_PROTOCOL.md
   - What tools should it have?
   - What veracity visualization design?
   - What data should be exposed?

2. **Confidence data not flowing through Claude** in Cards 1 & 2
   - Tools return confidence scores but Claude doesn't receive them in context
   - Claude's explanations don't reflect the underlying confidence levels

3. **Card 3, 4, 5 backends don't exist**
   - Can't build without River Path implementation
   - Can't test without fake/synthetic data

4. **Red/Yellow/Green UI component doesn't exist**
   - No frontend code for veracity visualization
   - No CSS for status indicators
   - No integration with data explorer (Card 5)

---

## IMMEDIATE NEXT STEPS (Before Building Anything)

1. **Design & Document Card 4 (USHI) in Detail**
   - Backend requirements (River Path, tools, data sources)
   - Veracity visualization design (red/yellow/green, layout)
   - Add to DR.md and TORQ_E_ARCHITECTURAL_PROTOCOL.md

2. **Implement Red/Yellow/Green Component**
   - Reusable UI component for confidence indicators
   - CSS for color-coded status
   - Tooltip showing confidence details
   - Use in both Card 4 & Card 5

3. **Wire Confidence Through Claude**
   - Modify tool execution to pass confidence metadata
   - Update Card 1 & 2 system prompts to reference confidence in explanations
   - Example: "This is based on state data (high confidence) rather than member-reported data (lower confidence)"

4. **Design Card 5 (UBADA) Based on Card 4 Patterns**
   - Use same red/yellow/green visualization
   - Add granular confidence per data row
   - Build data explorer with confidence overlays
   - Add collaboration features

---

## RISK IF WE BUILD WITHOUT THIS

If Card 5 is built without veracity framework:
- ❌ Analysts can't see why data conflicts
- ❌ They can't distinguish signal from noise
- ❌ False positives treated as high-confidence inauthenticity signals
- ❌ We ship the "Medicaid cluster-fuck" problem to our users
- ❌ Later retrofit requires gutting everything

---

## RECOMMENDATION

**Do not build Card 5 yet.**

1. **First:** Design & spec Card 4 completely (with red/yellow/green veracity)
2. **Second:** Build the red/yellow/green UI component (reusable)
3. **Third:** Wire confidence through Claude's responses
4. **Fourth:** Design Card 5 based on Card 4 patterns
5. **Fifth:** Build Card 5 with full confidence framework

This prevents the "disappearing specification" problem and ensures veracity is foundational, not bolted on.
