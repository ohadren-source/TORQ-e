"""
DATA CRAWLER SERVICE - TORQ-E
httpx + BeautifulSoup + Scrapy + Splash stack
Real data extraction from public Medicaid repositories
NO DUMMY DATA - ONLY REAL PUBLIC REPOSITORY DATA
"""

import asyncio
import httpx
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import json
import re

# Scrapy imports
try:
    import scrapy
    from scrapy.crawler import CrawlerProcess
    from scrapy.http import Request as ScrapyRequest
    HAS_SCRAPY = True
except ImportError:
    HAS_SCRAPY = False

# Splash imports (via scrapy-splash or direct HTTP to Splash server)
try:
    import requests as _requests
    SPLASH_URL = "http://localhost:8050"
    HAS_SPLASH = True
except ImportError:
    HAS_SPLASH = False

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
    "https://its.ny.gov/"
]

MAX_CRAWL_DEPTH = 2
REQUEST_TIMEOUT = 30.0
USER_AGENT = "TORQ-e DataCrawler/1.0 (NYS Medicaid Data Discovery)"

# ============================================================================
# DATA CRAWLER CLASS
# ============================================================================

class DataCrawler:
    def __init__(self):
        self.discovered_data = []
        self.visited_urls = set()
        self.errors = []
        self.total_urls_visited = 0
        self.sources_with_extracted_data = 0

    async def crawl(self) -> Dict[str, Any]:
        """
        Main entry point: Crawl all base URLs using httpx + BeautifulSoup + Scrapy + Splash stack
        Extract real data from public repositories
        """
        logger.info("Starting data crawler with httpx + BeautifulSoup + Scrapy + Splash stack...")

        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive"
        }

        async with httpx.AsyncClient(headers=headers, timeout=REQUEST_TIMEOUT) as client:
            for base_url in BASE_URLS:
                logger.info(f"🔍 Crawling: {base_url}")
                try:
                    await self._crawl_url(client, base_url, depth=0)
                except Exception as e:
                    logger.error(f"❌ Failed to crawl {base_url}: {str(e)}")
                    self.errors.append({
                        "url": base_url,
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    })

        # --- ENGINE 3: SCRAPY structured crawl (sync, runs after httpx pass) ---
        if HAS_SCRAPY:
            try:
                scrapy_data = self._run_scrapy_crawl()
                self.discovered_data.extend(scrapy_data)
                self.sources_with_extracted_data += len(scrapy_data)
                logger.info(f"✅ Scrapy pass complete: {len(scrapy_data)} additional sources")
            except Exception as e:
                logger.warning(f"⚠️  Scrapy pass failed: {e}")
                self.errors.append({"engine": "scrapy", "error": str(e), "timestamp": datetime.utcnow().isoformat()})
        else:
            logger.warning("Scrapy not installed — skipping Scrapy engine pass")

        # --- ENGINE 4: SPLASH for JavaScript-heavy pages ---
        js_heavy_urls = [
            "https://health.data.ny.gov",
            "https://omig.ny.gov/"
        ]
        for url in js_heavy_urls:
            try:
                splash_data = self._fetch_via_splash(url)
                if splash_data:
                    self.discovered_data.append(splash_data)
                    self.sources_with_extracted_data += 1
                    logger.info(f"✅ Splash fetched: {url}")
            except Exception as e:
                logger.warning(f"⚠️  Splash failed for {url}: {e}")
                self.errors.append({"engine": "splash", "url": url, "error": str(e), "timestamp": datetime.utcnow().isoformat()})

        return self._generate_schema()

    def _run_scrapy_crawl(self) -> List[Dict[str, Any]]:
        """
        Run a Scrapy spider synchronously to extract structured data
        from public Medicaid repositories.
        Returns list of discovered data entries.
        """
        if not HAS_SCRAPY:
            return []

        collected = []

        class TorqeSpider(scrapy.Spider):
            name = "torqe_medicaid"
            start_urls = BASE_URLS
            custom_settings = {
                "ROBOTSTXT_OBEY": True,
                "DOWNLOAD_DELAY": 0.5,
                "DEPTH_LIMIT": 2,
                "LOG_ENABLED": False,
            }

            def parse(self, response):
                # Extract tables
                for i, table in enumerate(response.css("table")[:5]):
                    headers = table.css("th::text").getall()
                    rows = table.css("tr")
                    if rows:
                        collected.append({
                            "type": "table",
                            "url": response.url,
                            "description": f"Scrapy Table #{i+1}: {' '.join(headers)[:200]}",
                            "format": "HTML",
                            "row_count": len(rows),
                            "discovered_at": datetime.utcnow().isoformat(),
                            "confidence": 0.88,
                            "engine": "scrapy"
                        })

                # Extract download links
                for link in response.css("a[href$='.csv'], a[href$='.xlsx'], a[href$='.json'], a[href$='.pdf'], a[href$='.xml']")[:5]:
                    href = link.attrib.get("href", "")
                    text = link.css("::text").get("").strip()
                    if href:
                        ext = href.split(".")[-1].lower()
                        collected.append({
                            "type": "download",
                            "url": response.urljoin(href),
                            "description": f"{text} ({ext})",
                            "format": ext.upper(),
                            "page_url": response.url,
                            "discovered_at": datetime.utcnow().isoformat(),
                            "confidence": 0.82,
                            "engine": "scrapy"
                        })

                # Follow internal links
                for href in response.css("a::attr(href)").getall()[:10]:
                    yield response.follow(href, self.parse)

        process = CrawlerProcess(settings={"LOG_ENABLED": False})
        process.crawl(TorqeSpider)
        process.start()

        return collected

    def _fetch_via_splash(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Use Splash to render JavaScript-heavy pages and extract content.
        Splash runs at localhost:8050 (docker: scrapinghub/splash).
        """
        if not HAS_SPLASH:
            return None

        try:
            splash_endpoint = f"{SPLASH_URL}/render.html"
            params = {
                "url": url,
                "wait": 2,          # seconds to wait for JS to execute
                "timeout": 20,
                "resource_timeout": 10
            }
            resp = _requests.get(splash_endpoint, params=params, timeout=25)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "lxml")
            title = soup.find("title")
            text_preview = soup.get_text()[:500]

            # Count tables and downloads in rendered content
            tables = soup.find_all("table")
            downloads = soup.find_all("a", href=re.compile(r"\.(csv|xlsx|json|pdf|xml)$", re.IGNORECASE))

            return {
                "type": "dynamic",
                "url": url,
                "description": f"Splash-rendered: {title.text.strip() if title else url} | {len(tables)} tables, {len(downloads)} downloads",
                "format": "HTML (JS-rendered)",
                "tables_found": len(tables),
                "downloads_found": len(downloads),
                "text_preview": text_preview,
                "discovered_at": datetime.utcnow().isoformat(),
                "confidence": 0.85,
                "engine": "splash"
            }

        except Exception as e:
            logger.error(f"Splash render failed for {url}: {e}")
            return None

    async def _crawl_url(self, client: httpx.AsyncClient, url: str, depth: int = 0):
        """
        Recursively crawl URL with BeautifulSoup parsing
        Extract data tables, links, metrics
        """
        if depth > MAX_CRAWL_DEPTH:
            return

        if url in self.visited_urls:
            return

        self.visited_urls.add(url)
        self.total_urls_visited += 1

        logger.info(f"  [Depth {depth}] Analyzing: {url}")

        try:
            # Fetch page with httpx
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()

            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.text, 'lxml')

            # Extract data from this page
            await self._extract_page_data(soup, url)

            # Find and follow internal links (same domain only)
            domain = urlparse(url).netloc
            links = soup.find_all('a', href=True)

            for link in links[:10]:  # Limit to prevent explosion
                href = link['href']
                if href:
                    absolute_url = urljoin(url, href)
                    link_domain = urlparse(absolute_url).netloc

                    # Only follow same-domain links
                    if link_domain == domain and absolute_url not in self.visited_urls:
                        if self._should_follow_link(absolute_url):
                            await asyncio.sleep(0.1)  # Be respectful
                            await self._crawl_url(client, absolute_url, depth + 1)

        except Exception as e:
            logger.error(f"Error analyzing {url}: {str(e)}")
            self.errors.append({
                "url": url,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })

    async def _extract_page_data(self, soup: BeautifulSoup, url: str):
        """
        Extract structured data from HTML:
        - Tables
        - Key-value metrics
        - Download links
        - API endpoints
        """
        # Extract tables
        tables = soup.find_all('table')
        for i, table in enumerate(tables[:5]):  # Limit to first 5 tables
            try:
                rows = table.find_all('tr')
                if rows:
                    table_text = ' '.join([cell.get_text().strip() for cell in rows[0].find_all(['td', 'th'])])[:200]

                    data_entry = {
                        "type": "table",
                        "url": url,
                        "description": f"Table #{i+1}: {table_text}",
                        "format": "HTML",
                        "row_count": len(rows),
                        "discovered_at": datetime.utcnow().isoformat(),
                        "confidence": 0.85
                    }

                    self.discovered_data.append(data_entry)
                    self.sources_with_extracted_data += 1
                    logger.info(f"    ✓ Found table with {len(rows)} rows")
            except Exception as e:
                logger.warning(f"Table extraction failed: {e}")

        # Extract metrics (look for common patterns)
        patterns = {
            "enrollment": r"enrollment|enrolled|members|beneficiaries",
            "denial": r"denial|denied|rejected|rejection",
            "processing": r"processing|process|timeline|days",
            "compliance": r"compliance|compliant|audit|review",
            "fraud": r"fraud|suspicious|flagged|investigation",
            "quality": r"quality|data quality|accuracy|error"
        }

        text_content = soup.get_text()
        found_metrics = {}

        for metric_name, pattern in patterns.items():
            if re.search(pattern, text_content, re.IGNORECASE):
                found_metrics[metric_name] = True
                logger.info(f"    ✓ Found metric indicator: {metric_name}")

        if found_metrics:
            data_entry = {
                "type": "metrics",
                "url": url,
                "description": f"Metrics page: {', '.join(found_metrics.keys())}",
                "format": "HTML",
                "metrics_found": found_metrics,
                "discovered_at": datetime.utcnow().isoformat(),
                "confidence": 0.70
            }

            self.discovered_data.append(data_entry)
            self.sources_with_extracted_data += 1

        # Extract download links
        downloads = soup.find_all('a', href=re.compile(r'\.(csv|xlsx|xls|json|pdf|xml)$', re.IGNORECASE))
        for download in downloads[:5]:
            href = download.get('href', '')
            text = download.get_text().strip()

            if href:
                full_url = urljoin(url, href)
                file_ext = href.split('.')[-1].lower()

                data_entry = {
                    "type": "download",
                    "url": full_url,
                    "description": f"{text} ({file_ext})",
                    "format": file_ext.upper(),
                    "page_url": url,
                    "discovered_at": datetime.utcnow().isoformat(),
                    "confidence": 0.80
                }

                self.discovered_data.append(data_entry)
                self.sources_with_extracted_data += 1
                logger.info(f"    ✓ Found downloadable: {text}")

    def _should_follow_link(self, url: str) -> bool:
        """
        Decide whether to follow a link
        Avoid common dead-ends and external redirects
        """
        skip_patterns = [
            r'\.(jpg|jpeg|png|gif|css|js|ico|svg)$',
            r'(logout|signin|register|subscribe)',
            r'(facebook|twitter|linkedin|instagram)',
            r'(captcha|recaptcha)',
            r'#$'  # Anchor-only links
        ]

        for pattern in skip_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False

        return True

    def _generate_schema(self) -> Dict[str, Any]:
        """
        Generate the public_data_schema that Card 4 expects
        """
        # Count different types of discovered data
        summary = {
            "tables": len([d for d in self.discovered_data if d.get("type") == "table"]),
            "downloads": len([d for d in self.discovered_data if d.get("type") == "download"]),
            "apis": len([d for d in self.discovered_data if d.get("type") == "api"]),
            "dashboards": len([d for d in self.discovered_data if d.get("type") == "dashboard"]),
            "metrics": len([d for d in self.discovered_data if d.get("type") == "metrics"])
        }

        schema = {
            "status": "success" if self.discovered_data else "partial",
            "timestamp": datetime.utcnow().isoformat(),
            "total_urls_visited": self.total_urls_visited,
            "base_repositories": BASE_URLS,
            "total_data_sources_discovered": len(self.discovered_data),
            "total_sources_with_extracted_data": self.sources_with_extracted_data,
            "discovered_data": self.discovered_data,
            "errors": self.errors,
            "reading_engine_integrated": False,
            "crawler_stack": "httpx + BeautifulSoup + Scrapy + Splash",
            "engines_available": {
                "httpx": True,
                "beautifulsoup": True,
                "scrapy": HAS_SCRAPY,
                "splash": HAS_SPLASH
            },
            "summary": summary,

            # Card 4 metric buckets (will be populated from discovered data)
            "enrollment_rate": self._extract_metric("enrollment", "enrollment_rate"),
            "claims_processing": self._extract_metric("processing", "claims_processing"),
            "data_quality": self._extract_metric("quality", "data_quality"),
            "audit_trail": self._extract_metric("audit", "audit_trail"),
            "compliance": self._extract_metric("compliance", "compliance"),
            "system_stability": self._extract_metric("fraud", "system_stability")
        }

        return schema

    def _extract_metric(self, metric_type: str, metric_key: str) -> Dict[str, Any]:
        """
        Extract metric data for Card 4
        """
        matching_sources = [
            d for d in self.discovered_data
            if metric_type.lower() in str(d).lower()
        ]

        if matching_sources:
            return {
                "value": len(matching_sources),
                "unit": "sources_found",
                "confidence_score": 0.75,
                "sources": matching_sources[:3],
                "status": "data_available"
            }
        else:
            return {
                "value": None,
                "confidence_score": 0.0,
                "sources": [],
                "status": "no_data"
            }


# ============================================================================
# EXECUTION
# ============================================================================

async def discover_public_data() -> Dict[str, Any]:
    """
    Entry point: Run the crawler and return discovered data schema
    """
    crawler = DataCrawler()
    schema = await crawler.crawl()

    logger.info(f"✅ Crawl complete: {schema['total_data_sources_discovered']} sources discovered")
    logger.info(f"📊 Extracted data from {schema['total_sources_with_extracted_data']} sources")

    if schema['errors']:
        logger.warning(f"⚠️  {len(schema['errors'])} errors during crawl")

    return schema


# Synchronous wrapper for FastAPI integration
def get_public_data_schema() -> Dict[str, Any]:
    """
    Synchronous wrapper - call from FastAPI routes
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(discover_public_data())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    schema = asyncio.run(discover_public_data())
    print(json.dumps(schema, indent=2, default=str))
