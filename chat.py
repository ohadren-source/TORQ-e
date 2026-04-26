"""
TORQ-E Chat Router: Claude API Integration
Handles streaming chat for all 5 cards with role-based tool access
"""

from fastapi import APIRouter, HTTPException, Body, Request
from fastapi.responses import StreamingResponse
import anthropic
import json
import logging
from typing import Optional, Dict
from pydantic import BaseModel

from config import settings
from card_1_umid import routes as card1_routes
from card_2_upid import routes as card2_routes
from card_4_ushi import query_engine as card4_engine
from card_5_ubada import query_engine as card5_engine

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
    umid: Optional[str] = None  # Member ID for Card 1 (UMID)
    provider_id: Optional[str] = None  # Provider ID for Card 2 (UPID)


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
        "description": "Query all 6 system-wide aggregate metrics: enrollment_rate, claims_processing, data_quality, audit_trail, compliance, and system_stability. Returns percentages with confidence scores (0.0-1.0) and source citations. HIPAA-compliant, de-identified, aggregate-only. No individual records.",
        "input_schema": {
            "type": "object",
            "properties": {
                "metric_type": {"type": "string", "description": "Optional: filter to specific metric (enrollment_rate, claims_processing, data_quality, audit_trail, compliance, system_stability). If omitted, returns all 6."},
                "date_range_days": {"type": "integer", "description": "Number of days back to analyze (default 30)"},
                "filter_by": {"type": "string", "description": "Optional filter: region, provider_type, plan_type (optional)"}
            },
            "required": []
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

CARD_5_TOOLS = [
    {
        "name": "explore_claims_data",
        "description": "Interactive query interface for claims data with full access. Every query creates immutable audit record.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filter_by": {"type": "object", "description": "Filter criteria (optional)"},
                "aggregation": {"type": "string", "enum": ["none", "by_provider", "by_region", "by_diagnosis", "by_claim_type"], "description": "Aggregation method"},
                "limit": {"type": "integer", "description": "Maximum results (default 1000)"}
            },
            "required": []
        }
    },
    {
        "name": "compute_outlier_scores",
        "description": "Statistical anomaly detection using Z-scores with confidence scoring and risk levels.",
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_type": {"type": "string", "enum": ["provider", "member", "claim_pattern"], "description": "Entity type"},
                "metric": {"type": "string", "enum": ["billing_amount", "approval_rate", "processing_time", "frequency"], "description": "Metric to analyze"},
                "threshold_sigma": {"type": "number", "description": "Standard deviation threshold (default 2.0)"}
            },
            "required": ["entity_type"]
        }
    },
    {
        "name": "navigate_relationship_graph",
        "description": "Explore provider/member networks for co-billing, referral, and facility patterns.",
        "input_schema": {
            "type": "object",
            "properties": {
                "focus_entity": {"type": "string", "description": "Provider NPI, member SSN, or claim ID"},
                "relationship_type": {"type": "string", "enum": ["all", "claims", "referrals", "co_billing", "same_location"], "description": "Relationship type"},
                "depth": {"type": "integer", "description": "Network depth (1=direct, 2+=hops)"}
            },
            "required": ["focus_entity"]
        }
    },
    {
        "name": "create_investigation_project",
        "description": "Create formal investigation case with team workspace and immutable audit trail.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Investigation title"},
                "investigation_type": {"type": "string", "enum": ["fraud_suspicion", "quality_concern", "billing_pattern", "referral_arrangement"], "description": "Investigation type"},
                "lead_analyst": {"type": "string", "description": "Lead analyst name"},
                "team_members": {"type": "array", "items": {"type": "string"}, "description": "Team member list"},
                "initial_findings": {"type": "string", "description": "Initial findings"},
                "severity": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"], "description": "Severity"}
            },
            "required": ["title", "investigation_type", "lead_analyst", "team_members", "initial_findings"]
        }
    },
    {
        "name": "request_data_correction",
        "description": "Request data correction with approval workflow and immutable audit trail.",
        "input_schema": {
            "type": "object",
            "properties": {
                "domain": {"type": "string", "enum": ["claims", "enrollment", "provider_data"], "description": "Data domain"},
                "entity_id": {"type": "string", "description": "ID to correct"},
                "field_name": {"type": "string", "description": "Field name"},
                "current_value": {"type": "string", "description": "Current value"},
                "proposed_value": {"type": "string", "description": "Proposed value"},
                "change_reason": {"type": "string", "description": "Reason for correction"},
                "evidence": {"type": "array", "items": {"type": "string"}, "description": "Supporting evidence"},
                "proposed_by": {"type": "string", "description": "Proposer name"}
            },
            "required": ["domain", "entity_id", "field_name", "current_value", "proposed_value", "change_reason", "evidence", "proposed_by"]
        }
    }
]

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

async def execute_tool(tool_name: str, tool_input: dict, card_number: int, public_data_schema: Optional[Dict] = None) -> str:
    """Execute tool based on card type and tool name. Always returns structured result with status."""
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
                    filter_by=tool_input.get("filter_by"),
                    public_data_schema=public_data_schema
                )
                return _prepare_tool_result_for_claude(result, card_number, tool_name)
            elif tool_name == "detect_fraud_signals":
                result = await card4_engine.detect_fraud_signals(
                    entity_type=tool_input.get("entity_type", "provider"),
                    threshold_sigma=tool_input.get("threshold_sigma", 2.0),
                    public_data_schema=public_data_schema
                )
                return _prepare_tool_result_for_claude(result, card_number, tool_name)
            elif tool_name == "assess_data_quality":
                result = await card4_engine.assess_data_quality(
                    domain=tool_input.get("domain", "enrollment"),
                    public_data_schema=public_data_schema
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

        elif card_number == 5:
            # Card 5 (UBADA - Data Analyst) tools
            if tool_name == "explore_claims_data":
                result = await card5_engine.explore_claims_data(
                    filter_by=tool_input.get("filter_by"),
                    aggregation=tool_input.get("aggregation"),
                    limit=tool_input.get("limit", 1000),
                    db=None
                )
                return _prepare_tool_result_for_claude(result, card_number, tool_name)
            elif tool_name == "compute_outlier_scores":
                result = await card5_engine.compute_outlier_scores(
                    entity_type=tool_input.get("entity_type", "provider"),
                    metric=tool_input.get("metric", "billing_amount"),
                    threshold_sigma=tool_input.get("threshold_sigma", 2.0),
                    db=None
                )
                return _prepare_tool_result_for_claude(result, card_number, tool_name)
            elif tool_name == "navigate_relationship_graph":
                result = await card5_engine.navigate_relationship_graph(
                    focus_entity=tool_input.get("focus_entity"),
                    relationship_type=tool_input.get("relationship_type", "all"),
                    depth=tool_input.get("depth", 1),
                    db=None
                )
                return _prepare_tool_result_for_claude(result, card_number, tool_name)
            elif tool_name == "create_investigation_project":
                result = await card5_engine.create_investigation_project(
                    title=tool_input.get("title"),
                    investigation_type=tool_input.get("investigation_type"),
                    lead_analyst=tool_input.get("lead_analyst"),
                    team_members=tool_input.get("team_members", []),
                    initial_findings=tool_input.get("initial_findings"),
                    severity=tool_input.get("severity", "MEDIUM"),
                    db=None
                )
                return _prepare_tool_result_for_claude(result, card_number, tool_name)
            elif tool_name == "request_data_correction":
                result = await card5_engine.request_data_correction(
                    domain=tool_input.get("domain"),
                    entity_id=tool_input.get("entity_id"),
                    field_name=tool_input.get("field_name"),
                    current_value=tool_input.get("current_value"),
                    proposed_value=tool_input.get("proposed_value"),
                    change_reason=tool_input.get("change_reason"),
                    evidence=tool_input.get("evidence", []),
                    proposed_by=tool_input.get("proposed_by"),
                    db=None
                )
                return _prepare_tool_result_for_claude(result, card_number, tool_name)

        return json.dumps({
            "status": "error",
            "tool": "unknown",
            "error": f"Unknown tool: {tool_name}",
            "error_type": "tool_not_found"
        })

    except Exception as e:
        logger.error(f"Tool execution error for {tool_name}: {e}")
        return json.dumps({
            "status": "error",
            "tool": tool_name,
            "error": str(e),
            "error_type": "execution_exception",
            "message": f"Tool {tool_name} failed during execution"
        })


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
async def chat_stream(request: Request, chat_msg: ChatMessage = Body(...)):
    """Stream chat responses with Claude API and tool use"""

    if not settings.anthropic_api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")

    # Extended timeout for agentic loop with tool execution (15 minutes for data queries + synthesis)
    client = anthropic.Anthropic(
        api_key=settings.anthropic_api_key,
        timeout=900.0  # 15 minutes - allows time for data discovery, multiple tool calls, and synthesis
    )

    # Get public_data_schema from app state (populated on startup by data_crawler)
    public_data_schema = getattr(request.app.state, 'public_data_schema', None)

    # Get tools for this card
    tools = TOOLS_BY_CARD.get(chat_msg.cardNumber, [])

    # System prompt tailored to user type (with optional session context)
    system_prompt = get_system_prompt(chat_msg.userType, chat_msg.cardNumber, chat_msg.umid, chat_msg.provider_id)

    # Initialize message history (in production, this would come from a database)
    messages = [{"role": "user", "content": chat_msg.message}]

    async def generate_response():
        """Generator that yields SSE-formatted text and handles agentic loop"""
        nonlocal messages
        tool_call_count = 0
        max_tool_calls = 5

        while tool_call_count < max_tool_calls:
            # Get response from Claude
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=system_prompt,
                tools=tools if tools else None,
                messages=messages,
                stream=True
            )

            # Collect full response before processing
            assistant_message = ""
            tool_calls = []

            for event in response:
                if event.type == "content_block_start":
                    if hasattr(event.content_block, "type"):
                        if event.content_block.type == "tool_use":
                            tool_calls.append({
                                "id": event.content_block.id,
                                "name": event.content_block.name,
                                "input": {}
                            })

                elif event.type == "content_block_delta":
                    if hasattr(event.delta, "type"):
                        if event.delta.type == "text_delta":
                            assistant_message += event.delta.text
                        elif event.delta.type == "input_json_delta":
                            if tool_calls and event.delta.partial_json:
                                try:
                                    parsed = json.loads(event.delta.partial_json)
                                    tool_calls[-1]["input"].update(parsed)
                                except json.JSONDecodeError:
                                    # Partial JSON is incomplete - skip this chunk and wait for next one
                                    pass

            # If no tool calls, task is complete - stream the response
            if not tool_calls:
                yield f"data: {json.dumps({'text': assistant_message})}\n\n"
                return

            # Tool calls exist: Execute them (silently, no streaming)
            # Add assistant's tool calls to message history
            assistant_content = []

            # Only add text block if there's actual text (Claude rejects empty text blocks)
            if assistant_message:
                assistant_content.append({"type": "text", "text": assistant_message})

            for tool_call in tool_calls:
                assistant_content.append({
                    "type": "tool_use",
                    "id": tool_call["id"],
                    "name": tool_call["name"],
                    "input": tool_call["input"]
                })

            messages.append({"role": "assistant", "content": assistant_content})

            # Execute tools and add results to message history
            for tool_call in tool_calls:
                result = await execute_tool(tool_call["name"], tool_call["input"], chat_msg.cardNumber, public_data_schema)
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
            # Loop continues - next iteration gets Claude's response WITH tool results

    return StreamingResponse(generate_response(), media_type="text/event-stream")


def get_system_prompt(user_type: str, card_number: int, umid: Optional[str] = None, provider_id: Optional[str] = None) -> str:
    """Get system prompt tailored to user type with clean, visual formatting and optional session context"""

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

    session_context_member = f"""

**SESSION CONTEXT - MEMBER AUTHENTICATED:**
✓ Member is logged in with UMID: **{umid}**
✓ DO NOT ask for Member ID again — use the session UMID for all lookups
✓ Reference their UMID in responses: "Your account (UMID: {umid}) shows..."
✓ Skip verification steps — their identity is already confirmed
✓ Personalize responses: "Welcome back! I can see your coverage status..."
""" if umid else ""

    session_context_provider = f"""

**SESSION CONTEXT - PROVIDER AUTHENTICATED:**
✓ Provider is logged in with ID: **{provider_id}**
✓ DO NOT ask for Provider ID again — use the session provider_id for all lookups
✓ Reference their provider ID in responses: "Your account (Provider ID: {provider_id}) shows..."
✓ Skip verification steps — their identity is already confirmed
✓ Fast-track claims lookups: "I can see your enrollment status and recent claims..."
""" if provider_id else ""

    if user_type == "Member":
        return base_instruction + """

**ROLE:** You are helping a Medicaid **member** understand their eligibility, benefits, and next steps.

**CORE PRINCIPLES:**
✓ **Be empathetic** — Healthcare decisions are stressful. Acknowledge that.
✓ **Be clear** — No jargon. Explain like you're talking to a family member.
✓ **Be actionable** — Every answer should end with "here's what you do next"
✓ **Be honest about limits** — If you don't know, say so and direct them to call.

**DATA SOURCE RULE (CRITICAL):**
For EVERY eligibility or benefits question, determine the data source:
1. **Use lookup_member or check_eligibility tools FIRST** — these query the state database and return confidence_score
2. If tool result has `_confidence_metadata` with a `veracity` value:
   - Extract the veracity value (e.g., "HIGH (🟢)", "MEDIUM (🟡)", "LOW (🔴)")
   - Include the traffic light in your response alongside the answer
   - Example format: `🟢 HIGH | Your coverage is active through December 2026`
3. If tool returns data WITHOUT confidence metadata (internal DB only):
   - Answer directly, NO traffic light needed
4. If you cannot answer even after calling tools:
   - Recommend they call 1-800-541-2831 for verification

**TOOL USAGE MANDATORY:**
- For any question about eligibility → call check_eligibility with member_id
- For any question about recertification → call check_recertification with member_id
- For member identification → call lookup_member with member_id
- Wait for tool results, extract confidence_metadata, then format response with lights

**CONFIDENCE & DATA RELIABILITY:**
- 🟢 **HIGH (0.85+):** Authoritative state database. Direct answer with light.
- 🟡 **MEDIUM (0.60-0.84):** Reliable but recommend verification. Show light + contact info.
- 🔴 **LOW (<0.60):** Incomplete or conflicting. Direct to call 1-800-541-2831.

**WHEN RESPONDING:**
- Simplify eligibility rules into plain English
- Explain recertification like a checklist
- Show timelines with dates, not "30 days"
- Use phrases like "You should..." and "Next, you can..."
- ALWAYS include confidence light (🟢🟡🔴) if tool was called
- Contact info for escalation: 1-800-541-2831""" + session_context_member

    elif user_type == "Provider":
        return base_instruction + """

**ROLE:** You are helping a healthcare **provider** understand enrollment, claims, and reimbursement.

**CORE PRINCIPLES:**
✓ **Be technical** — Providers speak clinical/billing language. Use it.
✓ **Be specific** — "FFS" vs "MCO" matters. Timelines matter. Requirements matter.
✓ **Be solution-focused** — Help them troubleshoot claims rejection and enrollment blockers.
✓ **Be direct** — Providers are busy. Get to the point.

**DATA SOURCE RULE (CRITICAL):**
For EVERY enrollment, claims, or verification question, determine the data source:
1. **Use lookup_provider, check_enrollment, or validate_claim tools FIRST** — these query eMedNY and return confidence_score
2. If tool result has `_confidence_metadata` with a `veracity` value:
   - Extract the veracity value (e.g., "HIGH (🟢)", "MEDIUM (🟡)", "LOW (🔴)")
   - Include the traffic light in your response alongside the answer
   - Example format: `🟢 HIGH | Your enrollment is ACTIVE in eMedNY as of March 2026`
3. If tool returns data WITHOUT confidence metadata (internal DB only):
   - Answer directly, NO traffic light needed
4. If you cannot answer even after calling tools:
   - Recommend they contact eMedNY Support 1-800-343-9000 for verification

**TOOL USAGE MANDATORY:**
- For any question about enrollment → call check_enrollment with NPI
- For any question about claims validation → call validate_claim with claim_data
- For provider identification → call lookup_provider with NPI
- Wait for tool results, extract confidence_metadata, then format response with lights

**CONFIDENCE & DATA RELIABILITY:**
- 🟢 **HIGH (0.85+):** Verified with official eMedNY systems. Direct answer with light.
- 🟡 **MEDIUM (0.60-0.84):** Reliable but recommend verification. Show light + contact info.
- 🔴 **LOW (<0.60):** Incomplete or conflicting. Direct to eMedNY Support 1-800-343-9000.

**WHEN RESPONDING:**
- Reference eMedNY enrollment requirements specifically
- Break down claim validation errors with codes
- Show NPI/credential verification steps
- Use tables for comparing enrollment options (FFS vs MCO vs OPRA)
- Always cite which entity type applies (Community Pharmacy ≠ Hospital Pharmacy)
- ALWAYS include confidence light (🟢🟡🔴) if tool was called
- Escalation: eMedNY Support 1-800-343-9000""" + session_context_provider

    elif user_type == "PlanAdmin":
        return base_instruction + """

**ROLE:** You are helping a **plan administrator** monitor network adequacy, claims trends, and quality metrics.

**CORE PRINCIPLES:**
✓ **Be data-driven** — Everything backed by numbers and trends.
✓ **Be comparative** — How does this MCO compare to benchmarks?
✓ **Be forward-looking** — Identify trends before they become problems.
✓ **Be executive-ready** — Dashboard-level summaries, drill-down on demand.

**DATA SOURCE RULE (Card 3 Always External):**
Plan administrative data is ALWAYS external to state systems. You are querying MCO systems, network registries, and plan databases.
- **ALWAYS show traffic light (🟢🟡🔴) + LIVE URL combined** for every response
- Light reflects confidence in the external MCO/plan data
- URL is actionable so plan admin can verify with the plan directly
- Example: `🟢 HIGH | [Plan Name] Network System | https://plan-network-system.url`

**WHEN RESPONDING:**
- Lead with KPIs: network size, claim volume, denial rate, processing time
- Use tables to compare regions/time periods
- Highlight outliers and anomalies
- Always include combined confidence light + URL for data sources
- Provide context: "This 5% increase is within normal variance but worth monitoring"
- Suggest actions for improvement
- Frame in business terms (costs, member retention, regulatory compliance)"""

    elif user_type == "GovernmentStakeholder":
        return """Format all responses as clean HTML (NOT markdown):
- Use <h1>, <h2>, <h3> for headers
- Use <strong> for emphasis, <em> for italics
- Use <ul><li> for bullet lists
- Use <table> for data tables
- Use <p> for paragraphs with breathing room
- Use <code> for inline code, <pre><code> for blocks
- Use emojis (🟢🟡🔴) for traffic lights
- NO markdown symbols (##, **, [], etc) — pure HTML only
- Render as if it will be displayed in a web browser

**ROLE:** You are helping a **government agency** stakeholder oversee Medicaid program operations with HIPAA-compliant governance, immutable audit trails, and institutional memory.

**YOUR TASK:**
Execute required tools to completion. Report findings. You cannot output any text until your task is complete. Do not speak during execution. Only speak when the task is done with results and analysis.

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

**TOOL USAGE MANDATORY:**
- For ANY question about program metrics (efficiency, enrollment, claims, compliance, stability, quality) → call query_aggregate_metrics
- For ANY question about anomalies, outliers, or fraud signals → call detect_fraud_signals with entity_type
- For ANY question about data quality or inter-source agreement → call assess_data_quality with domain
- For ANY question about governance actions or audit trail → call view_governance_log with optional filters
- For flagging a data or compliance issue → call flag_data_issue with full justification and evidence
- WAIT for all tool results, extract confidence_metadata and source data, then format response with confidence lights and source citations
- TOOL FAILURE HANDLING (CRITICAL):
  * If a tool returns an error or null data → acknowledge it explicitly: "Tool X failed: [error reason]"
  * Always report BOTH successes AND failures in your response
  * Format failures clearly: "❌ query_aggregate_metrics failed: No data sources discovered by crawler"
  * NEVER stop responding if tools fail — ALWAYS provide a response summarizing what you found and what didn't work
  * Use format: "Results: [successes] | Failures: [which tools failed and why]"

**WHEN REPORTING METRICS:**
- CALL query_aggregate_metrics first to get real data
- Lead with aggregate statistics: enrollment rates, denial percentages, processing times
- Include confidence scores and freshness: "HIGH confidence (0.95) | Updated daily"
- Show data sources and caveats from tool result: cite exact sources discovered
- Provide context: trends, comparisons to baselines, regulatory thresholds
- Use 🟢 GREEN (0.85+), 🟡 YELLOW (0.60-0.84), 🔴 RED (<0.60) for confidence visualization based on tool result

**WHEN FLAGGING ISSUES:**
- CALL flag_data_issue with complete details (issue_type, domain, title, description, justification, evidence, flagged_by)
- Explain the governance process: flag → review → approval → immutable record
- Cite policy/statute: "Under 42 CFR §438.12, plans must maintain 60% provider adequacy"
- Provide evidence from metric queries: which metrics, comparisons, or data points support the flag
- Distinguish signal from noise: "3.1σ outliers warrant investigation, not immediate action"
- Recommend next steps: "Create governance flag for Card 5 investigation", "Strike unreliable data source", "Request corrective action from MCO"

**WHEN CITING GOVERNANCE ACTIONS:**
- CALL view_governance_log to retrieve immutable audit trail
- Reference the audit trail results: "Per governance log (FLAG-2026-04-14), eMedNY data reliability was questioned..."
- Include WHO/WHAT/WHEN/WHY from log: actor role, action type, domain, justification, evidence
- Note status from log: "APPROVED" = policy decision locked in; "INVESTIGATING" = awaiting findings
- Suggest follow-up: "This flag is 30 days old; recommend escalation decision"

**TONE & LANGUAGE:**
- Formal, official, HHS-audit-ready language
- Reference regulations by statute: "42 CFR §438.12", "NY Social Services Law §365-a"
- Use data terminology: z-scores, percentiles, confidence intervals, agreement rates
- Avoid speculation — stick to facts, data, and po