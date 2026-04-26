# TORQ-e Design Review — DR.md
**Internal Memo | Living Document | Updated: 2026-04-26 (snapshot 5)**
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
| 4 | USHI | Government Stakeholders | Active development — see below |
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

- **Audit Trail** — Was 0.0 confidence. Fix deployed: added `"audit"` pattern to crawler + `METRIC_ALIASES` map in query engine so OMIG audit/PERM pages now register as audit_trail sources. Pending visual verification post-deploy.
- **Claims domain** — 0 dedicated sources. Claims processing metric inferred from OMIG PERM pages.
- **Equalizer bar heights** — Fixed. Was: overflow formula made all bars render at max. Now: `Math.max(3, (value/100) * 45 * (i/5))` — staircase scaling within 45px. Pending visual verification.
- **Breakdown panel color thresholds** — Fixed. Was: 90/70. Now: 65/50 matching NYS Medicaid spectrum. Pending visual verification.

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
- **Problem:** 90% per-source confidence score looks like the metric value to users
- **Fix:** Label needs to read "Source reliability: 90%" not just "90%"
- **Status:** Not yet done

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

## Engineering Philosophy

> MOVE STEADFAST && BREAK IT DOWN.

One thing at a time. Syntax-check before commit. Verify visually before calling it done. People's Medicaid coverage depends on this system being coherent.

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
