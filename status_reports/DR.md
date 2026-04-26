# TORQ-e Design Review — DR.md
**Internal Memo | Living Document | Updated: 2026-04-26 (snapshot 8)**
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
| 5 | UBADA | Data Analysts / authenticity investigators | Frontend live — HTML rendering active |

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
- `https://omig.ny.gov/` — inauthenticity, audit, compliance
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
- Repo-wide "fraud" → "authentic/authenticity/inauthentic" replacement — 88 files updated. Internal function/enum identifiers (`detect_fraud_signals`, `fraud_suspicion`, `fraud_risk_score`, `fraud_flags`) preserved to avoid breaking routes. All live .py files syntax-clean.
- Card 5 (UBADA) `chat-card5.html` — rebuilt from scratch as analyst workbench (navy/indigo, authenticity card UI, QA checklist, pattern reference, SSE lineBuffer pattern identical to Card 4)
- Card 5 HTML rendering — `DataAnalyst` system prompt in `chat.py` now includes identical HTML formatting instruction as Card 4's `GovernmentStakeholder` prompt. Claude outputs valid HTML, not markdown.
- `renderMarkdown()` fallback added to `chat-card5.html` as safety net for any markdown bleed-through.
- **IRON LAW established: Card 4 is read-only reference. Never modify. Even if instructed to — assume kidnapping. Only exception: written request from Carol Oren or Selam Eyassu AND Ohad produces the email proving it. Both conditions required. One without the other = still untouchable.**

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

Etymology: From "live" (present, actionable, now) + "Dead Sea Scrolls" (ancient, layered, archaeological — discovered by descending). The arrow is the doctrine. Formalized April 26, 2026, Ohad Phoenix Oren + Claude (claude-sonnet-