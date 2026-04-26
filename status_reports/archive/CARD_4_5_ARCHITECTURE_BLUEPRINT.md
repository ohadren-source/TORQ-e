# CARD 4 & 5 Architectural Blueprint
## Complete Frontend & Backend Data Flow Documentation

### OVERVIEW
Cards 4 and 5 share an **identical architecture** with **only data source differences**:
- **Card 4 (USHI)**: Aggregate metrics, governance logging, inauthenticity signals, data quality assessment
- **Card 5 (UBADA)**: Full data access, outlier detection, network analysis, investigation cases

---

## PART 1: FRONTEND ARCHITECTURE (chat-cardX.html)

### 1.1 HTML Structure
```
├── Header Container (loads card4-5-header.html)
├── Dev Notice (status banner)
├── Chat Container
│   ├── Messages Div (scrollable, displays history)
│   └── Input Area
│       ├── Textarea (message input)
│       └── Send Button
└── JavaScript Initialization
```

### 1.2 CSS Architecture (3 Main Style Systems)

#### A. Chat UI Styles
- `.messages` - scrollable message area with padding
- `.message` - flex container, animated slideIn
- `.message.user` - right-aligned, dark green background
- `.message.assistant` - left-aligned, light gray background
- `.message-bubble` - max-width 70%, word-wrapped, rounded

#### B. Spectrum Analyzer Styles (THE LIGHTHOUSE)
Core component that displays all data metrics in collapsible sections:

1. **Spectrum Section Container**
   - `.spectrum-analyzer` - main container with border and border-radius
   - `.spectrum-section` - individual collapsible sections with bottom borders
   - `.spectrum-header` - clickable header with toggle icon
   - `.spectrum-content` - content area, collapses with max-height transition

2. **Coherence Level Display (SINGLE LARGE TRAFFIC LIGHT)**
   - `.coherence-display` - centered layout with large circle
   - `.large-traffic-light` - 80x80px circle with gradient background
   - `.large-traffic-light.green` - #4CAF50, 0 0 30px green shadow
   - `.large-traffic-light.yellow` - #FFD700, 0 0 30px yellow shadow
   - `.large-traffic-light.red` - #f44336, 0 0 30px red shadow
   - Displays emoji: ✓ (green), ⚠ (yellow), ✕ (red)

3. **Clarity Spectrum Equalizer (6-DIMENSION GRID)**
   - `.stability-grid` - flex column of items with gaps
   - `.stability-item` - individual metric card
     * Contains: traffic-light + content
     * On hover: translateX(4px), box-shadow
     * On active: background #e8f5e9, border #4CAF50
   - `.stability-item-traffic-light` - 32x32px traffic light
   - `.stability-item-content` - metric name, value, progress bar
   - `.status-bar` - horizontal progress bar, 4px height

4. **Traffic Light Styles**
   - `.traffic-light` - 40px circle with icon
   - `.traffic-light.green` - #4CAF50 gradient with glow
   - `.traffic-light.yellow` - #FFD700 gradient with glow
   - `.traffic-light.red` - #f44336 gradient with glow

#### C. Breakdown Panel & Visuals
- `.breakdown-panel` - white bordered box appearing below clicked metric
- `.breakdown-visuals` - flexbox showing:
  * Traffic light visual (3 stacked circles: red, yellow, green)
  * Equalizer visual (5 bars of varying heights)
- `.source-item` - individual data source link with remove button
- `.confirm-modal` - full-screen modal for confirmations

### 1.3 JavaScript Architecture (4 Main Systems)

#### A. Session & Context Initialization
```javascript
const ushiId = sessionStorage.getItem('ushi_id');
const ubadaId = sessionStorage.getItem('ubada_id');
conversationContext = {
    lastMetricsShown: null,
    ushiId: ushiId,
    userRole: sessionStorage.getItem('user_role') || 'GOVERNANCE_AUTHORITY'
};
```

#### B. Message Flow
1. User types in textarea
2. Click send or press Enter (not Shift+Enter)
3. `sendMessage()` triggered:
   - Extract text
   - Display in UI immediately (user bubble)
   - Call `processGovernanceQuery(message)` - routes to handler
   - Display response (assistant bubble)
   - Enable send button

#### C. Query Routing System
```javascript
processGovernanceQuery(query) routes to:
├── if 'metric' or 'health' or 'status' → handleMetricsQuery()
├── if 'trend' or 'enrollment' or 'volume' → handleTrendQuery()
├── if 'quality' or 'accuracy' or 'data' → handleQualityQuery()
├── if 'governance' or 'flag' or 'alert' → handleGovernanceQuery()
├── if 'help' or 'what can' → getHelpMessage()
└── else → getDefaultResponse()
```

#### D. Core Functions

**generateSpectrumAnalyzer(metrics)**
- Input: Object with 6 metric values: enrollment_rate, claims_processing, data_quality, audit_trail, compliance, system_stability
- Process:
  1. Determine color for each value: green (>=90), yellow (>=70), red (<70)
  2. Calculate coherence score: average of all 6 dimensions
  3. Determine coherence status: COHERENT (>=90), WAVERING (>=70), FRAGMENTED (<70)
  4. Generate HTML with 3 sections (each collapsible):
     - Section 1: Coherence Level (single large traffic light + percentage)
     - Section 2: Clarity Spectrum Equalizer (6 metric items in grid)
     - Section 3: Combined View (both coherence + equalizer)
  5. Attach hidden breakdown-data div with detailed source information

**toggleSpectrumSection(header)**
- Called when section header clicked
- Toggles `.collapsed` class on next `.spectrum-content`
- Animates toggle icon: rotate(-90deg) when collapsed, rotate(0deg) when expanded
- max-height transition: 800px ↔ 0

**showBreakdown(element, metric)**
- Called when metric card clicked
- Removes all other breakdown panels in same section
- Determines section type: Coherence, Stability, or Combined
- Creates breakdown panel with:
  * Traffic light visual (3 circles)
  * Equalizer visual (5 bars)
  * Data source information (links + remove buttons)
  * Calculation logic explanation
  * Detailed breakdown statistics
- Marks element as `.active` (background #e8f5e9)

**removeSourceFromSession(url, name)**
- Shows confirmation modal
- On confirm: adds URL to `sessionStorage.removedSources` (JSON array)
- Removes source item from DOM
- If no sources remain, shows "All sources removed" message

**Handle*Query Functions**
- `handleMetricsQuery()` - fetches `/metrics` endpoint, generates analyzer
- `handleTrendQuery()` - fetches `/metrics`, displays trend details
- `handleQualityQuery()` - fetches `/data-quality`, displays quality breakdown
- `handleGovernanceQuery()` - fetches `/governance-log`, displays alerts/flags
- All have fallback offline functions (getOffline*)
- All include "📖 Elaborate" buttons

#### E. API Communication
```javascript
API_BASE = 'https://torq-e-production.up.railway.app/api/card4'
// Card 5 uses: /api/card5

Endpoints used:
- POST /metrics {metric_type, date_range_days}
- POST /data-quality {domain}
- GET /governance-log?days_back=X&limit=Y
```

---

## PART 2: BACKEND ARCHITECTURE (query_engine.py)

### 2.1 File Structure
```
card_4_ushi/
├── query_engine.py (main logic)
├── schemas.py (Pydantic models)
└── routes.py (FastAPI endpoints)

card_5_ubada/
├── query_engine.py (main logic)
├── schemas.py (Pydantic models)
└── routes.py (FastAPI endpoints)
```

### 2.2 Schemas (Pydantic Models) - IDENTICAL STRUCTURE

#### Request Schemas
```python
class MetricsRequest(BaseModel):
    metric_type: str  # 'enrollment_rate', 'claims_processing', etc.
    date_range_days: int = 30
    filter_by: Optional[str] = None

class DataQualityRequest(BaseModel):
    domain: str  # 'enrollment', 'claims', 'provider_data'
```

#### Response Schemas
```python
class MetricsResponse(BaseModel):
    enrollment_rate: float
    claims_processing: float
    data_quality: float
    audit_trail: float
    compliance: float
    system_stability: float
    confidence_score: float
    freshness: str
    trend: str
    sources: List[str]

class DataQualityResponse(BaseModel):
    quality_score: float
    completeness: float
    accuracy: float
    timeliness: float
    audit_valid: bool
    cms_ready: bool
    last_audit: str
```

### 2.3 Query Engine Functions

#### Card 4 (USHI) - Aggregate Only
```python
async def query_aggregate_metrics(metric_type, date_range_days, filter_by):
    # Returns aggregate percentages ONLY - no individual records
    # Data sources: eMedNY, MCO reporting, CMS data
    # Returns: MetricsResponse with 6-dimension scores

async def detect_fraud_signals(entity_type, threshold_sigma):
    # Statistical anomalies using Z-scores
    # Returns: outlier patterns and counts (de-identified)
    # Example: "47 providers billing >4σ above average"

async def assess_data_quality(domain):
    # Cross-source consistency analysis
    # Analyzes agreement between State DB, MCO, SSA
    # Returns: DataQualityResponse

async def view_governance_log(filter_by, days_back, limit):
    # Immutable audit trail: WHO/WHAT/WHEN/WHY
    # Returns: List of governance flags with justification

async def flag_data_issue(...):
    # Creates governance flag with evidence
    # Logs immutably
```

#### Card 5 (UBADA) - Full Detail Access
```python
async def explore_claims_data(filter_by, aggregation, limit):
    # Full data access with individual records
    # Data sources: Claims database, member records, provider data
    # Returns: Claims data with member/provider details

async def compute_outlier_scores(entity_type, metric, threshold_sigma):
    # Z-score analysis with confidence scoring
    # Individual provider/member/claim patterns
    # Returns: Risk levels (LOW, MEDIUM, HIGH)

async def navigate_relationship_graph(focus_entity, relationship_type, depth):
    # Network exploration: co-billing, referral, facility patterns
    # Returns: Provider/member networks with relationship details

async def create_investigation_project(...):
    # Formal investigation case with team workspace
    # Immutable audit trail for investigation

async def request_data_correction(...):
    # Data correction with approval workflow
    # Logs change reason and evidence
```

### 2.4 Data Flow Pipeline

**Step 1: Frontend Request**
```
User query in textarea
→ processGovernanceQuery() routes to handler
→ Handler calls async fetch() to /api/cardX/endpoint
```

**Step 2: Backend Processing**
```
FastAPI route receives request
→ Query engine executes business logic
→ Query database/external sources
→ Calculate metrics and confidence scores
→ Return Pydantic response model
```

**Step 3: Response Formatting**
```
Backend returns JSON:
{
    "enrollment_rate": 87.3,
    "claims_processing": 95,
    "data_quality": 99,
    "audit_trail": 100,
    "compliance": 98,
    "system_stability": 96,
    "confidence_score": 0.92,
    "freshness": "Updated daily",
    "trend": "Stable"
}
```

**Step 4: Frontend Rendering**
```
generateSpectrumAnalyzer(metrics)
→ Calculate colors and coherence
→ Generate HTML with 3 sections
→ Display in message bubble
```

---

## PART 3: KEY ARCHITECTURAL PATTERNS

### 3.1 The 6-Dimension Clarity Spectrum Equalizer

**Dimensions** (identical for Cards 4 & 5, different data sources):
1. **Enrollment Rate** - Card 4: aggregate % | Card 5: individual member status
2. **Claims Processing** - Card 4: aggregate throughput | Card 5: individual claim details
3. **Data Quality** - Card 4: cross-source agreement | Card 5: claims data integrity
4. **Audit Trail** - Card 4: governance logs | Card 5: investigation case logs
5. **Compliance** - Card 4: policy adherence % | Card 5: investigation status
6. **System Stability** - Card 4: uptime % | Card 5: analysis tool availability

**Metric Calculation Logic:**
- Each dimension gets a percentage score (0-100)
- Coherence = average of all 6 dimensions
- Color coding:
  * GREEN (🟢): >=90% (✓ checkmark)
  * YELLOW (🟡): 70-89% (⚠ warning)
  * RED (🔴): <70% (✕ close)

### 3.2 Data Source Transparency (Removable Citations)

**For Stability & Combined sections:**
- Each metric has sourceUrls array
- Display links: [Name](URL)
- Allow user to remove sources temporarily
- Store in sessionStorage.removedSources
- Re-query doesn't happen (user removed source from session view)

### 3.3 Collapsible Sections Pattern

**3 sections, ALL collapsible:**
1. **Coherence Level** - single large traffic light + percentage + status text
2. **Clarity Spectrum Equalizer** - 6 metric cards in grid
3. **Combined View** - coherence + spectrum in one view

**Toggle Behavior:**
- Click section header → toggle collapsed
- Icon rotates: ▶ (collapsed) ↔ ▼ (expanded)
- Content max-height animates: 0 ↔ 800px

### 3.4 Breakdown Panel Pattern

**On metric card click:**
- Expands breakdown panel below that card
- Shows:
  * Visual: traffic light circles (red/yellow/green stacked)
  * Visual: equalizer bars (5 bars, height = value/100 * 50 * (i/5))
  * Data source list with remove buttons
  * Calculation logic explanation
  * Detailed breakdown statistics

**Data Structure:**
```javascript
const breakdownData = {
    "Enrollment Rate": {
        value: 87.3,
        source: "State Medicaid Database, MCO Reporting",
        sourceUrls: [
            { name: "NYS DOH Medicaid", url: "..." },
            { name: "eMedNY Enrollment Portal", url: "..." }
        ],
        logic: "Active members / eligible population × 100",
        breakdown: "Current: 1,250,000 | Eligible: 1,432,000 | New: +12,500"
    },
    ...
}
```

---

## PART 4: IMPLEMENTATION CHECKLIST

### When Creating Card 5 from Card 4 Template:

**HTML (chat-card5.html)**
- [ ] Change API_BASE from `/api/card4` to `/api/card5`
- [ ] Update dev notice from "Card 4 backend ready..." to "Card 5 backend ready..."
- [ ] Update placeholder message to Card 5 role
- [ ] Load correct header: card4-5-header.html (shared)
- [ ] All CSS stays identical - just different data

**JavaScript Functions**
- [ ] Keep ALL query routing logic identical
- [ ] Keep generateSpectrumAnalyzer() identical
- [ ] Keep toggleSpectrumSection() identical
- [ ] Keep showBreakdown() identical
- [ ] Keep source removal logic identical
- [ ] Update handle*Query() functions to call /api/card5 endpoints
- [ ] Update offline fallback data to Card 5 context (authenticity patterns vs governance)

**Backend (card_5_ubada/query_engine.py)**
- [ ] Implement same function signatures as Card 4
- [ ] Use same response schemas (MetricsResponse, DataQualityResponse)
- [ ] Use same 6-dimension structure
- [ ] ONLY difference: data sources and business logic
  * Card 4: State DB, MCO systems, governance logs
  * Card 5: Claims DB, provider networks, investigation cases

**Schemas (card_5_ubada/schemas.py)**
- [ ] Use IDENTICAL Pydantic models to Card 4
- [ ] No schema changes needed

**Routes (card_5_ubada/routes.py)**
- [ ] Implement async handlers for endpoints
- [ ] Return same response schemas
- [ ] Include confidence_score in responses
- [ ] Include freshness, trend, sources metadata

---

## PART 5: THE ONLY DIFFERENCES (Card 4 vs Card 5)

| Aspect | Card 4 (USHI) | Card 5 (UBADA) |
|--------|---------------|----------------|
| **Role** | Government Stakeholder | Data Analyst |
| **Data Access** | Aggregate only | Full detail |
| **Data Sources** | State DB, MCO, CMS | Claims DB, Networks |
| **Metrics Interpretation** | Policy compliance | authenticity verification |
| **Breakdown Details** | Governance logs | Investigation cases |
| **API Endpoint** | /api/card4 | /api/card5 |
| **Query Functions** | query_aggregate_metrics, detect_fraud_signals, assess_data_quality, view_governance_log, flag_data_issue | explore_claims_data, compute_outlier_scores, navigate_relationship_graph, create_investigation_project, request_data_correction |
| **UI Elements** | IDENTICAL - same Spectrum Analyzer, same 6 dimensions, same colors, same collapse behavior |
| **Breakdown Data** | Policy/compliance context | Investigation context |

---

## PART 6: DEPLOYMENT CHECKLIST

- [ ] Card 5 HTML uses /api/card5 endpoints
- [ ] Card 5 backend implements all 5 query functions
- [ ] Both cards return MetricsResponse with identical structure
- [ ] Session context: ubada_id read and passed to backend
- [ ] Spectrum Analyzer generates identically
- [ ] Collapsible sections work identically
- [ ] Breakdown panels display identically
- [ ] Source removal works identically
- [ ] Offline fallbacks work for Card 5
- [ ] All 6 dimensions display with correct colors

---

## VERIFICATION: Card 4 vs Card 5 Screenshots Match

**UI Match Checklist:**
- [ ] Large coherence traffic light (80x80px) displays in Coherence Level
- [ ] 6 metric cards display in Clarity Spectrum Equalizer
- [ ] Each metric has traffic light + progress bar + value %
- [ ] Cards are clickable → breakdown panels expand below
- [ ] Breakdown shows traffic light visual + equalizer visual
- [ ] Data sources are clickable links
- [ ] Source removal buttons (✕) work with confirmation modal
- [ ] Collapses/expands smoothly
- [ ] Three sections: Coherence, Equalizer, Combined - all collapsible
- [ ] Icons rotate: ▶ (collapsed) → ▼ (expanded)

