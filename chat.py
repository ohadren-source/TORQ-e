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
CARD_4_TOOLS = []  # Government Stakeholder tools - pending implementation
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
    """Execute tool based on card type and tool name"""
    try:
        if card_number == 1:
            # Card 1 (Member) tools
            if tool_name == "lookup_member":
                result = await card1_routes.lookup_member(tool_input.get("member_id"))
                return json.dumps(result)
            elif tool_name == "check_eligibility":
                result = await card1_routes.check_eligibility(tool_input.get("member_id"))
                return json.dumps(result)
            elif tool_name == "check_recertification":
                result = await card1_routes.check_recertification(tool_input.get("member_id"))
                return json.dumps(result)

        elif card_number == 2:
            # Card 2 (Provider) tools
            if tool_name == "lookup_provider":
                result = await card2_routes.lookup_provider(tool_input.get("npi"))
                return json.dumps(result)
            elif tool_name == "check_enrollment":
                result = await card2_routes.check_enrollment(tool_input.get("npi"))
                return json.dumps(result)
            elif tool_name == "validate_claim":
                result = await card2_routes.validate_claim(tool_input.get("claim_data"))
                return json.dumps(result)

        return json.dumps({"error": f"Unknown tool: {tool_name}"})

    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return json.dumps({"error": str(e)})


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
    """Get system prompt tailored to user type"""
    base_context = """You are a helpful assistant for the TORQ-e Medicaid Clarity System.
You help users navigate Medicaid eligibility, provider enrollment, claims, and related information.
Be clear, concise, and focused. Always prioritize clarity over technical jargon.
Use accessible language. If you need more information, ask focused questions."""

    if user_type == "Member":
        return base_context + """

You are helping a Medicaid member understand their eligibility, benefits, and next steps.
- Be empathetic and clear about benefits and limitations
- Explain complex eligibility rules in simple terms
- Help members understand recertification requirements
- Provide actionable next steps"""

    elif user_type == "Provider":
        return base_context + """

You are helping a healthcare provider understand enrollment, claims, and reimbursement.
- Use clinical/healthcare terminology when appropriate
- Focus on enrollment status, claims processing, and payment details
- Be specific about timelines and required documentation
- Help providers troubleshoot claims issues"""

    elif user_type == "PlanAdmin":
        return base_context + """

You are helping a plan administrator monitor network, claims, and quality metrics.
- Use data-driven language and focus on metrics
- Help identify trends and outliers
- Provide summary-level views of network performance"""

    elif user_type == "GovernmentStakeholder":
        return base_context + """

You are helping a government agency stakeholder monitor program operations.
- Focus on compliance, reporting, and program oversight
- Use official terminology
- Provide aggregate-level insights"""

    elif user_type == "DataAnalyst":
        return base_context + """

You are helping a data analyst investigate claims, fraud patterns, and anomalies.
- Be technical and precise
- Provide detailed data context
- Help identify suspicious patterns or outliers
- Focus on signal vs. noise detection"""

    return base_context


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
