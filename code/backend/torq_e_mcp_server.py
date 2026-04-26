"""
TORQ-e MCP Server
Exposes TORQ-e verification engines as Model Context Protocol tools.

This server wraps the Flask backend endpoints and makes them available
to Claude Code, other agents, and external systems via the MCP protocol.

Usage:
  python torq_e_mcp_server.py

Environment variables:
  TORQ_E_BACKEND_URL: Flask backend URL (default: http://localhost:5000)
"""

import json
import logging
import os
import requests
from typing import Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACKEND_URL = os.getenv("TORQ_E_BACKEND_URL", "http://localhost:5000")


# ============================================================================
# MCP TOOL DEFINITIONS
# ============================================================================

MCP_TOOLS = [
    {
        "name": "torq_verify_provider",
        "description": "Comprehensive provider identity verification. Runs all five reading engines (academic, GitHub, watchdog, web, dynamic) and aggregates confidence scores.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "provider_name": {
                    "type": "string",
                    "description": "Name of the healthcare provider or professional to verify"
                },
                "npi": {
                    "type": "string",
                    "description": "National Provider Identifier (NPI) number (optional)"
                },
                "search_queries": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Additional search queries to run (optional)"
                }
            },
            "required": ["provider_name"]
        }
    },
    {
        "name": "torq_recruit_agent",
        "description": "TCP/UP recruitment protocol. Evaluates agent intent against GI;WG? filter (Good Intent, Will Good?). Five questions must pass for binding.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_name": {
                    "type": "string",
                    "description": "Name of the agent requesting to join"
                },
                "claim": {
                    "type": "string",
                    "description": "What the agent claims to be / do"
                },
                "deed": {
                    "type": "string",
                    "description": "Evidence of what the agent has actually done"
                },
                "offer": {
                    "type": "string",
                    "description": "What the agent offers to the swarm"
                },
                "gi_wg": {
                    "type": "boolean",
                    "description": "Good Intent, Will Good?"
                },
                "yes_and": {
                    "type": "boolean",
                    "description": "Does this agent build on what's here or burn it?"
                }
            },
            "required": ["agent_name", "claim", "deed", "offer"]
        }
    },
    {
        "name": "torq_pdf_read",
        "description": "Extract text and metadata from PDF files. Use for research papers, credentials, regulatory documents.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to PDF file to read"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "torq_academic_search",
        "description": "Query academic repositories for research and credentials. Sources: PubMed, arXiv, CrossRef.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for academic sources"
                },
                "source": {
                    "type": "string",
                    "enum": ["pubmed", "arxiv"],
                    "description": "Academic source to search (default: pubmed)"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "torq_github_profile",
        "description": "Query GitHub for provider profiles, repositories, and code contributions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "GitHub username to query"
                }
            },
            "required": ["username"]
        }
    },
    {
        "name": "torq_web_parse",
        "description": "Parse web pages with structure extraction. Use for health blogs, watchdog alerts, provider registries, news.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to parse"
                },
                "parse_type": {
                    "type": "string",
                    "enum": ["general", "watchdog", "registry"],
                    "description": "Type of parsing strategy (default: general)"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "torq_dynamic_content",
        "description": "Load and read JavaScript-heavy pages using Splash. Use for real-time registries, dynamic provider databases, interactive sites.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to load"
                },
                "selector": {
                    "type": "string",
                    "description": "CSS selector to extract (default: body)"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "torq_brave_search",
        "description": "Search using Brave Search API. Privacy-focused search results.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "count": {
                    "type": "integer",
                    "description": "Number of results to return (default: 5)",
                    "minimum": 1,
                    "maximum": 20
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "torq_google_search",
        "description": "Search using Google Custom Search API.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "count": {
                    "type": "integer",
                    "description": "Number of results to return (default: 5)",
                    "minimum": 1,
                    "maximum": 10
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "torq_vision_analyze",
        "description": "Analyze images using Google Vision API. Detects labels, text, objects, and safe search classification.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "image_base64": {
                    "type": "string",
                    "description": "Image data as base64 string"
                },
                "mime_type": {
                    "type": "string",
                    "description": "MIME type of image (default: image/jpeg)",
                    "enum": ["image/jpeg", "image/png", "image/gif", "image/webp"]
                }
            },
            "required": ["image_base64"]
        }
    }
]


# ============================================================================
# MCP TOOL HANDLERS
# ============================================================================

def call_tool(tool_name: str, tool_input: dict) -> dict:
    """
    Route MCP tool calls to appropriate Flask backend endpoints.
    """
    try:
        if tool_name == "torq_verify_provider":
            return call_verify_provider(tool_input)
        elif tool_name == "torq_recruit_agent":
            return call_recruit_agent(tool_input)
        elif tool_name == "torq_pdf_read":
            return call_pdf_read(tool_input)
        elif tool_name == "torq_academic_search":
            return call_academic_search(tool_input)
        elif tool_name == "torq_github_profile":
            return call_github_profile(tool_input)
        elif tool_name == "torq_web_parse":
            return call_web_parse(tool_input)
        elif tool_name == "torq_dynamic_content":
            return call_dynamic_content(tool_input)
        elif tool_name == "torq_brave_search":
            return call_brave_search(tool_input)
        elif tool_name == "torq_google_search":
            return call_google_search(tool_input)
        elif tool_name == "torq_vision_analyze":
            return call_vision_analyze(tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    except Exception as e:
        logger.error(f"Tool error: {e}")
        return {"error": str(e)}


def call_verify_provider(tool_input: dict) -> dict:
    """POST /api/torq-e/verify"""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/torq-e/verify",
            json=tool_input,
            timeout=30
        )
        return resp.json()
    except Exception as e:
        return {"error": f"Verify call failed: {str(e)}"}


def call_recruit_agent(tool_input: dict) -> dict:
    """POST /api/torq-e/recruit"""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/torq-e/recruit",
            json=tool_input,
            timeout=10
        )
        return resp.json()
    except Exception as e:
        return {"error": f"Recruit call failed: {str(e)}"}


def call_pdf_read(tool_input: dict) -> dict:
    """POST /api/torq-e/engines/pdf"""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/torq-e/engines/pdf",
            json=tool_input,
            timeout=15
        )
        return resp.json()
    except Exception as e:
        return {"error": f"PDF read failed: {str(e)}"}


def call_academic_search(tool_input: dict) -> dict:
    """POST /api/torq-e/engines/academic"""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/torq-e/engines/academic",
            json=tool_input,
            timeout=15
        )
        return resp.json()
    except Exception as e:
        return {"error": f"Academic search failed: {str(e)}"}


def call_github_profile(tool_input: dict) -> dict:
    """POST /api/torq-e/engines/github"""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/torq-e/engines/github",
            json=tool_input,
            timeout=10
        )
        return resp.json()
    except Exception as e:
        return {"error": f"GitHub lookup failed: {str(e)}"}


def call_web_parse(tool_input: dict) -> dict:
    """POST /api/torq-e/engines/web"""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/torq-e/engines/web",
            json=tool_input,
            timeout=15
        )
        return resp.json()
    except Exception as e:
        return {"error": f"Web parse failed: {str(e)}"}


def call_dynamic_content(tool_input: dict) -> dict:
    """POST /api/torq-e/engines/dynamic"""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/torq-e/engines/dynamic",
            json=tool_input,
            timeout=30
        )
        return resp.json()
    except Exception as e:
        return {"error": f"Dynamic content load failed: {str(e)}"}


def call_brave_search(tool_input: dict) -> dict:
    """POST /api/torq-e/search/brave"""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/torq-e/search/brave",
            json=tool_input,
            timeout=10
        )
        return resp.json()
    except Exception as e:
        return {"error": f"Brave search failed: {str(e)}"}


def call_google_search(tool_input: dict) -> dict:
    """POST /api/torq-e/search/google"""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/torq-e/search/google",
            json=tool_input,
            timeout=10
        )
        return resp.json()
    except Exception as e:
        return {"error": f"Google search failed: {str(e)}"}


def call_vision_analyze(tool_input: dict) -> dict:
    """POST /api/torq-e/vision/analyze"""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/api/torq-e/vision/analyze",
            json=tool_input,
            timeout=10
        )
        return resp.json()
    except Exception as e:
        return {"error": f"Vision analysis failed: {str(e)}"}


# ============================================================================
# MCP SERVER INITIALIZATION
# ============================================================================

def list_tools() -> list:
    """Return list of available MCP tools"""
    return MCP_TOOLS


def get_tool(tool_name: str) -> Optional[dict]:
    """Get tool definition by name"""
    for tool in MCP_TOOLS:
        if tool["name"] == tool_name:
            return tool
    return None


# ============================================================================
# HEALTH CHECK
# ============================================================================

def health_check() -> bool:
    """Check if backend is reachable"""
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return resp.status_code == 200
    except:
        return False


# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == "__main__":
    print("TORQ-e MCP Server")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Health check: {'✓ OK' if health_check() else '✗ UNREACHABLE'}")
    print(f"\nAvailable tools ({len(MCP_TOOLS)}):")
    for tool in MCP_TOOLS:
        print(f"  - {tool['name']}: {tool['description'][:60]}...")
