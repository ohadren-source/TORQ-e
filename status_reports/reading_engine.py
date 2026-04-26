"""
reading_engine.py
Consolidated reading engines for TORQ-e identity verification.
Unified interface for PDFs, academic sources, GitHub, web pages, and dynamic content.

Returns standardized verification results:
{
  "source": str,
  "confidence": float (0.0-1.0),
  "findings": str,
  "raw_data": dict,
  "timestamp": str
}
"""

import os
import logging
import json
from datetime import datetime
from typing import Optional

# Third-party imports (install as needed)
try:
    import PyPDF2
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

try:
    from github import Github
    HAS_PYGITHUB = True
except ImportError:
    HAS_PYGITHUB = False

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_WEBPOET = True
except ImportError:
    HAS_WEBPOET = False

logger = logging.getLogger(__name__)


# ============================================================================
# ENGINE 1: PDF EXTRACTION (Research Papers, Regulatory Docs)
# ============================================================================

def read_pdf(file_path: str) -> dict:
    """
    Extract text and metadata from PDF files.
    Use case: Research papers, credentials, regulatory documents.
    """
    if not HAS_PYPDF:
        logger.warning("PyPDF2 not installed. Install with: pip install pypdf2")
        return {
            "source": "pdf",
            "confidence": 0.0,
            "findings": "PDF reader not available",
            "raw_data": {},
            "timestamp": datetime.now().isoformat()
        }

    try:
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            metadata = pdf_reader.metadata or {}

            for page in pdf_reader.pages:
                text += page.extract_text()

        return {
            "source": "pdf",
            "confidence": 0.8,  # PDFs are generally reliable if they exist
            "findings": f"Extracted {len(text)} characters from {len(pdf_reader.pages)} pages",
            "raw_data": {
                "text": text[:2000],  # First 2000 chars
                "page_count": len(pdf_reader.pages),
                "metadata": {k: str(v) for k, v in metadata.items()}
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"PDF read error: {e}")
        return {
            "source": "pdf",
            "confidence": 0.0,
            "findings": f"PDF read failed: {str(e)}",
            "raw_data": {},
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# ENGINE 2: ACADEMIC REPOSITORY (PubMed, arXiv, University Sources)
# ============================================================================

def read_academic_sources(query: str, source: str = "pubmed") -> dict:
    """
    Query academic repositories for research and credentials.
    Sources: PubMed, arXiv, CrossRef
    Use case: Provider credentials, health research, evidence-based practice.
    """
    if not HAS_WEBPOET:
        logger.warning("requests/BeautifulSoup not installed.")
        return {
            "source": "academic",
            "confidence": 0.0,
            "findings": "Academic reader not available",
            "raw_data": {},
            "timestamp": datetime.now().isoformat()
        }

    try:
        if source == "pubmed":
            url = f"https://pubmed.ncbi.nlm.nih.gov/?term={query}&sort=date"
            headers = {"User-Agent": "TORQ-e/1.0"}
            resp = requests.get(url, headers=headers, timeout=8)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, 'html.parser')
            # Extract article titles and links
            articles = soup.find_all('a', {'class': 'docsum-title'})
            findings = [{"title": a.text.strip(), "url": a.get('href')} for a in articles[:5]]

            return {
                "source": "academic",
                "confidence": 0.85 if findings else 0.0,
                "findings": f"Found {len(findings)} academic articles matching '{query}'",
                "raw_data": {"articles": findings, "source": "pubmed"},
                "timestamp": datetime.now().isoformat()
            }

        elif source == "arxiv":
            url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=5"
            resp = requests.get(url, timeout=8)
            resp.raise_for_status()

            # Parse arXiv Atom feed (simple)
            entries = resp.text.split('<entry>')
            findings = [{"raw": e[:200]} for e in entries[1:6]]

            return {
                "source": "academic",
                "confidence": 0.8 if findings else 0.0,
                "findings": f"Found {len(findings)} arXiv papers matching '{query}'",
                "raw_data": {"entries": findings, "source": "arxiv"},
                "timestamp": datetime.now().isoformat()
            }

        else:
            raise ValueError(f"Unknown academic source: {source}")

    except Exception as e:
        logger.error(f"Academic source error: {e}")
        return {
            "source": "academic",
            "confidence": 0.0,
            "findings": f"Academic query failed: {str(e)}",
            "raw_data": {},
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# ENGINE 3: GITHUB (Code, Documentation, Credentials)
# ============================================================================

def read_github(username: str) -> dict:
    """
    Query GitHub for provider/organization profiles, repos, credentials.
    Use case: Provider background, code transparency, documentation.
    """
    if not HAS_PYGITHUB:
        logger.warning("PyGithub not installed. Install with: pip install PyGithub")
        return {
            "source": "github",
            "confidence": 0.0,
            "findings": "GitHub reader not available",
            "raw_data": {},
            "timestamp": datetime.now().isoformat()
        }

    try:
        token = os.getenv("GITHUB_TOKEN")
        g = Github(token) if token else Github()

        user = g.get_user(username)

        repos = [{"name": r.name, "stars": r.stargazers_count, "language": r.language}
                 for r in user.get_repos()[:5]]

        return {
            "source": "github",
            "confidence": 0.75 if user else 0.0,
            "findings": f"GitHub user '{username}' found with {user.public_repos} public repos",
            "raw_data": {
                "login": user.login,
                "name": user.name,
                "public_repos": user.public_repos,
                "followers": user.followers,
                "bio": user.bio,
                "repos": repos
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"GitHub read error: {e}")
        return {
            "source": "github",
            "confidence": 0.0,
            "findings": f"GitHub query failed: {str(e)}",
            "raw_data": {},
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# ENGINE 4: WEB PARSER (Health Blogs, Watchdog Sites, Registries)
# ============================================================================

def read_web_page(url: str, parse_type: str = "general") -> dict:
    """
    Parse web pages with structure extraction.
    Use case: Health blogs, watchdog alerts, provider registries, news.
    """
    if not HAS_WEBPOET:
        logger.warning("requests/BeautifulSoup not installed.")
        return {
            "source": "web",
            "confidence": 0.0,
            "findings": "Web parser not available",
            "raw_data": {},
            "timestamp": datetime.now().isoformat()
        }

    try:
        headers = {"User-Agent": "TORQ-e/1.0"}
        resp = requests.get(url, headers=headers, timeout=8)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, 'html.parser')

        if parse_type == "watchdog":
            # Look for alert/warning divs
            alerts = soup.find_all(['div', 'article'], {'class': ['alert', 'warning', 'inauthenticity-alert']})
            content = [a.get_text()[:300] for a in alerts[:3]]
        elif parse_type == "registry":
            # Look for table data (provider registries)
            tables = soup.find_all('table')
            content = [{"rows": len(t.find_all('tr')), "cols": len(t.find_all('th'))} for t in tables[:3]]
        else:  # general
            # Extract main content
            main_text = soup.get_text()[:1000]
            title = soup.find('title')
            content = {"title": title.text if title else "No title", "text": main_text}

        return {
            "source": "web",
            "confidence": 0.7,
            "findings": f"Parsed {len(soup.find_all())} elements from {url}",
            "raw_data": {"content": content, "url": url, "parse_type": parse_type},
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Web parse error: {e}")
        return {
            "source": "web",
            "confidence": 0.0,
            "findings": f"Web parse failed: {str(e)}",
            "raw_data": {},
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# ENGINE 5: PLAYWRIGHT (Dynamic Content, JavaScript-Heavy Sites)
# ============================================================================

def read_dynamic_page(url: str, selector: str = "body") -> dict:
    """
    Use Playwright to load and read JavaScript-heavy pages.
    Use case: Real-time registries, dynamic provider databases, interactive sites.
    """
    if not HAS_PLAYWRIGHT:
        logger.warning("Playwright not installed. Install with: pip install playwright && playwright install")
        return {
            "source": "dynamic",
            "confidence": 0.0,
            "findings": "Playwright not available",
            "raw_data": {},
            "timestamp": datetime.now().isoformat()
        }

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=10000)
            page.wait_for_load_state("networkidle")

            # Extract content from specified selector
            element = page.query_selector(selector)
            if element:
                content = element.inner_text()[:2000]
            else:
                content = page.content()[:2000]

            return {
                "source": "dynamic",
                "confidence": 0.8,
                "findings": f"Loaded and parsed {url} via Playwright",
                "raw_data": {
                    "url": url,
                    "selector": selector,
                    "content": content,
                    "title": page.title()
                },
                "timestamp": datetime.now().isoformat()
            }

    except Exception as e:
        logger.error(f"Playwright error: {e}")
        return {
            "source": "dynamic",
            "confidence": 0.0,
            "findings": f"Dynamic page load failed: {str(e)}",
            "raw_data": {},
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# UNIFIED QUERY INTERFACE
# ============================================================================

def run_verification_suite(provider_name: str, npi: Optional[str] = None) -> dict:
    """
    Run all reading engines for comprehensive provider verification.
    Aggregates confidence scores into a single reliability metric.
    """
    results = {
        "provider_name": provider_name,
        "npi": npi,
        "engines_run": [],
        "confidence_scores": {},
        "overall_confidence": 0.0,
        "timestamp": datetime.now().isoformat()
    }

    # Engine 1: Academic sources
    academic = read_academic_sources(f"{provider_name} credentials", source="pubmed")
    results["engines_run"].append(academic)
    results["confidence_scores"]["academic"] = academic.get("confidence", 0.0)

    # Engine 2: GitHub
    github = read_github(provider_name.lower().replace(" ", ""))
    results["engines_run"].append(github)
    results["confidence_scores"]["github"] = github.get("confidence", 0.0)

    # Engine 3: Web (watchdog)
    watchdog = read_web_page(f"https://google.com/search?q={provider_name}+inauthenticity", parse_type="watchdog")
    results["engines_run"].append(watchdog)
    results["confidence_scores"]["watchdog"] = watchdog.get("confidence", 0.0)

    # Calculate overall confidence (average of all engines)
    scores = list(results["confidence_scores"].values())
    results["overall_confidence"] = sum(scores) / len(scores) if scores else 0.0

    return results


# ============================================================================
# REQU