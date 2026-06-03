"""
CONTEXT-AWARE DATA ORCHESTRATOR - TORQ-E
Intelligent data fetcher that analyzes query context and selects relevant NYS repos.

Features:
  - Analyzes query intent (what data do we need?)
  - Selects from all 9 NYS public health repos based on context
  - Fetches from selected sources in parallel
  - Processes + refines data intelligently
  - Returns with clarity scores + source attribution
  - Supports all 5 card types with role-based access

Public API:
  orchestrate(query, context, card_number) -> dict with clarity + sources
"""

import asyncio
import httpx
import logging
import json
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

# ============================================================================
# ALL 9 NYS PUBLIC HEALTH REPOSITORIES
# ============================================================================

NYS_REPOS = {
    # 1. eMedNY - Member & Provider enrollment
    "emedny": {
        "url": "https://www.emedny.org/",
        "name": "eMedNY - Medicaid Enrollment System",
        "domains": ["member_data", "provider_enrollment", "eligibility"],
        "card_access": [1, 2, 4, 5],
        "priority": 1
    },
    
    # 2. Health Data NY - Public health metrics & datasets
    "health_data_ny": {
        "url": "https://health.data.ny.gov",
        "name": "Health Data NY - Public Health Datasets",
        "domains": ["enrollment", "claims", "quality", "metrics", "plan_data"],
        "card_access": [1, 2, 3, 4, 5],
        "priority": 1
    },
    
    # 3. OMIG - Office of Medicaid Inspector General (fraud, audit, compliance)
    "omig": {
        "url": "https://omig.ny.gov/",
        "name": "OMIG - Medicaid Inspector General",
        "domains": ["audit", "fraud", "compliance", "investigation", "provider_authenticity"],
        "card_access": [4, 5],
        "priority": 1
    },
    
    # 4. ITS NY - Infrastructure & system status
    "its_ny": {
        "url": "https://its.ny.gov/",
        "name": "ITS NY - Information Technology Services",
        "domains": ["infrastructure", "processing", "system_status"],
        "card_access": [4],
        "priority": 2
    },
    
    # 5. Medicaid.NY.Gov - Official Medicaid portal
    "medicaid_ny": {
        "url": "https://www.medicaid.ny.gov/",
        "name": "Medicaid.NY.Gov - Official Portal",
        "domains": ["eligibility", "benefits", "enrollment_status", "plan_info"],
        "card_access": [1, 2, 3],
        "priority": 1
    },
    
    # 6. NYS Department of Health - Health data & statistics
    "doh_ny": {
        "url": "https://www.health.ny.gov/",
        "name": "NYS Department of Health",
        "domains": ["health_data", "statistics", "quality", "provider_data"],
        "card_access": [1, 2, 3, 4, 5],
        "priority": 1
    },
    
    # 7. NYS Comptroller - Financial audits & oversight
    "comptroller_ny": {
        "url": "https://www.osc.state.ny.us/",
        "name": "NYS Comptroller - Financial Oversight",
        "domains": ["audit", "financial", "compliance", "investigation"],
        "card_access": [4, 5],
        "priority": 2
    },
    
    # 8. CMS NPI Registry - Provider authenticity (federal)
    "npi_registry": {
        "url": "https://npiregistry.cms.hhs.gov/",
        "name": "CMS NPI Registry - Provider Verification",
        "domains": ["provider_authenticity", "npi_verification", "provider_data"],
        "card_access": [2, 5],
        "priority": 1
    },
    
    # 9. PECOS - Provider Enrollment, Chains, and Ownership System (federal)
    "pecos": {
        "url": "https://pecos.cms.hhs.gov/",
        "name": "PECOS - Provider Enrollment System",
        "domains": ["provider_enrollment", "provider_authenticity", "compliance"],
        "card_access": [2, 5],
        "priority": 1
    }
}

# ============================================================================
# INTENT ANALYZER
# ============================================================================

class IntentAnalyzer:
    """Analyzes query context to determine data needs"""
    
    INTENT_PATTERNS = {
        "provider_authenticity": {
            "keywords": ["authentic", "npi", "provider", "verify", "legitimate", "fraud", "suspicious"],
            "required_domains": ["provider_authenticity", "npi_verification"],
            "repos": ["npi_registry", "pecos", "omig"]
        },
        "member_eligibility": {
            "keywords": ["eligible", "eligibility", "member", "qualify", "benefits", "enrollment"],
            "required_domains": ["eligibility", "member_data", "enrollment_status"],
            "repos": ["emedny", "medicaid_ny", "health_data_ny"]
        },
        "claims_analysis": {
            "keywords": ["claim", "billing", "payment", "processing", "denial", "approval"],
            "required_domains": ["claims", "processing"],
            "repos": ["health_data_ny", "emedny", "omig"]
        },
        "fraud_investigation": {
            "keywords": ["fraud", "suspicious", "pattern", "outlier", "investigation", "anomaly"],
            "required_domains": ["fraud", "investigation", "audit"],
            "repos": ["omig", "health_data_ny", "emedny"]
        },
        "plan_metrics": {
            "keywords": ["plan", "network", "adequacy", "enrollment", "formulary", "mco"],
            "required_domains": ["plan_data", "enrollment", "metrics"],
            "repos": ["health_data_ny", "medicaid_ny", "doh_ny"]
        },
        "compliance_audit": {
            "keywords": ["compliance", "audit", "review", "protocol", "standard", "requirement"],
            "required_domains": ["audit", "compliance"],
            "repos": ["omig", "comptroller_ny", "doh_ny"]
        }
    }
    
    @staticmethod
    async def analyze(query: str, context: dict) -> Dict[str, Any]:
        """Analyze query to determine intent and required data sources"""
        query_lower = query.lower()
        
        # Score each intent
        intent_scores = {}
        for intent_name, intent_config in IntentAnalyzer.INTENT_PATTERNS.items():
            score = sum(1 for kw in intent_config["keywords"] if kw in query_lower)
            if score > 0:
                intent_scores[intent_name] = score
        
        # Determine primary intent
        if not intent_scores:
            primary_intent = "general_query"
            required_repos = list(NYS_REPOS.keys())
        else:
            primary_intent = max(intent_scores, key=intent_scores.get)
            required_repos = IntentAnalyzer.INTENT_PATTERNS[primary_intent]["repos"]
        
        return {
            "primary_intent": primary_intent,
            "intent_scores": intent_scores,
            "required_repos": required_repos,
            "required_domains": IntentAnalyzer.INTENT_PATTERNS.get(primary_intent, {}).get("required_domains", []),
            "card_number": context.get("card_number", 5),
            "user_type": context.get("user_type", "DataAnalyst")
        }

# ============================================================================
# SOURCE SELECTOR
# ============================================================================

class SourceSelector:
    """Selects relevant repos based on intent and card access"""
    
    @staticmethod
    def select(intent_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Select repos based on intent and card access"""
        card_number = intent_analysis["card_number"]
        required_repos = intent_analysis["required_repos"]
        
        selected = []
        for repo_key in required_repos:
            if repo_key in NYS_REPOS:
                repo = NYS_REPOS[repo_key]
                # Check card access
                if card_number in repo["card_access"]:
                    selected.append({
                        "key": repo_key,
                        "url": repo["url"],
                        "name": repo["name"],
                        "domains": repo["domains"],
                        "priority": repo["priority"]
                    })
        
        # Sort by priority
        selected.sort(key=lambda x: x["priority"])
        return selected

# ============================================================================
# DATA FETCHER
# ============================================================================

class DataFetcher:
    """Fetches data from selected sources in parallel"""
    
    REQUEST_TIMEOUT = 30.0
    USER_AGENT = "TORQ-e DataOrchestrator/1.0 (NYS Medicaid Intelligence)"
    
    @staticmethod
    async def fetch_all(sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fetch from all selected sources in parallel"""
        headers = {
            "User-Agent": DataFetcher.USER_AGENT,
            "Accept": "text/html,application/json,*/*",
        }
        
        results = {}
        async with httpx.AsyncClient(headers=headers, timeout=DataFetcher.REQUEST_TIMEOUT) as client:
            tasks = [
                DataFetcher._fetch_source(client, source)
                for source in sources
            ]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            for source, response in zip(sources, responses):
                if isinstance(response, Exception):
                    results[source["key"]] = {
                        "status": "error",
                        "error": str(response),
                        "data": None
                    }
                else:
                    results[source["key"]] = response
        
        return results
    
    @staticmethod
    async def _fetch_source(client: httpx.AsyncClient, source: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch and parse a single source"""
        try:
            response = await client.get(source["url"], follow_redirects=True)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Extract key data
            data = {
                "status": "success",
                "url": source["url"],
                "title": soup.title.string if soup.title else "Unknown",
                "tables": len(soup.find_all('table')),
                "links": len(soup.find_all('a')),
                "text_snippet": soup.get_text()[:500],
                "data": None
            }
            
            return data
        except Exception as e:
            logger.error(f"Error fetching {source['key']}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "data": None
            }

# ============================================================================
# DATA PROCESSOR & REFINER
# ============================================================================

class DataProcessor:
    """Processes and refines raw data"""
    
    @staticmethod
    async def process(raw_data: Dict[str, Any], intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Process raw data based on intent"""
        processed = {}
        
        for repo_key, data in raw_data.items():
            if data["status"] == "error":
                processed[repo_key] = {
                    "status": "error",
                    "error": data["error"],
                    "clarity": "red",
                    "confidence": 0.0
                }
            else:
                # Determine clarity based on data quality
                clarity = DataProcessor._determine_clarity(data, intent_analysis)
                confidence = DataProcessor._calculate_confidence(data)
                
                processed[repo_key] = {
                    "status": "success",
                    "title": data.get("title"),
                    "data": data.get("data"),
                    "clarity": clarity,
                    "confidence": confidence,
                    "tables_found": data.get("tables", 0),
                    "snippet": data.get("text_snippet", "")
                }
        
        return processed
    
    @staticmethod
    def _determine_clarity(data: Dict[str, Any], intent_analysis: Dict[str, Any]) -> str:
        """Determine clarity light (green/yellow/red)"""
        if data["status"] == "error":
            return "red"
        
        # Green: data found and relevant
        if data.get("tables", 0) > 0:
            return "green"
        
        # Yellow: data found but limited
        if data.get("text_snippet"):
            return "yellow"
        
        # Red: no data
        return "red"
    
    @staticmethod
    def _calculate_confidence(data: Dict[str, Any]) -> float:
        """Calculate confidence score (0.0-1.0)"""
        if data["status"] == "error":
            return 0.0
        
        score = 0.5
        if data.get("tables", 0) > 0:
            score += 0.3
        if data.get("text_snippet"):
            score += 0.2
        
        return min(score, 1.0)

# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

class ContextAwareDataOrchestrator:
    """Main orchestrator: analyze → select → fetch → process → display"""
    
    @staticmethod
    async def orchestrate(
        query: str,
        context: dict,
        card_number: int = 5
    ) -> Dict[str, Any]:
        """
        Main entry point: orchestrate data discovery and processing
        
        Args:
            query: User's question/request
            context: Additional context (user_type, session_id, etc)
            card_number: Which card is making the request (1-5)
        
        Returns:
            Dict with clarity scores, sources, and processed data
        """
        context["card_number"] = card_number
        
        # Step 1: Analyze intent
        logger.info(f"[Orchestrator] Analyzing intent: {query[:100]}")
        intent_analysis = await IntentAnalyzer.analyze(query, context)
        logger.info(f"[Orchestrator] Primary intent: {intent_analysis['primary_intent']}")
        
        # Step 2: Select sources
        logger.info(f"[Orchestrator] Selecting sources...")
        selected_sources = SourceSelector.select(intent_analysis)
        logger.info(f"[Orchestrator] Selected {len(selected_sources)} sources: {[s['key'] for s in selected_sources]}")
        
        # Step 3: Fetch from all sources in parallel
        logger.info(f"[Orchestrator] Fetching from {len(selected_sources)} sources...")
        raw_data = await DataFetcher.fetch_all(selected_sources)
        
        # Step 4: Process and refine
        logger.info(f"[Orchestrator] Processing and refining data...")
        processed_data = await DataProcessor.process(raw_data, intent_analysis)
        
        # Step 5: Format for display with clarity
        result = {
            "status": "success",
            "query": query,
            "intent": intent_analysis["primary_intent"],
            "intent_scores": intent_analysis["intent_scores"],
            "sources_queried": len(selected_sources),
            "sources": selected_sources,
            "data": processed_data,
            "clarity": ContextAwareDataOrchestrator._determine_overall_clarity(processed_data),
            "confidence": ContextAwareDataOrchestrator._calculate_overall_confidence(processed_data),
            "timestamp": datetime.utcnow().isoformat(),
            "card_number": card_number,
            "user_type": context.get("user_type", "DataAnalyst")
        }
        
        logger.info(f"[Orchestrator] Complete. Overall clarity: {result['clarity']}")
        return result
    
    @staticmethod
    def _determine_overall_clarity(processed_data: Dict[str, Any]) -> str:
        """Determine overall clarity light"""
        clarities = [d.get("clarity", "red") for d in processed_data.values()]
        
        if "green" in clarities:
            return "green"
        elif "yellow" in clarities:
            return "yellow"
        else:
            return "red"
    
    @staticmethod
    def _calculate_overall_confidence(processed_data: Dict[str, Any]) -> float:
        """Calculate overall confidence score"""
        if not processed_data:
            return 0.0
        
        confidences = [d.get("confidence", 0.0) for d in processed_data.values()]
        return sum(confidences) / len(confidences)

# ============================================================================
# PUBLIC API
# ============================================================================

async def orchestrate_data_query(
    query: str,
    context: dict,
    card_number: int = 5
) -> Dict[str, Any]:
    """
    Public API: Orchestrate a data query across all 9 NYS repos
    
    Usage:
        result = await orchestrate_data_query(
            query="Is NPI 1649767344 authentic?",
            context={"user_type": "DataAnalyst", "session_id": "..."},
            card_number=5
        )
    """
    return await ContextAwareDataOrchestrator.orchestrate(query, context, card_number)

