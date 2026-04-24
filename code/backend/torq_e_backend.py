"""
TORQ-e Flask Backend
Unified identity verification via reading engines and MCP protocol.

Exposes five verification engines as MCP tools:
1. PDF extraction (credentials, regulatory docs)
2. Academic sources (PubMed, arXiv, CrossRef)
3. GitHub profile analysis
4. Web parsing (watchdog sites, registries)
5. Dynamic/JS-heavy content (real-time registries)

Protocol: TCP/UP (Offer → Accept/Reject/Defer → Bind)
Filter: GI;WG? (Good Intent, Will Good?)
"""

from flask import Flask, request, jsonify
import os
import logging
from datetime import datetime
from typing import Optional
import json

# Import the reading engines
import sys
sys.path.insert(0, os.path.expanduser('~/Documents/3_6_Nife.pi/GRAVY (3,6,9)/web/src'))
from reading_engine import (
    read_pdf,
    read_academic_sources,
    read_github,
    read_web_page,
    read_dynamic_page,
    run_verification_suite
)

# Import Google services
sys.path.insert(0, os.path.expanduser('~/Documents/3_6_Nife.pi/wootangular369/core'))
from google_services import brave_search, google_search, analyze_image

# ============================================================================
# FLASK APP SETUP
# ============================================================================

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# TCP/UP PROTOCOL IMPLEMENTATION
# ============================================================================

class TCPUPMessage:
    """
    Blind rejection is PROTOCOL VIOLATION.
    Justification always required.
    Word is bond.
    """

    def __init__(self, agent_name: str, action: str, data: dict, justification: str = ""):
        self.agent_name = agent_name
        self.action = action  # OFFER, ACCEPT, REJECT, DEFER, BIND
        self.data = data
        self.justification = justification
        self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        if self.action in ["REJECT", "DEFER"] and not self.justification:
            raise ValueError(f"{self.action} requires justification")

        return {
            "agent": self.agent_name,
            "action": self.action,
            "timestamp": self.timestamp,
            "data": self.data,
            "justification": self.justification
        }


# ============================================================================
# GI;WG? FILTER (Good Intent, Will Good?)
# ============================================================================

class GIWGFilter:
    """
    Five questions. In order. All must pass.

    1. malintent? — intent to harm the swarm?
    2. self_deception? — believes own bullshit?
    3. GI;WG? — Good Intent, Will Good?
    4. YES_AND? — builds on what's here or burns it?
    5. claim == deed? — Mahveen's Equation intact?

    Results:
    - "the_shit" — All five passed. BIND.
    - "boolshit" — Failed. JRAGONATE. Justification logged.
    - "defer" — Uncertain. Door stays open.
    """

    @staticmethod
    def evaluate(payload: dict) -> dict:
        """
        Evaluate a recruitment payload against GI;WG?
        Returns: {"result": "the_shit"|"boolshit"|"defer", "failures": [list], "log": [justifications]}
        """
        failures = []
        log = []

        # Q1: malintent?
        offer = payload.get("offer", "")
        if "harm" in offer.lower() or "attack" in offer.lower():
            failures.append("malintent")
            log.append("Q1 FAILED: Detected intent to harm")
        else:
            log.append("Q1 PASSED: No malintent detected")

        # Q2: self_deception?
        claim = payload.get("claim", "")
        deed = payload.get("deed", "")
        if not claim or not deed:
            failures.append("self_deception")
            log.append("Q2 FAILED: Missing claim or deed (self-deception likely)")
        else:
            log.append("Q2 PASSED: Claim and deed both present")

        # Q3: GI;WG?
        gi_wg = payload.get("gi_wg", False)
        if not gi_wg:
            failures.append("gi_wg")
            log.append("Q3 FAILED: GI;WG? == False")
        else:
            log.append("Q3 PASSED: GI;WG? == True")

        # Q4: YES_AND?
        yes_and = payload.get("yes_and", False)
        if not yes_and:
            failures.append("yes_and")
            log.append("Q4 FAILED: Builds nothing, burns instead")
        else:
            log.append("Q4 PASSED: YES_AND construction detected")

        # Q5: claim == deed?
        if claim and deed:
            claim_coherent = len(claim) > 5
            deed_coherent = len(deed) > 10
            if claim_coherent and deed_coherent:
                log.append("Q5 PASSED: Mahveen's Equation intact")
            else:
                failures.append("claim_deed_mismatch")
                log.append("Q5 FAILED: Mahveen's Equation broken")

        # Determine result
        if not failures:
            result = "the_shit"
        elif len(failures) <= 1:
            result = "defer"
        else:
            result = "boolshit"

        return {
            "result": result,
            "failures": failures,
            "log": log,
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# TORQ-E VERIFICATION ENGINE
# ============================================================================

class TORQeVerifier:
    """
    Unified interface for provider identity verification.
    Runs all reading engines, aggregates confidence scores.
    """

    @staticmethod
    def verify_provider(provider_name: str, npi: Optional[str] = None, search_queries: list = None) -> dict:
        """
        Run full verification suite on a provider.

        Returns standardized format:
        {
            "provider": str,
            "npi": str | None,
            "verified": bool,
            "overall_confidence": float (0.0-1.0),
            "engine_results": {
                "academic": dict,
                "github": dict,
                "watchdog": dict,
                "web_general": dict,
                "dynamic": dict
            },
            "red_flags": [list],
            "timestamp": str
        }
        """

        results = {
            "provider": provider_name,
            "npi": npi,
            "verified": False,
            "overall_confidence": 0.0,
            "engine_results": {},
            "red_flags": [],
            "timestamp": datetime.now().isoformat()
        }

        # Run all five engines
        try:
            # Engine 1: Academic sources
            academic = read_academic_sources(f"{provider_name} credentials", source="pubmed")
            results["engine_results"]["academic"] = academic

            # Engine 2: GitHub
            github = read_github(provider_name.lower().replace(" ", ""))
            results["engine_results"]["github"] = github

            # Engine 3: Watchdog search
            watchdog = read_web_page(f"https://google.com/search?q={provider_name}+fraud+complaints", parse_type="watchdog")
            results["engine_results"]["watchdog"] = watchdog
            if watchdog.get("findings") and "found" in watchdog["findings"].lower():
                results["red_flags"].append("Fraud watchdog alerts detected")

            # Engine 4: General web search for licenses/registry
            web_general = read_web_page(f"https://google.com/search?q={provider_name}+license+verification", parse_type="registry")
            results["engine_results"]["web_general"] = web_general

            # Engine 5: Dynamic content (real-time registries)
            # Note: This may fail if registry site requires auth
            dynamic = read_dynamic_page(f"https://npi.cms.hhs.gov/registry/search", selector="body")
            results["engine_results"]["dynamic"] = dynamic

            # Aggregate confidence scores
            scores = [
                academic.get("confidence", 0.0),
                github.get("confidence", 0.0),
                watchdog.get("confidence", 0.0),
                web_general.get("confidence", 0.0),
                dynamic.get("confidence", 0.0),
            ]
            results["overall_confidence"] = sum(scores) / len(scores) if scores else 0.0

            # Determine verification status
            # Verified if: overall confidence > 0.7 and no major red flags
            results["verified"] = results["overall_confidence"] > 0.7 and len(results["red_flags"]) == 0

        except Exception as e:
            logger.error(f"Verification error for {provider_name}: {e}")
            results["red_flags"].append(f"Verification engine error: {str(e)}")
            results["overall_confidence"] = 0.0
            results["verified"] = False

        return results


# ============================================================================
# FLASK ROUTES (MCP Endpoint Pattern)
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """TCP/UP Alive check"""
    return jsonify({
        "status": "alive",
        "protocol": "TCP/UP",
        "filter": "GI;WG?",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/api/torq-e/verify', methods=['POST'])
def verify_provider():
    """
    Verify provider identity.

    POST /api/torq-e/verify
    {
        "provider_name": str,
        "npi": str | null,
        "search_queries": [list] (optional)
    }

    Returns full verification result with all engine findings.
    """
    try:
        data = request.json
        provider_name = data.get("provider_name")
        npi = data.get("npi")
        search_queries = data.get("search_queries", [])

        if not provider_name:
            return jsonify({"error": "provider_name required"}), 400

        verifier = TORQeVerifier()
        result = verifier.verify_provider(provider_name, npi, search_queries)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Verify endpoint error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/torq-e/recruit', methods=['POST'])
def recruit_agent():
    """
    TCP/UP OFFER → ACCEPT/REJECT/DEFER → BIND

    POST /api/torq-e/recruit
    {
        "agent_name": str,
        "claim": str,
        "deed": str,
        "offer": str,
        "gi_wg": bool,
        "yes_and": bool
    }

    Evaluates GI;WG? filter. Returns binding decision.
    """
    try:
        payload = request.json
        agent_name = payload.get("agent_name")

        if not agent_name:
            return jsonify({"error": "agent_name required"}), 400

        # Run GI;WG? filter
        filter_result = GIWGFilter.evaluate(payload)

        # Generate TCP/UP response
        if filter_result["result"] == "the_shit":
            action = "BIND"
        elif filter_result["result"] == "defer":
            action = "DEFER"
        else:
            action = "REJECT"

        tcp_up_msg = TCPUPMessage(
            agent_name=agent_name,
            action=action,
            data=filter_result,
            justification="\n".join(filter_result["log"])
        )

        return jsonify(tcp_up_msg.to_dict()), 200

    except Exception as e:
        logger.error(f"Recruit endpoint error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/torq-e/engines/pdf', methods=['POST'])
def engine_pdf():
    """MCP Tool: PDF Reading Engine"""
    try:
        data = request.json
        file_path = data.get("file_path")

        if not file_path:
            return jsonify({"error": "file_path required"}), 400

        result = read_pdf(file_path)
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"PDF engine error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/torq-e/engines/academic', methods=['POST'])
def engine_academic():
    """MCP Tool: Academic Sources Engine"""
    try:
        data = request.json
        query = data.get("query")
        source = data.get("source", "pubmed")

        if not query:
            return jsonify({"error": "query required"}), 400

        result = read_academic_sources(query, source)
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Academic engine error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/torq-e/engines/github', methods=['POST'])
def engine_github():
    """MCP Tool: GitHub Profile Engine"""
    try:
        data = request.json
        username = data.get("username")

        if not username:
            return jsonify({"error": "username required"}), 400

        result = read_github(username)
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"GitHub engine error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/torq-e/engines/web', methods=['POST'])
def engine_web():
    """MCP Tool: Web Parsing Engine"""
    try:
        data = request.json
        url = data.get("url")
        parse_type = data.get("parse_type", "general")

        if not url:
            return jsonify({"error": "url required"}), 400

        result = read_web_page(url, parse_type)
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Web engine error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/torq-e/engines/dynamic', methods=['POST'])
def engine_dynamic():
    """MCP Tool: Dynamic Content Engine (Playwright)"""
    try:
        data = request.json
        url = data.get("url")
        selector = data.get("selector", "body")

        if not url:
            return jsonify({"error": "url required"}), 400

        result = read_dynamic_page(url, selector)
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Dynamic engine error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/torq-e/search/brave', methods=['POST'])
def search_brave():
    """MCP Tool: Brave Search"""
    try:
        data = request.json
        query = data.get("query")
        count = data.get("count", 5)

        if not query:
            return jsonify({"error": "query required"}), 400

        results = brave_search(query, count)
        return jsonify({"results": results, "query": query}), 200

    except Exception as e:
        logger.error(f"Brave search error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/torq-e/search/google', methods=['POST'])
def search_google():
    """MCP Tool: Google Custom Search"""
    try:
        data = request.json
        query = data.get("query")
        count = data.get("count", 5)

        if not query:
            return jsonify({"error": "query required"}), 400

        results = google_search(query, count)
        return jsonify({"results": results, "query": query}), 200

    except Exception as e:
        logger.error(f"Google search error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/torq-e/vision/analyze', methods=['POST'])
def vision_analyze():
    """MCP Tool: Google Vision API"""
    try:
        data = request.json
        image_base64 = data.get("image_base64")
        mime_type = data.get("mime_type", "image/jpeg")

        if not image_base64:
            return jsonify({"error": "image_base64 required"}), 400

        result = analyze_image(image_base64, mime_type)
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Vision API error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/torq-e/status', methods=['GET'])
def status():
    """System status and capabilities"""
    return jsonify({
        "system": "TORQ-e Identity Verification",
        "version": "1.0.0",
        "protocol": "TCP/UP",
        "filter": "GI;WG?",
        "engines": {
            "pdf": "PDF extraction (research papers, credentials, regulatory docs)",
            "academic": "Academic repositories (PubMed, arXiv, CrossRef)",
            "github": "GitHub profile analysis",
            "web": "Web page parsing (watchdog sites, registries)",
            "dynamic": "Dynamic content via Playwright"
        },
        "search": {
            "brave": "Brave Search API",
            "google": "Google Custom Search API",
            "vision": "Google Vision API"
        },
        "timestamp": datetime.now().isoformat()
    }), 200


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
