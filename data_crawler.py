"""
DATA CRAWLER SERVICE - TORQ-E
Crawls public Medicaid repositories and feeds every URL through reading_engine.py.
The reading engine is the sole content extractor — web pages, PDFs, dynamic pages.
NO DUMMY DATA — ALL CONTENT FROM REAL PUBLIC REPOSITORIES.
"""

import asyncio
import httpx
import tempfile
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re

import reading_engine

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_URLS = [
    # Card 1 & 2: Member & Provider Data
    "https://www.emedny.org/",
    "https://www.emedny.org/info/providerenrollment/",

    # Card 3: Managed Care Organizations & Plans
    "https://health.data.ny.gov",

    # Card 4 & 5: Government Stakeholder & Fraud Investigation
    "https://omig.ny.gov/",
    "https://its.ny.gov/",
]

# Domains that block server-side crawlers — never attempt, never log as errors
BLOCKED_DOMAINS = {
    "www.health.ny.gov",
    "health.ny.gov",
}

MAX_CRAWL_DEPTH = 2
REQUEST_TIMEOUT = 30.0
USER_AGENT = "TORQ-e DataCrawler/1.0 (NYS Medicaid Data Discovery)"

# Metric keyword map — used to tag each source with which metrics it covers
METRIC_PATTERNS = {
    "enrollment": r"enrollment|enrolled|members|beneficiar",
    "denial": r"denial|denied|rejected|rejection",
    "processing": r"processing|process|timeline|days",
    "compliance": r"compliance|compliant|audit|review",
    "fraud": r"fraud|suspicious|flagged|investigation",
    "quality": r"quality|data quality|accuracy|error",
    "stability": r"uptime|availability|outage|downtime|system status",
}


# ============================================================================
# DATA CRAWLER CLASS
# ============================================================================

class DataCrawler:
    def __init__(self):
        self.discovered_data: List[Dict] = []
        self.visited_urls: set = set()
        self.errors: List[Dict] = []
        self.total_urls_visited: int = 0
        self.sources_with_extracted_data: int = 0

    async def crawl(self) -> Dict[str, Any]:
        """Main entry point — crawl all base URLs via reading engine."""
        logger.info("Starting TORQ-e crawler (reading_engine as primary reader)...")

        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }

        async with httpx.AsyncClient(headers=headers, timeout=REQUEST_TIMEOUT, follow_redirects=True) as client:
            for base_url in BASE_URLS:
                logger.info(f"Crawling: {base_url}")
                try:
                    await self._crawl_url(client, base_url, depth=0)
                except Exception as e:
                    logger.error(f"Failed to crawl {base_url}: {e}")
                    self.errors.append({
                        "url": base_url,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat(),
                    })

        return self._generate_schema()

    async def _crawl_url(self, client: httpx.AsyncClient, url: str, depth: int = 0):
        """Fetch a URL, read it through reading_engine, then follow links."""
        if depth > MAX_CRAWL_DEPTH or url in self.visited_urls:
            return

        domain = urlparse(url).netloc
        if domain in BLOCKED_DOMAINS:
            return

        self.visited_urls.add(url)
        self.total_urls_visited += 1
        logger.info(f"  [depth={depth}] {url}")

        try:
            response = await client.get(url)

            # 403 = this domain blocks crawlers — blacklist it for the session
            if response.status_code == 403:
                BLOCKED_DOMAINS.add(domain)
                logger.info(f"  403 on {domain} — removed from corpus")
                return

            response.raise_for_status()

            content_type = response.headers.get("content-type", "").lower()

            if "pdf" in content_type or url.lower().endswith(".pdf"):
                # Route PDFs through reading_engine.read_pdf
                await self._read_pdf_url(url, response.content)
            else:
                # Route HTML/text through reading_engine.read_web_page,
                # then discover and follow links + PDF download refs
                await self._read_html_url(client, url, response.text, depth)

        except Exception as e:
            logger.error(f"  Error on {url}: {e}")
            self.errors.append({
                "url": url,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            })

    # ------------------------------------------------------------------
    # PDF READING via reading_engine.read_pdf
    # ------------------------------------------------------------------

    async def _read_pdf_url(self, url: str, content: bytes):
        """Write PDF bytes to a temp file and read via reading_engine."""
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            result = reading_engine.read_pdf(tmp_path)
            os.unlink(tmp_path)

            if result.get("confidence", 0) > 0:
                text = result.get("raw_data", {}).get("text", "")
                entry = self._build_entry(
                    url=url,
                    src_type="pdf",
                    fmt="PDF",
                    text_snippet=text[:2000],
                    confidence=result["confidence"],
                    description=result.get("findings", f"PDF: {url}"),
                )
                self.discovered_data.append(entry)
                self.sources_with_extracted_data += 1
                logger.info(f"    ✓ PDF read: {len(text)} chars")
            else:
                logger.warning(f"    ✗ PDF unreadable: {result.get('findings')}")

        except Exception as e:
            logger.warning(f"    ✗ PDF read failed for {url}: {e}")

    # ------------------------------------------------------------------
    # HTML READING via reading_engine.read_web_page
    # ------------------------------------------------------------------

    async def _read_html_url(self, client: httpx.AsyncClient, url: str, html: str, depth: int):
        """Read an HTML page via reading_engine, then discover links."""

        # reading_engine.read_web_page is sync — run in executor so we don't block
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, reading_engine.read_web_page, url, "general")

        if result.get("confidence", 0) > 0:
            raw = result.get("raw_data", {})
            content = raw.get("content", {})

            # Flatten content to a text snippet
            if isinstance(content, dict):
                title = content.get("title", "")
                text = content.get("text", "")
                snippet = f"{title}\n{text}".strip()
            elif isinstance(content, str):
                snippet = content
            else:
                snippet = str(content)

            entry = self._build_entry(
                url=url,
                src_type="web",
                fmt="HTML",
                text_snippet=snippet[:2000],
                confidence=result["confidence"],
                description=result.get("findings", f"Web page: {url}"),
            )
            self.discovered_data.append(entry)
            self.sources_with_extracted_data += 1
            logger.info(f"    ✓ Web read: {len(snippet)} chars via reading_engine")

        # Regardless of reading_engine result, use BeautifulSoup to follow links
        # (reading_engine doesn't expose link discovery)
        soup = BeautifulSoup(html, "lxml")
        domain = urlparse(url).netloc

        # Discover PDF download links and queue them
        pdf_links = soup.find_all("a", href=re.compile(r"\.pdf$", re.IGNORECASE))
        for link in pdf_links[:5]:
            href = link.get("href", "")
            if href:
                abs_url = urljoin(url, href)
                if abs_url not in self.visited_urls:
                    await asyncio.sleep(0.1)
                    await self._crawl_url(client, abs_url, depth + 1)

        # Follow internal HTML links
        if depth < MAX_CRAWL_DEPTH:
            for link in soup.find_all("a", href=True)[:10]:
                href = link["href"]
                abs_url = urljoin(url, href)
                link_domain = urlparse(abs_url).netloc
                if (link_domain == domain
                        and abs_url not in self.visited_urls
                        and self._should_follow(abs_url)):
                    await asyncio.sleep(0.1)
                    await self._crawl_url(client, abs_url, depth + 1)

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    def _build_entry(
        self,
        url: str,
        src_type: str,
        fmt: str,
        text_snippet: str,
        confidence: float,
        description: str,
    ) -> Dict:
        """Build a standard discovered_data entry with metric tags."""
        metrics_found = {}
        for metric_name, pattern in METRIC_PATTERNS.items():
            if re.search(pattern, text_snippet, re.IGNORECASE):
                metrics_found[metric_name] = True

        return {
            "type": src_type,
            "url": url,
            "description": description,
            "format": fmt,
            "metrics_found": metrics_found,
            "text_snippet": text_snippet,
            "confidence": confidence,
            "discovered_at": datetime.utcnow().isoformat(),
        }

    def _should_follow(self, url: str) -> bool:
        skip = [
            r"\.(jpg|jpeg|png|gif|css|js|ico|svg)$",
            r"(logout|signin|register|subscribe|captcha|recaptcha)",
            r"(facebook|twitter|linkedin|instagram)",
            r"#$",
        ]
        return not any(re.search(p, url, re.IGNORECASE) for p in skip)

    def _generate_schema(self) -> Dict[str, Any]:
        """Build the public_data_schema that Card 4's query engine consumes."""
        summary = {
            "web": len([d for d in self.discovered_data if d.get("type") == "web"]),
            "pdf": len([d for d in self.discovered_data if d.get("type") == "pdf"]),
        }

        return {
            "status": "success" if self.discovered_data else "partial",
            "timestamp": datetime.utcnow().isoformat(),
            "total_urls_visited": self.total_urls_visited,
            "base_repositories": BASE_URLS,
            "total_data_sources_discovered": len(self.discovered_data),
            "total_sources_with_extracted_data": self.sources_with_extracted_data,
            "discovered_data": self.discovered_data,
            "errors": self.errors,
            "reading_engine_integrated": True,
            "crawler_stack": "httpx + reading_engine (web/pdf/dynamic)",
            "summary": summary,
        }


# ============================================================================
# ENTRY POINTS
# ============================================================================

async def discover_public_data() -> Dict[str, Any]:
    """Async entry point — run crawler and return schema."""
    crawler = DataCrawler()
    schema = await crawler.crawl()
    logger.info(f"Crawl complete: {schema['total_data_sources_discovered']} sources, "
                f"{schema['total_sources_with_extracted_data']} with content")
    if schema["errors"]:
        logger.warning(f"{len(schema['errors'])} errors during crawl")
    return schema


def get_public_data_schema() -> Dict[str, Any]:
    """Sync wrapper for FastAPI startup."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Already inside an event loop (e.g. uvicorn) — create a new one in a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, discover_public_data())
                return future.result()
    except RuntimeError:
        pass
    return asyncio.run(discover_public_data())


if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO)
    schema = asyncio.run(discover_public_data())
    print(json.dumps(schema, indent=2, default=str))
