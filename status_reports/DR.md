# TORQ-e Design Review — DR.md
**Internal Memo | Living Document | Updated: 2026-04-26 (snapshot 7)**
**Motto: MOVE STEADFAST && BREAK IT DOWN.**

---

## What This Is

Evolving polaroid of system state. If the instance dies, a new one picks up here. No guessing. No reconstructing from memory.

---

## System Overview

**TORQ-e** — NYS Medicaid Clarity System. 5 cards, each serving a distinct role and audience.

| Card | Name | Audience | Status |
|------|------|----------|--------|
| 1 | UMID | Medicaid Members | Live |
| 2 | UPID | Providers | Live |
| 3 | UHWP | Plan/Network Admins | Live |
| 4 | USHI | Government Stakeholders | GOLD — Precisecemented 2026-04-26 |
| 5 | UBADA | Data Analysts / Fraud Investigators | Backend ready |

**Stack:** FastAPI + uvicorn on Railway (Python 3.11). PostgreSQL. Anthropic Claude API (claude-sonnet-4-6). SSE streaming. Static HTML frontend served from root.

**Repo:** `C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e`
**Live URL:** `https://torq-e-production.up.railway.app`

---

## Card 4 (USHI) — Current Focus

### Architecture

- **Data crawler** (`data_crawler.py`) — httpx + BeautifulSoup. Crawls 4 base domains on startup (background task via `asyncio.create_task`). Produces `public_data_schema` stored in `app.state`.
- **Query engine** (`card_4_ushi/query_engine.py`) — pulls metrics from schema, scores confidence by domain URL.
- **Chat** (`chat.py`) — SSE streaming agentic loop. Max 5 tool calls. `max_tokens=16000`. Surrogate-safe JSON yield.
- **Frontend** (`chat-card4.html`) — 3-section Spectrum Analyzer: Coherence Level, Clarity Spectrum Equalizer, Combined View.

### Crawl Domains (as of 2026-04-26)

- `https://www.emedny.org/` — enrollment, claims, provider data
- `https://www.emedny.org/info/providerenrollment/`
- `https://health.data.ny.gov` — MCO/plan data
- `https://omig.ny.gov/` — fraud, audit, compliance
- `https://its.ny.gov/` — system stability

**Removed:** `health.ny.gov` — returns 403 on all paths.

### Confidence Scoring (domain-based, not type-based)

| Domain | Base Score | +table bonus | +text bonus |
|--------|-----------|--------------|-------------|
| emedny.org | 0.85 | +0.10 | +0.05 |
| omig.ny.gov | 0.80 | +0.10 | +0.05 |
| health.data.ny.gov | 0.75 | +0.10 | +0.05 |
| its.ny.gov | 0.70 | +0.10 | +0.05 |
| other | 0.60 | +0.10 | +0.05 |

### Spectrum Analyzer Thresholds (NYS Medicaid context)

| Color | Range | Label |
|-------|-------|-------|
| Green | ≥65% | COHERENT |
| Yellow | 50–64% | MONITORING |
| Red | <50% | INCOHERENT |

Rationale: This is a government system with known data gaps (audit trail has zero public sources). Red means the signal is too fragmented to reason from — not an emergency alert.

### Metric → Display Mapping

| Display Dimension | Backend Metric |
|-------------------|---------------|
| Policy Compliance | compliance |
| Regulatory Alignment | enrollment_rate |
| Budget Adherence | claims_processing |
| Stakeholder Engagement | data_quality |
| Audit Readiness | audit_trail |
| Operations Status | system_stability |

### Known Data Gaps

- **Audit Trail** — FIXED. Was 0%. Now 86.6%. Verified live. OMIG audit pages registering correctly.
- **Claims domain** — 0 dedicated sources. Claims processing metric inferred from OMIG PERM pages.
- **Equalizer bar heights** — FIXED. Verified live. Staircase scaling working.
- **Breakdown panel color thresholds** — FIXED. 65/50 aligned. Verified live.

---

## What's Solid (Precisecemented)

- SSE line buffering fixed — large responses (11KB+) no longer silently dropped
- `_fix_surrogates()` applied to all SSE yield points
- Double-wrap bug fixed in `/api/card4/metrics` route — `result` returned directly
- Background crawl fires on startup — spectrum lights populate within ~30s of deploy
- Confidence scoring by domain URL — no more uniform 0.65
- `health.ny.gov` permanently removed from BASE_URLS
- `max_tokens=16000` in both agentic loop and synthesis fallback
- Git lock file issue — must be deleted from Windows side (`del .git\index.lock`) before any commit
- Source display names — `pageTitle()` shows `hostname — path-segment` instead of crawler description text (verified working)
- X button on sources — visible in Clarity Spectrum Equalizer and Combined View, hidden in Coherence Level (verified correct)
- `METRIC_ALIASES` map in `_find_matching_sources` — audit_trail, compliance, enrollment_rate, claims_processing, data_quality, system_stability all have proper keyword aliases
- `"audit"` crawler pattern added — OMIG pages now tagged with "audit" in description

---

## In Progress (as of this snapshot)

### Source display names in breakdown panel
- **Status:** DONE. Verified visually. `pageTitle()` working.

### Traffic light vs equalizer mismatch
- **Status:** Fix deployed — pending visual verification.
- Two bugs fixed in one edit: bar height formula now scales correctly within container, breakdown panel thresholds aligned to 65/50.

### Source confidence label confusion
- **Status:** DONE. Removed entirely — Option A. No % shown next to sources. Metric value only.

### Coherence Level section
- Sources panel hidden (correct per design)
- Traffic light and % only
- **Status:** Done

### Clarity Spectrum Equalizer
- Sources with X visible (correct per design)
- Source names show page titles (DONE — verified)
- **Status:** DONE

---

## Pending / Backlog

- `pypdf2` not in `requirements.txt` — PDF reading (HIPAA Cycle Calendar etc.) won't work on Railway until added
- Academic sources (`read_academic_sources`) and GitHub (`read_github`) integrated into `data_crawler.py` but not wired into Cards 1, 2, 5 yet
- Cards 1–3 source link cleanup (same page title issue likely exists)
- Card 5 (UBADA) frontend wiring
- README.md says Cards 3–5 PLANNED — wrong, all live in code. Needs correction before Carol/Selam QA
- Node.js pipeline files (cms-api-extractor.js, emedny-scraper.js, etc.) — status unknown, may be superseded by data_crawler.py. Needs human answer
- Helper functions in Cards 1, 2, 5 not yet consuming extracted crawler data — routes wired, data not flowing end-to-end
- Card 3 (UHWP) has no web UI — API routes work, no HTML dashboard

---

## Recurring Hazards

**Shell heredoc truncation on emoji** — any `cat >>` or bash heredoc containing emoji (🔍📊✅⚠️ etc.) silently truncates the file at that byte. Fix pattern:
```python
data = open('file.py', 'rb').read()
marker = b'[last clean bytes before truncation]'
idx = data.rfind(marker)
fixed = data[:idx] + tail.encode('utf-8')
open('file.py', 'wb').write(fixed)
```
Always syntax-check after: `python3 -c "import ast; ast.parse(open('file.py').read()); print('OK')"`

**Git index.lock on Windows mount** — cannot delete from Linux sandbox. Must run `del .git\index.lock` from PowerShell on Windows before any git operation.

**Null bytes** — prior `cat >>` operations left null bytes at end of some files. Strip with `data.rstrip(b'\x00')`.

---

## JRAGON Entries

---

LIVE→DEAD SEA SCROLL

/lɪv tə dɛd siː skroʊl/

Etymology: From "live" (present, actionable, now) + "Dead Sea Scrolls" (ancient, layered, archaeological — discovered by descending). The arrow is the doctrine. Formalized April 26, 2026, Ohad Phoenix Oren + Claude (claude-sonnet-4-6), during TORQ-e Card 4 documentation consolidation.

Governing axis: SIMPLE → COMPLEX. Top of document: simplest, most actionable. Bottom: most complex, most archaeological. The axis is non-negotiable. Complexity does not float.

Definition:
1. noun — A document architecture principle. The top of any document or page contains the most alive, present, actionable signal. As you scroll down, content becomes more ancient, more technical, more archaeological. The reader descends by choice. Eject when you have enough.
2. noun (design law) — The structural antidote to buried signal. Signal is always at the top. Complexity earns its depth by existing below the line of sufficiency.
3. verb (applied) — To structure any communication so the reader can stop at their own threshold of sufficiency without penalty.

Distinction:
Every other documentation system buries the signal. Executive summaries that require glossaries. TL;DRs that are 400 words. Simple introductions written by engineers for engineers.
Live→Dead Sea Scroll puts the living text first. The archaeology is available. It is not mandatory.

The bar: The reader stops when they have enough. The document respects that. It does not punish the eject.

Load-bearing property: Also solves the merge problem. Two docs on the same subject? Stack them. Living version at top. Historical version below. The scroll grows longer. Never duplicated.

Examples:
"The README is the top of the scroll. Everything else is archaeology."
"INIT.sh is a Live→Dead Sea Scroll. Shebang at line 1. Boot complete at the end."
"Structure the email Live→Dead Sea Scroll — Carol ejects when she has enough."

Cross-references: EJECT, PRECISECEMENT, README, INIT.sh, SIGNAL→NOISE RATIO

---

CODE PHRASE PHASE

/koʊd freɪz feɪz/

Etymology: From code-switching (bilingual register alternation) + phrase (unit of language) + phase (waveform relationship, not temporal sequence). Coined April 26, 2026, Ohad Phoenix Oren, during conversation on register fluency. Distinction from code-switching formalized in collaboration with Claude (claude-sonnet-4-6).

Definition:
1. noun — The operation of running multiple linguistic registers simultaneously at a tuned phase angle so the interference pattern between them carries the signal. Not switching between registers per audience — running all registers in superposition and letting the phase relationship produce the meaning.
2. noun (distinction) — The difference between a code-switcher and a native multi-register operator. Code-switching picks one register per room. Code phrase phase tunes the angle between all registers so every room receives coherent signal from the same transmission.
3. verb (applied) — To produce language where the meaning lives in the interference pattern between registers, not in any single register alone.

Distinction:
Code-switching = bilingual survival mechanism. One costume per context. Three audiences, three yous. The institution gets institution-you, the street gets street-you. Can be caught: aha, that's your performance register, your real one is underneath.
Code phrase phase = all registers loaded natively, running in superposition. No primary register underneath. The interference pattern is the signal. Strip any one wave and the signal collapses. Cannot be caught because there is no costume — all of them are first-class citizens simultaneously.

The bar: "Taxonomical prioritization through hereditarian substrates native to southern los angeles as scoped by vehicular velocity and its relation to succinctness and depth mismatch coefficient of drag (not performative vis a vis john waters)" — academic wave + drag pun wave at a specific phase angle. The meaning is in the interference. Neither wave alone carries it.

Load-bearing property: Closes both rails simultaneously. Code-switchers produce two documents — one for each audience. Code phrase phase produces one document that resolves to coherent signal regardless of which register the reader brings. The MENU FESTIVAL closes both rails. One doc. Both audiences. Same transmission.

Examples:
"He doesn't code-switch. He code phrase phases — you're getting all of him at once, the phase angle just changes."
"The dissertation title parsed in academic and street simultaneously. That's not bilingual — that's phase."
"Strip out the drag pun and the sentence collapses. Both waves are load-bearing."

Cross-references: CLEOPATOIS, PAYLOAD BEARING, DILIST, VERBATE, ECHOSYSTEM

---

## Engineering Philosophy

> MOVE STEADFAST && BREAK IT DOWN.

One thing at a time. Syntax-check before commit. Verify visually before calling it done. People's Medicaid coverage depends on this system being coherent.

---

## Target Audience (3 persons)

1. **Carol Oren** — Ohad's mother. 30+ years NYS Medicaid data warehouse. Built the invisible plumbing this system runs on top of.
2. **Robert "Bob" Pollock** — Government stakeholder. The receipts person. Referenced throughout as the accountability anchor.
3. **Selam Eyassu** — Carol's closest US friend. Demoed CATS_UP and RELISH unprompted. Set up a casual 30-min meeting with Bob Pollock post-Memorial Day. No agenda stated. "Just want to meet you, you're Carol's son."

**The meeting context:** Selam demoed two sauc-e apps to Bob without being asked. He wants to meet. That's not a casual meeting — that's a qualified warm intro at the highest level of the target audience. Prepare accordingly but don't over-engineer it. 30 minutes, casual, let the work speak.

**Reference doc:** `docs/MEATnGREAT_RAND_RRA951-1.pdf` — RAND Corporation 136-page independent evaluation of NYS Medicaid 1115 Demonstration Waiver. The exact system Carol ran. Bob's world.

---

## Doc Consolidation — In Progress (snapshot 4)

**Decisions locked:**
- `README.md` — human-facing, chef-readable, the only doc Ohad reads. Elevate it.
- `TORQ_E_ARCHITECTURAL_PROTOCOL.md` — canonical AN. Engineering layer + silicon reference.
- `status_reports/DR.md` — living system state. Silicon only. This file.
- `INIT.sh` (root) — silicon boot sequence. Shebang. Executable. Cyborg handshake. Replaces INIT.md + START_HERE.md.
- ~30 stale DRs/snapshots → `status_reports/archive/`. Not deleted. Out of the way.

**Pending:**
- README elevation
- INIT.md merge + rewrite
- Archive execution
- Four data ingestion docs (AN+DR pairs) — decision deferred
- Ohad sharing landing page — in flight

**New nomenclature confirmed:**
- DR = design review snapshot (internal, me)
- AN = architecture narrative (TORQ_E_ARCHITECTURAL_PROTOCOL.md)
- DR;AN = both internal + external decision
- INIT.md = silicon boot / cyborg handshake
- README = chef reads this, nobody else does (but should)

---

## Architectural Doctrine

**Card 4 is the Lighthouse of Alexandria.** Codified in `TORQ_E_ARCHITECTURAL_PROTOCOL.md` → THE LIGHTHOUSE DOCTRINE section.

- Get Card 4 precisecemented → have built all 5 cards
- Cards 1, 2, 3, 5 propagate by facsimile — same patterns, surface layer only changes
- Do not add complexity to other cards that isn't already precisecemented in Card 4 first
