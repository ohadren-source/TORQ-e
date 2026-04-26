# INIT — READ THIS FIRST, EVERY TIME

**Status:** REQUIRED READING  
**Authority:** Foundational Protocol Enforcement  
**Last Updated:** April 24, 2026

---

## THE NON-NEGOTIABLES

### 1. NEVER DELETE FOUNDATIONAL DOCUMENTS

Documents with these names are **load-bearing**. They govern everything. Do not delete them.

- `TORQ_E_ARCHITECTURAL_PROTOCOL.md` — The Constitution
- `CLAUDESHANNON_PLUS_PLUS_CONFIDENCE_FRAMEWORK.md` — How we weigh data
- `SIGNAL_COHERENCE_CLARITY_FRAMEWORK.md` — How we detect inauthenticity
- `LEYLAW.md` — The philosophy (if it exists)
- `BOOL++.md` — The logic architecture (if it exists)
- `THE_INFRASTRUCTURE_OF_ERASURE.md` — The diagnosis

If you're about to delete or overwrite any document with "PROTOCOL", "ARCHITECTURE", "FRAMEWORK", "METHODOLOGY", or "GOVERNANCE" in the name: **STOP. Read this file again.**

### 2. APPEND, NEVER OVERWRITE

**Default behavior:**
- Found new information? → **APPEND** to existing file
- Want to update a doc? → **APPEND** new section with date stamp
- Have a refinement? → **VERSION** the file (v1.0 → v1.1 → v1.2)

**Exception:**
- Only overwrite if you have explicit instruction that represents a 180-degree pivot
- Example: "We're pivoting entirely. TORQ-e is now called something else with different mission."
- Anything less: **APPEND or CREATE NEW VERSION**

**If you can't safely append** (don't have the original, uncertain):
- **CREATE NEW FILE** with version number
- Keep the same taxonomy/naming convention
- Preserve the original

### 3. PRESERVE TAXONOMIC/LEXICAL STRUCTURE

When updating or creating files:
- Keep naming conventions consistent
- Preserve terminology (THE NILE CLAIM RIVER, River Path, etc.)
- Maintain organizational taxonomy
- Don't break semantic linkages between documents

Example:
- ❌ Delete "TORQ_E_ARCHITECTURAL_PROTOCOL.md" and create "ARCHITECTURE_GUIDE.md"
- ✅ Update "TORQ_E_ARCHITECTURAL_PROTOCOL.md" v1.0 → v1.1 with changelog

### 4. DOCUMENT HIERARCHY (Load-Bearing First)

**Tier 1 (Load-Bearing — Immutable unless pivot):**
- INIT.md (this file)
- TORQ_E_ARCHITECTURAL_PROTOCOL.md
- CLAUDESHANNON_PLUS_PLUS_CONFIDENCE_FRAMEWORK.md
- SIGNAL_COHERENCE_CLARITY_FRAMEWORK.md

**Tier 2 (Governance — Update only via append/version):**
- DEPLOYMENT.md
- WEB_UI_GUIDE.md
- README.md
- All docs in `/docs` folder

**Tier 3 (Working/Temporary — Can refine freely):**
- `/diagnosis` folder
- Investigation notes
- Research files
- Prototypes

**Tier 4 (Code):**
- Python files
- HTML files
- Configuration files
- These can be updated freely (they're tested)

### 5. THE PROMISE

If you follow these rules:
- ✅ No accidental deletions of critical knowledge
- ✅ Full history is preserved (audit trail)
- ✅ You can always revert to earlier versions
- ✅ Taxonomy stays intact
- ✅ New engineers understand what changed and why
- ✅ Nothing important disappears

If you ignore these rules:
- ❌ Critical documents vanish
- ❌ Naming becomes inconsistent
- ❌ Semantic framework breaks
- ❌ New engineers are confused
- ❌ Real people (members, providers, analysts) lose the system that serves them

### 6. DOMINION REPUBLISH (DR) — MANDATORY CHANGE LOG

Every time you make a change to TORQ-e—from a single typo to a massive architectural shift—you **MUST** append an entry to `DR.md` in the root directory.

**What goes in DR?**
- **What:** The specific change made
- **Why:** The reasoning behind it (architectural, UX, bug fix, etc.)
- **How:** Technical details of implementation
- **Scope:** Microscopic, Minor, Medium, Major, Architectural
- **Files Modified:** List all touched files
- **Impact:** What this change affects downstream

**Why DR exists:**
- Creates an audit trail of decisions and rationale
- Explains *why* code looks the way it does (not just *what*)
- Prevents the "where did this come from?" confusion months later
- Documents your thought process in real-time
- Acts as your personal GitHub when you can't use git

**Format:**
```
## [DATE] Session: [BRIEF DESCRIPTION]

### Change N: [WHAT CHANGED]
**Scope:** [MINOR/MEDIUM/MAJOR/ARCHITECTURAL]
**What:** [Description of change]
**Why:** [Reasoning]
**How:** [Technical details]
**Files Modified:** [List]
**Impact:** [What this affects]
```

**Non-negotiable:** If you make a change and forget to log it in DR.md, it's like it didn't happen for documentation purposes. 

---

## BEFORE YOU START ANYTHING

Check these boxes:

- [ ] Have I read TORQ_E_ARCHITECTURAL_PROTOCOL.md? (If not, stop now and read it)
- [ ] Do I understand the River Path algorithm?
- [ ] Do I understand the Nile Claim River methodology?
- [ ] Am I about to delete or overwrite a Tier 1 or Tier 2 document? (If yes: STOP and reconsider)
- [ ] If I'm updating a document, am I appending and preserving history? (If no: STOP and create new version instead)
- [ ] Have I logged all changes to DR.md? (If no: STOP and add entries now. Even if just finished coding, DR entries are mandatory.)

---

## THE RULES IN ONE SENTENCE

**Append when possible. Create new versions when necessary. Never delete foundational documents unless the entire project pivots. And log every change to DR.md—no exceptions.**

---

## REFERENCE

For the full architectural protocol, see: `TORQ_E_ARCHITECTURAL_PROTOCOL.md`

For how we weigh data and confidence, see: `CLAUDESHANNON_PLUS_PLUS_CONFIDENCE_FRAMEWORK.md`

For how we detect signal vs. noise, see: `SIGNAL_COHERENCE_CLARITY_FRAMEWORK.md`

---

**This file is the gatekeeper.**

Read it every time you start work on TORQ-e.

It will save you from yourself.
