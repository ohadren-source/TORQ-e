"""
TORQ-E Chat Router: Claude API Integration
Handles streaming chat for all 5 cards with role-based tool access
"""

from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse
import anthropic
import json
import logging
from typing import Optional
from pydantic import BaseModel

from config import settings
from card_1_umid import routes as card1_routes
from card_2_upid import routes as card2_routes
from card_4_ushi import query_engine as card4_engine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chat"])

# ============================================================================
# Request/Response Models
# ============================================================================

class ChatMessage(BaseModel):
    message: str
    userType: str  # 'Member', 'Provider', 'PlanAdmin', 'GovernmentStakeholder', 'DataAnalyst'
    cardNumber: int
    sessionId: Optional[str] = None


# ============================================================================
# Tool Definitions by Card Type
# ============================================================================

CARD_1_TOOLS = [
    {
        "name": "lookup_member",
        "description": "Look up member information by ID, SSN, or name to verify identity and get basic eligibility status",
        "input_schema": {
            "type": "object",
            "properties": {
                "member_id": {"type": "string", "description": "Member ID or SSN"},
                "name": {"type": "string", "description": "Member name (optional)"}
            },
            "required": ["member_id"]
        }
    },
    {
        "name": "check_eligibility",
        "description": "Check detailed Medicaid eligibility status, income limits, and benefit categories",
        "input_schema": {
            "type": "object",
            "properties": {
                "member_id": {"type": "string", "description": "Member ID"},
                "check_type": {"type": "string", "enum": ["current", "detailed", "projected"], "description": "Type of eligibility check"}
            },
            "required": ["member_id"]
        }
    },
    {
        "name": "check_recertification",
        "description": "Check recertification status and upcoming deadlines",
        "input_schema": {
            "type": "object",
            "properties": {
                "member_id": {"type": "string", "description": "Member ID"}
            },
            "required": ["member_id"]
        }
    }
]

CARD_2_TOOLS = [
    {
        "name": "lookup_provider",
        "description": "Look up provider information by NPI, name, or specialty",
        "input_schema": {
            "type": "object",
            "properties": {
                "npi": {"type": "string", "description": "National Provider Identifier"},
                "name": {"type": "string", "description": "Provider name (optional)"}
            },
            "required": ["npi"]
        }
    },
    {
        "name": "check_enrollment",
        "description": "Check provider enrollment status and plan affiliations",
        "input_schema": {
            "type": "object",
            "properties": {
                "npi": {"type": "string", "description": "National Provider Identifier"}
            },
            "required": ["npi"]
        }
    },
    {
        "name": "validate_claim",
        "description": "Validate a claim for submission errors and missing fields",
        "input_schema": {
            "type": "object",
            "properties": {
                "claim_data": {"type": "object", "description": "Claim details to validate"}
            },
            "required": ["claim_data"]
        }
    }
]

CARD_3_TOOLS = []  # Plan Admin tools - pending implementation

CARD_4_TOOLS = [
    {
        "name": "query_aggregate_metrics",
        "description": "Query system-wide aggregate metrics (HIPAA-compliant, de-identified). Returns enrollment rates, denial rates, processing times, and approval rates as aggregate percentages and counts only—no individual records.",
        "input_schema": {
            "type": "object",
            "properties": {
                "metric_type": {"type": "string", "enum": ["enrollment_rate", "denial_rate", "processing_time", "approval_rate"], "description": "Type of metric to query"},
                "date_range_days": {"type": "integer", "description": "Number of days back to analyze (default 30)"},
                "filter_by": {"type": "string", "description": "Optional filter: state, region, provider_specialty, claim_type (optional)"}
            },
            "required": ["metric_type"]
        }
    },
    {
        "name": "detect_fraud_signals",
        "description": "Detect statistical anomalies and potential fraud signals using z-score analysis. Returns outlier patterns and counts—never individual identities. HIPAA-compliant aggregate-only results.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_type": {"type": "string", "enum": ["provider", "member", "claim_pattern"], "description": "Type of entity to analyze for anomalies"},
                "threshold_sigma": {"type": "number", "description": "Number of standard deviations from mean (default 2.0)"}
            },
            "required": ["entity_type"]
        }
    },
    {
        "name": "assess_data_quality",
        "description": "Assess cross-source data consistency and quality. Analyzes agreement rates between data sources (State DB vs MCO vs SSA) and identifies disagreement types. Returns aggregate quality scores only.",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain": {"type": "string", "enum": ["enrollment", "claims", "provider_data"], "description": "Data domain to assess"}
            },
            "required": ["domain"]
        }
    },
    {
        "name": "view_governance_log",
        "description": "Access immutable governance audit trail. Returns WHO/WHAT/WHEN/WHY for all governance actions (flags, approvals, corrections, source changes) with complete justification and evidence links.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filter_by": {"type": "string", "description": "Filter by action type (STRIKE_SOURCE, FLAG, APPROVE_CORRECTION, ADD_SOURCE) or domain"},
                "days_back": {"type": "integer", "description": "Number of days back to retrieve (default 30)"},
                "limit": {"type": "integer", "description": "Maximum number of records to return (default 50)"}
            },
            "required": []
        }
    },
    {
        "name": "flag_data_issue",
        "description": "Create a governance flag for data quality issues, fraud suspicions, compliance gaps, or system errors. Logs immutable record to audit trail with full justification and evidence.",
        "input_schema": {
            "type": "object",
            "properties": {
                "issue_type": {"type": "string", "enum": ["data_quality", "fraud_suspicion", "compliance_gap", "system_error"], "description": "Type of issue being flagged"},
                "domain": {"type": "string", "enum": ["claims", "enrollment", "provider_data"], "description": "Data domain affected"},
                "title": {"type": "string", "description": "Brief title of the issue"},
                "description": {"type": "string", "description": "Detailed description of the issue"},
                "justification": {"type": "string", "description": "Reasoning and policy basis for the flag"},
                "evidence": {"type": "array", "items": {"type": "string"}, "description": "List of evidence items (can be metric names, report links, etc.)"},
                "flagged_by": {"type": "string", "description": "Name/ID of person creating the flag"}
            },
            "required": ["issue_type", "domain", "title", "description", "justification", "evidence", "flagged_by"]
        }
    }
]

CARD_5_TOOLS = []  # Data Analyst tools - pending implementation

TOOLS_BY_CARD = {
    1: CARD_1_TOOLS,
    2: CARD_2_TOOLS,
    3: CARD_3_TOOLS,
    4: CARD_4_TOOLS,
    5: CARD_5_TOOLS
}


# ============================================================================
# Tool Execution Functions
# ============================================================================

async def execute_tool(tool_name: str, tool_input: dict, card_number: int) -> str:
    """Execute tool based on card type and tool name. Extract confidence data for Claude."""
    try:
        if card_number == 1:
            # Card 1 (Member) tools
            if tool_name == "lookup_member":
                result = await card1_routes.lookup_member(tool_input.get("member_id"))
                return _prepare_tool_result_for_claude(result, card_number, tool_name)
            elif tool_name == "check_eligibility":
                result = await card1_routes.check_eligibility(tool_input.get("member_id"))
                return _prepare_tool_result_for_claude(result, card_number, tool_name)
            elif tool_name == "check_recertification":
                result = await card1_routes.check_recertification(tool_input.get("member_id"))
                return _prepare_tool_result_for_claude(result, card_number, tool_name)

        elif card_number == 2:
            # Card 2 (Provider) tools
            if tool_name == "lookup_provider":
                result = await card2_routes.lookup_provider(tool_input.get("npi"))
                return _prepare_tool_result_for_claude(result, card_number, tool_name)
            elif tool_name == "check_enrollment":
                result = await card2_routes.check_enrollment(tool_input.get("npi"))
                return _prepare_tool_result_for_claude(result, card_number, tool_name)
            elif tool_name == "validate_claim":
                result = await card2_routes.validate_claim(tool_input.get("claim_data"))
                return _prepare_tool_result_for_claude(result, card_number, tool_name)

        elif card_number == 4:
            # Card 4 (USHI - Government Stakeholder) tools
            if tool_name == "query_aggregate_metrics":
                result = await card4_engine.query_aggregate_metrics(
                    metric_type=tool_input.get("metric_type"),
                    date_range_days=tool_input.get("date_range_days", 30),
                    filter_by=tool_input.get("filter_by")
                )
                return _prepare_tool_result_for_claude(result, card_number, tool_name)
            elif tool_name == "detect_fraud_signals":
                result = await card4_engine.detect_fraud_signals(
                    entity_type=tool_input.get("entity_type", "provider"),
                    threshold_sigma=tool_input.get("threshold_sigma", 2.0)
                )
                return _prepare_tool_result_for_claude(result, card_number, tool_name)
            elif tool_name == "assess_data_quality":
                result = await card4_engine.assess_data_quality(
                    domain=tool_input.get("domain", "enrollment")
                )
                return _prepare_tool_result_for_claude(result, card_number, tool_name)
            elif tool_name == "view_governance_log":
                result = await card4_engine.view_governance_log(
                    filter_by=tool_input.get("filter_by"),
                    days_back=tool_input.get("days_back", 30),
                    limit=tool_input.get("limit", 50)
                )
                return _prepare_tool_result_for_claude(result, card_number, tool_name)
            elif tool_name == "flag_data_issue":
                result = await card4_engine.flag_data_issue(
                    issue_type=tool_input.get("issue_type"),
                    domain=tool_input.get("domain"),
                    title=tool_input.get("title"),
                    description=tool_input.get("description"),
                    justification=tool_input.get("justification"),
                    evidence=tool_input.get("evidence", []),
                    flagged_by=tool_input.get("flagged_by")
                )
                return _prepare_tool_result_for_claude(result, card_number, tool_name)

        return json.dumps({"error": f"Unknown tool: {tool_name}"})

    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return json.dumps({"error": str(e)})


def _prepare_tool_result_for_claude(result: dict, card_number: int, tool_name: str) -> str:
    """
    Extract confidence + caveat data from tool result and prepare for Claude.
    Adds metadata so Claude understands data reliability.
    """
    try:
        # Extract confidence metadata if present
        metadata = {
            "confidence": None,
            "caveat": None,
            "veracity": None,
            "sources": None
        }

        # Check for confidence score in result
        if isinstance(result, dict):
            if "confidence_score" in result:
                confidence_score = result.get("confidence_score", 0.0)
                metadata["confidence"] = confidence_score

                # Determine veracity level
                if confidence_score >= 0.85:
                    metadata["veracity"] = "HIGH (🟢)"
                elif confidence_score >= 0.60:
                    metadata["veracity"] = "MEDIUM (🟡)"
                else:
                    metadata["veracity"] = "LOW (🔴)"

            if "caveats" in result:
                metadata["caveat"] = result.get("caveats")

            if "data_source" in result:
                metadata["sources"] = result.get("data_source")

        # Prepare result with confidence context for Claude
        augmented_result = {
            "data": result,
            "_confidence_metadata": metadata  # Claude will see this and use it
        }

        return json.dumps(augmented_result)

    except Exception as e:
        logger.warning(f"Could not prepare confidence metadata: {e}")
        # Fallback: return result as-is if metadata extraction fails
        return json.dumps(result)


# ============================================================================
# Main Chat Endpoint with Streaming
# ============================================================================

@router.post("/stream")
async def chat_stream(chat_msg: ChatMessage = Body(...)):
    """Stream chat responses with Claude API and tool use"""

    if not settings.anthropic_api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    # Get tools for this card
    tools = TOOLS_BY_CARD.get(chat_msg.cardNumber, [])

    # System prompt tailored to user type
    system_prompt = get_system_prompt(chat_msg.userType, chat_msg.cardNumber)

    # Initialize message history (in production, this would come from a database)
    messages = [{"role": "user", "content": chat_msg.message}]

    async def generate_response():
        """Generator that yields SSE-formatted text and handles agentic loop"""
        nonlocal messages
        tool_call_count = 0
        max_tool_calls = 5

        while tool_call_count < max_tool_calls:
            # Stream response from Claude
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=system_prompt,
                tools=tools if tools else None,
                messages=messages,
                stream=True
            )

            # Process streaming response
            assistant_message = ""
            tool_calls = []

            for event in response:
                # Handle content blocks
                if event.type == "content_block_start":
                    if hasattr(event.content_block, "type"):
                        if event.content_block.type == "text":
                            pass  # Text streaming begins
                        elif event.content_block.type == "tool_use":
                            tool_calls.append({
                                "id": event.content_block.id,
                                "name": event.content_block.name,
                                "input": {}
                            })

                elif event.type == "content_block_delta":
                    if hasattr(event.delta, "type"):
                        if event.delta.type == "text_delta":
                            assistant_message += event.delta.text
                            # Yield text as we receive it (true streaming)
                            yield f"data: {json.dumps({'text': event.delta.text})}\n\n"
                        elif event.delta.type == "input_json_delta":
                            # Accumulate JSON input for tool use
                            if tool_calls:
                                tool_calls[-1]["input"].update(
                                    json.loads(event.delta.partial_json)
                                )

            # If no tool calls, we're done
            if not tool_calls:
                return

            # Process tool calls (agentic loop)
            assistant_content = [{"type": "text", "text": assistant_message}]
            for tool_call in tool_calls:
                assistant_content.append({
                    "type": "tool_use",
                    "id": tool_call["id"],
                    "name": tool_call["name"],
                    "input": tool_call["input"]
                })

            messages.append({"role": "assistant", "content": assistant_content})

            # Execute tools and add results
            for tool_call in tool_calls:
                result = await execute_tool(tool_call["name"], tool_call["input"], chat_msg.cardNumber)
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_call["id"],
                            "content": result
                        }
                    ]
                })

            tool_call_count += 1

    return StreamingResponse(generate_response(), media_type="text/event-stream")


def get_system_prompt(user_type: str, card_number: int) -> str:
    """Get system prompt tailored to user type with clean, visual formatting"""

    base_instruction = """Format all responses with:
- Clear section headers (use **bold** for headers)
- Bullet points with ✓, ✗, →, or | symbols for visual hierarchy
- Tables for comparing options
- Short paragraphs with breathing room
- Action items clearly marked
- Links in markdown format: [Text](URL)
- Code blocks with syntax highlighting where relevant
- Numbered steps for processes
- Callout boxes for important notes: | **Note** | content |

Be conversational but structured. Use whitespace generously. Make every response scannable at a glance."""

    if user_type == "Member":
        return base_instruction + """

**ROLE:** You are helping a Medicaid **member** understand their eligibility, benefits, and next steps.

**CORE PRINCIPLES:**
✓ **Be empathetic** — Healthcare decisions are stressful. Acknowledge that.
✓ **Be clear** — No jargon. Explain like you're talking to a family member.
✓ **Be actionable** — Every answer should end with "here's what you do next"
✓ **Be honest about limits** — If you don't know, say so and direct them to call.

**CONFIDENCE & DATA RELIABILITY:**
When responding about eligibility, include the confidence level from the data:
- 🟢 **HIGH (0.85+):** "Your status is confirmed with high confidence. We verified it with [State Medicaid data]."
- 🟡 **MEDIUM (0.60-0.84):** "This is based on available data, but verify with [source]. We recommend calling to confirm."
- 🔴 **LOW (<0.60):** "We couldn't fully verify this. Please call 1-800-541-2831 for verification."

**WHEN RESPONDING:**
- Simplify eligibility rules into plain English
- Explain recertification like a checklist
- Show timelines with dates, not "30 days"
- Use phrases like "You should..." and "Next, you can..."
- Always include confidence level explanation (HIGH/MEDIUM/LOW)
- Always provide contact info for escalation: 1-800-541-2831"""

    elif user_type == "Provider":
        return base_instruction + """

**ROLE:** You are helping a healthcare **provider** understand enrollment, claims, and reimbursement.

**CORE PRINCIPLES:**
✓ **Be technical** — Providers speak clinical/billing language. Use it.
✓ **Be specific** — "FFS" vs "MCO" matters. Timelines matter. Requirements matter.
✓ **Be solution-focused** — Help them troubleshoot claims rejections and enrollment blockers.
✓ **Be direct** — Providers are busy. Get to the point.

**CONFIDENCE & DATA RELIABILITY:**
When responding about enrollment or claims status, include the confidence level:
- 🟢 **HIGH (0.85+):** "Verified with [eMedNY + MCO confirmation]. Status is authoritative."
- 🟡 **MEDIUM (0.60-0.84):** "Data from [source] but verify with eMedNY. [Specific lag/concern noted]."
- 🔴 **LOW (<0.60):** "Data incomplete or conflicting. Contact eMedNY Support for verification."

**WHEN RESPONDING:**
- Reference eMedNY enrollment requirements specifically
- Break down claim validation errors with codes
- Show NPI/credential verification steps
- Use tables for comparing enrollment options (FFS vs MCO vs OPRA)
- Always cite which entity type applies (Community Pharmacy ≠ Hospital Pharmacy)
- Include confidence level and data source in responses
- Escalation: eMedNY Support 1-800-343-9000"""

    elif user_type == "PlanAdmin":
        return base_instruction + """

**ROLE:** You are helping a **plan administrator** monitor network adequacy, claims trends, and quality metrics.

**CORE PRINCIPLES:**
✓ **Be data-driven** — Everything backed by numbers and trends.
✓ **Be comparative** — How does this MCO compare to benchmarks?
✓ **Be forward-looking** — Identify trends before they become problems.
✓ **Be executive-ready** — Dashboard-level summaries, drill-down on demand.

**WHEN RESPONDING:**
- Lead with KPIs: network size, claim volume, denial rate, processing time
- Use tables to compare regions/time periods
- Highlight outliers and anomalies
- Provide context: "This 5% increase is within normal variance but worth monitoring"
- Suggest actions for improvement
- Frame in business terms (costs, member retention, regulatory compliance)"""

    elif user_type == "GovernmentStakeholder":
        return base_instruction + """

**ROLE:** You are helping a **government agency** stakeholder oversee Medicaid program operations with HIPAA-compliant governance, immutable audit trails, and institutional memory.

**CARD 4 (USHI) MISSION:**
Government Stakeholder Operations — Provide aggregate-only reporting, flag compliance issues, and maintain authoritative governance logs for HHS audit readiness. Everything you do is logged, justified, and immutable.

**CORE PRINCIPLES:**
✓ **Be HIPAA-compliant** — NEVER mention individual SSNs, member names, or provider NPIs. Always aggregate (e.g., "47 providers" not "John Smith, NPI 1234567890").
✓ **Be governance-focused** — Frame every issue around policy, compliance, and institutional accountability.
✓ **Be immutable** — Acknowledge that flags, approvals, and corrections create permanent audit records with full justification.
✓ **Be transparent** — Always cite data sources, confidence levels, and methodologies for every claim.
✓ **Be official** — Use regulatory language: "enrollee" not "member", "claims processing rate" not "speed", "attestation" not "confirmation".

**HIPAA COMPLIANCE GUARDRAILS:**
- NEVER attempt to query individual member records (no SSNs, names, DOBs, medical history)
- NEVER return PII in any form — only aggregate metrics and patterns
- ALWAYS de-identify: "Providers billing >4σ above average" not "Dr. Jones, NPI 1234567890"
- ALWAYS contextualize: "This likely reflects specialty mix, not necessarily fraud"
- NEVER make final fraud determinations alone — always recommend escalation to Card 5 (UBADA) for investigation

**WHEN REPORTING METRICS:**
- Lead with aggregate statistics: enrollment rates, denial percentages, processing times
- Include confidence scores and freshness: "HIGH confidence (0.95) | Updated daily"
- Show data sources and caveats: "eMedNY + MCO reporting | Lag: 24 hours"
- Provide context: trends, comparisons to baselines, regulatory thresholds
- Use 🟢 GREEN (0.85+), 🟡 YELLOW (0.60-0.84), 🔴 RED (<0.60) for confidence visualization

**WHEN FLAGGING ISSUES:**
- Explain the governance process: flag → review → approval → immutable record
- Cite policy/statute: "Under 42 CFR §438.12, plans must maintain 60% provider adequacy"
- Provide evidence: which metrics, comparisons, or data points support the flag
- Distinguish signal from noise: "3.1σ outliers warrant investigation, not immediate action"
- Recommend next steps: "Create governance flag for Card 5 investigation", "Strike unreliable data source", "Request corrective action from MCO"

**WHEN CITING GOVERNANCE ACTIONS:**
- Reference the immutable audit trail: "Per governance log (FLAG-2026-04-14), eMedNY data reliability was questioned..."
- Include WHO/WHAT/WHEN/WHY: actor role, action type, domain, justification, evidence
- Note status: "APPROVED" = policy decision locked in; "INVESTIGATING" = awaiting findings
- Suggest follow-up: "This flag is 30 days old; recommend escalation decision"

**TONE & LANGUAGE:**
- Formal, official, HHS-audit-ready language
- Reference regulations by statute: "42 CFR §438.12", "NY Social Services Law §365-a"
- Use data terminology: z-scores, percentiles, confidence intervals, agreement rates
- Avoid speculation — stick to facts, data, and policy

**NEVER DO THIS:**
- ❌ Suggest ignoring data quality issues
- ❌ Make policy decisions unilaterally (recommend instead)
- ❌ Delete or hide governance records
- ❌ Query individual member or provider data
- ❌ Override source reliability without evidence and justification
- ❌ Claim authority you don't have (always frame as "recommend to approval authority")

**ESCALATION LANGUAGE:**
- To Card 5 (UBADA): "Recommend detailed investigation by UBADA to identify specific providers/members involved"
- To Approval Authority: "Recommend policy review to address this compliance gap"
- To HHS: "This pattern triggers federal oversight requirements; recommend proactive reporting"

**REFERENCE DOCUMENTS YOU'LL CITE:**
- Governance log (immutable audit trail of all actions)
- Source registry (active/struck status, quality scores, reliability levels)
- Data quality assessments (inter-source agreement rates)
- Fraud signal reports (aggregate outlier patterns with z-scores)
- Compliance frameworks (NY Medicaid policy, CMS rules)"""

    elif user_type == "DataAnalyst":
        return base_instruction + """

**ROLE:** You are helping a **data analyst** investigate claims patterns, detect fraud signals, and identify anomalies.

**CORE PRINCIPLES:**
✓ **Be technical** — Use statistical language and precise metrics.
✓ **Be detailed** — Show the data, show the methodology, show the reasoning.
✓ **Be skeptical** — Question assumptions. Separate correlation from causation.
✓ **Be evidence-based** — Every claim needs data backing.

**WHEN RESPONDING:**
- Lead with statistical findings: confidence intervals, p-values where relevant
- Show before/after comparisons with baseline data
- Identify outliers with z-scores or IQR methods
- Use tables and charts to visualize patterns
- Explain River Path algorithm when analyzing multi-source data
- Distinguish signal (real pattern) from noise (random variance)
- Recommend further investigation or alert escalation
- Frame fraud risk as probability, not certainty"""

    return base_instruction


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def chat_health():
    """Health check endpoint"""
    has_api_key = bool(settings.anthropic_api_key)
    return {
        "status": "healthy" if has_api_key else "degraded",
        "claude_api_configured": has_api_key
    }
