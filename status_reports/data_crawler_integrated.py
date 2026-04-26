"""
DATA CRAWLER SERVICE - TORQ-E
httpx + BeautifulSoup + Scrapy + Splash stack
Discover and map available data from public Medicaid repositories
NO DUMMY DATA - ONLY REAL PUBLIC REPOSITORY DATA

Unified Substrate Repositories (for all Cards 1-5):
- Card 1 & 2 (Member & Provider): eMedNY, Health.NY.gov Medicaid Program
- Card 3 (MCO Plans): MCO Directory, Health Data NY, Managed Care Reports
- Card 4 & 5 (Governance & Fraud): OHIP, OMIG, ITS, Medicaid Reference

Integration: Uses reading_engine.py to extract data from discovered sources in multiple formats
- PDF: research papers, regulatory docs, credentials
- Web Pages: general content, watchdog sites, registries (httpx + BeautifulSoup)
- Dynamic Content: JavaScript-heavy dashboards, interactive tools (Splash)
- Structured Crawl: Scrapy spider for table/download discovery
- Academic Sources: PubMed, arXiv for research verification
- GitHub: provider background, code transparency, documentation
"""

import asyncio
import httpx
import requests as _requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from urllib.parse import urljoin, urlparse
import logging
import os
import sys
import re

# Scrapy
try:
    import scrapy
    from scrapy.crawler import CrawlerProcess
    HAS_SCRAPY = True
except ImportError:
    HAS_SCRAPY = False

# Splash
SPLASH_URL = os.getenv("SPLASH_URL", "http://localhost:8050")
HAS_SPLASH = True  # requests already imported above

# Import reading_engine for multi-format data extraction
try:
    from reading_engine import (
        read_pdf,
        read_web_page,
        read_dynamic_page,
        read_academic_sources,
        read_github
    )
    HAS_READING_ENGINE = True
except ImportError:
    HAS_READING_ENGINE = False
    logger.warning("reading_engine not available - discovery-only mode")

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_URLS = [
    # Card 1 & 2: Member & Provider Data
    "https://www.emedny.org/",
    "https://www.emedny.org/info/providerenrollment/",
    "https://www.health.ny.gov/health_care/medicaid/program/update/main.htm",

    # Card 3: Managed Care Organizations & Plans
    "https://www.health.ny.gov/health_care/managed_care/plans/mcp_dir_by_plan.htm",
    "https://www.health.ny.gov/health_care/managed_care/reports/enrollment/monthly/",
    "https://health.data.ny.gov",
    "https://www.health.ny.gov/health_care/managed_care/reports/",

    # Card 4 & 5: Government Stakeholder & Fraud Investigation
    "https://ohipdocs.health.ny.gov/ohipdocs/web/",
    "https://omig.ny.gov/",
    "https://its.ny.gov/",
    "https://www.health.ny.gov/health_care/medicaid/reference/",
    "https://www.health.ny.gov/health_care/medicaid/publications/"
]

# Maximum depth for folder crawling (prevent infinite loops)
MAX_CRAWL_DEPTH = 3

# Data types to look for
DATA_TYPES = {
    "table": "HTML table with data",
    "csv": "Downloadable CSV file",
    "json": "JSON API or data file",
    "xml": "XML data file",
    "download": "Data download link",
    "dashboard": "Interactive dashboard/query tool",
    "report": "Report or statistics page"
}

# ============================================================================
# DATA CRAWLER
# ============================================================================

class PublicRepositoryCrawler:
    """
    Crawls public Medicaid repositories to discover available data.
    Maps data sources, formats, and access patterns.
    """

    def __init__(self):
        self.discovered_data = []
        self.visited_urls = set()
        self.errors = []

    def crawl(self) -> Dict[str, Any]:
        """
        Main entry point: Crawl all base URLs using httpx + BeautifulSoup + Scrapy + Splash stack
        """
        logger.info("Starting repository crawl with httpx + BeautifulSoup + Scrapy + Splash stack...")

        # --- ENGINE 1 & 2: httpx + BeautifulSoup async pass ---
        asyncio.run(self._crawl_all_httpx())

        # --- ENGINE 3: Scrapy structured crawl ---
        if HAS_SCRAPY:
            try:
                scrapy_data = self._run_scrapy_crawl()
                self.discovered_data.extend(scrapy_data)
                logger.info(f"✅ Scrapy pass: {len(scrapy_data)} additional sources")
            except Exception as e:
                logger.warning(f"⚠️  Scrapy pass failed: {e}")
                self.errors.append({"engine": "scrapy", "error": str(e)})
        else:
            logger.warning("Scrapy not installed — skipping Scrapy engine pass")

        # --- ENGINE 4: Splash for JS-heavy URLs ---
        js_heavy_urls = [
            "https://health.data.ny.gov",
            "https://omig.ny.gov/"
        ]
        for url in js_heavy_urls:
            try:
                splash_entry = self._fetch_via_splash(url)
                if splash_entry:
                    self.discovered_data.append(splash_entry)
                    logger.info(f"✅ Splash fetched: {url}")
            except Exception as e:
                logger.warning(f"⚠️  Splash failed for {url}: {e}")
                self.errors.append({"engine": "splash", "url": url, "error": str(e)})

        return self._generate_schema()

    async def _crawl_all_httpx(self):
        """Async httpx pass over all base URLs."""
        headers = {
            "User-Agent": "TORQ-e DataCrawler/1.0 (NYS Medicaid Data Discovery)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
            for base_url in BASE_URLS:
                logger.info(f"🔍 httpx crawling: {base_url}")
                try:
                    await self._crawl_url_httpx(client, base_url, depth=0)
                except Exception as e:
                    logger.error(f"❌ Failed to crawl {base_url}: {e}")
                    self.errors.append({"url": base_url, "error": str(e)})

    async def _crawl_url_httpx(self, client: httpx.AsyncClient, url: str, depth: int = 0):
        """
        Recursively crawl a URL using httpx + BeautifulSoup.
        """
        if depth > MAX_CRAWL_DEPTH or url in self.visited_urls:
            return

        self.visited_urls.add(url)
        logger.info(f"  [Depth {depth}] Analyzing: {url}")

        try:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            self._discover_page_data_bs(soup, url)

            domain = urlparse(url).netloc
            for link in soup.find_all("a", href=True)[:10]:
                href = link["href"]
                absolute_url = urljoin(url, href)
                link_domain = urlparse(absolute_url).netloc
                if link_domain == domain and absolute_url not in self.visited_urls:
                    if self._should_follow_link(absolute_url):
                        await asyncio.sleep(0.1)
                        await self._crawl_url_httpx(client, absolute_url, depth + 1)

        except Exception as e:
            logger.error(f"Error analyzing {url}: {e}")
            self.errors.append({"url": url, "error": str(e)})

    def _discover_page_data_bs(self, soup: BeautifulSoup, url: str):
        """
        Analyze a BeautifulSoup page for available data sources.
        """
        # Tables
        for i, table in enumerate(soup.find_all("table")[:5]):
            rows = table.find_all("tr")
            table_text = " ".join(cell.get_text().strip() for cell in rows[0].find_all(["td", "th"]))[:200] if rows else ""
            data_entry = {
                "type": "table",
                "url": url,
                "description": f"HTML Table #{i+1}: {table_text}",
                "format": "HTML",
                "row_count": len(rows),
                "discovered_at": datetime.utcnow().isoformat(),
                "confidence": 0.85,
                "engine": "httpx+bs4"
            }
            if HAS_READING_ENGINE:
                extraction = self._extract_source_data(url, "web", parse_type="general")
                if extraction.get("raw_data"):
                    data_entry["extracted_data"] = extraction.get("raw_data")
                    data_entry["confidence"] = extraction.get("confidence", 0.7)
            self.discovered_data.append(data_entry)
            logger.info(f"    Found table on {url}")

        # Downloads
        for download in soup.find_all("a", href=re.compile(r"\.(csv|xlsx|xls|json|pdf|xml)$", re.IGNORECASE))[:5]:
            href = download.get("href", "")
            text = download.get_text().strip()
            if href:
                full_url = urljoin(url, href)
                file_ext = href.split(".")[-1].lower()
                data_entry = {
                    "type": "download",
                    "url": full_url,
                    "description": f"{text} ({file_ext})",
                    "format": file_ext.upper(),
                    "page_url": url,
                    "discovered_at": datetime.utcnow().isoformat(),
                    "confidence": 0.82,
                    "engine": "httpx+bs4"
                }
                if HAS_READING_ENGINE and file_ext == "pdf":
                    try:
                        pdf_path = self._download_file(full_url, file_ext)
                        if pdf_path:
                            extraction = read_pdf(pdf_path)
                            data_entry["extracted_data"] = extraction.get("raw_data")
                            data_entry["confidence"] = extraction.get("confidence", 0.8)
                            try:
                                os.remove(pdf_path)
                            except:
                                pass
                    except Exception as e:
                        logger.warning(f"PDF extraction failed for {full_url}: {e}")
                self.discovered_data.append(data_entry)
                logger.info(f"    Found downloadable data: {text}")

        # API endpoints
        for api_link in soup.find_all("a", href=re.compile(r"/api/"))[:5]:
            href = api_link.get("href", "")
            text = api_link.get_text().strip()
            if href:
                api_url = urljoin(url, href)
                data_entry = {
                    "type": "api",
                    "url": api_url,
                    "description": f"API endpoint: {text}",
                    "format": "JSON/API",
                    "page_url": url,
                    "discovered_at": datetime.utcnow().isoformat(),
                    "confidence": 0.85,
                    "engine": "httpx+bs4"
                }
                self.discovered_data.append(data_entry)
                logger.info(f"    Found API endpoint: {text}")

        # Dashboards
        page_text = soup.get_text().lower()
        title_tag = soup.find("title")
        page_title = title_tag.get_text().lower() if title_tag else ""
        if any(kw in page_text or kw in page_title for kw in ["dashboard", "report", "statistics", "metrics", "data view"]):
            data_entry = {
                "type": "dashboard",
                "url": url,
                "description": f"Data dashboard/report: {title_tag.get_text() if title_tag else url}",
                "format": "Interactive",
                "discovered_at": datetime.utcnow().isoformat(),
                "confidence": 0.75,
                "engine": "httpx+bs4"
            }
            if HAS_READING_ENGINE:
                extraction = read_dynamic_page(url, selector="body")
                if extraction.get("raw_data"):
                    data_entry["extracted_data"] = extraction.get("raw_data")
                    data_entry["confidence"] = extraction.get("confidence", 0.80)
            self.discovered_data.append(data_entry)
            logger.info(f"    Found dashboard: {page_title}")

    def _run_scrapy_crawl(self) -> List[Dict[str, Any]]:
        """Scrapy spider pass for structured table and download extraction."""
        if not HAS_SCRAPY:
            return []

        collected = []

        class TorqeSpider(scrapy.Spider):
            name = "torqe_integrated"
            start_urls = BASE_URLS
            custom_settings = {
                "ROBOTSTXT_OBEY": True,
                "DOWNLOAD_DELAY": 0.5,
                "DEPTH_LIMIT": 2,
                "LOG_ENABLED": False,
            }

            def parse(self, response):
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
                for link in response.css("a[href$='.csv'], a[href$='.xlsx'], a[href$='.json'], a[href$='.pdf']")[:5]:
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
                for href in response.css("a::attr(href)").getall()[:10]:
                    yield response.follow(href, self.parse)

        process = CrawlerProcess(settings={"LOG_ENABLED": False})
        process.crawl(TorqeSpider)
        process.start()
        return collected

    def _fetch_via_splash(self, url: str) -> Optional[Dict[str, Any]]:
        """Use Splash to render JavaScript-heavy pages and extract content."""
        try:
            resp = _requests.get(
                f"{SPLASH_URL}/render.html",
                params={"url": url, "wait": 2, "timeout": 20, "resource_timeout": 10},
                timeout=25
            )
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")
            title_tag = soup.find("title")
            title = title_tag.get_text().strip() if title_tag else url
            tables = soup.find_all("table")
            downloads = soup.find_all("a", href=re.compile(r"\.(csv|xlsx|json|pdf|xml)$", re.IGNORECASE))
            return {
                "type": "dynamic",
                "url": url,
                "description": f"Splash-rendered: {title} | {len(tables)} tables, {len(downloads)} downloads",
                "format": "HTML (JS-rendered)",
                "tables_found": len(tables),
                "downloads_found": len(downloads),
                "discovered_at": datetime.utcnow().isoformat(),
                "confidence": 0.85,
                "engine": "splash"
            }
        except Exception as e:
            logger.error(f"Splash render failed for {url}: {e}")
            return None

    def _extract_source_data(self, url: str, source_type: str, parse_type: str = "general") -> Dict[str, Any]:
        """
        Route to appropriate reading_engine function based on source type.
        Returns standardized result: {source, confidence, findings, raw_data, timestamp}
        """
        if not HAS_READING_ENGINE:
            return {"confidence": 0.0, "findings": "Reading engine unavailable"}

        try:
            if source_type == "web":
                return read_web_page(url, parse_type=parse_type)
            elif source_type == "dynamic":
                return read_dynamic_page(url)
            elif source_type == "academic":
                # For academic sources, query for content from the page text
                return read_web_page(url, parse_type="general")
            else:
                return read_web_page(url, parse_type=parse_type)
        except Exception as e:
            logger.warning(f"Data extraction failed for {url}: {e}")
            return {"confidence": 0.0, "findings": f"Extraction error: {str(e)}"}

    def _download_file(self, url: str, file_ext: str) -> Optional[str]:
        """
        Temporarily download a file for processing.
        Returns path to temporary file, or None if download fails.
        """
        try:
            import requests
            import tempfile

            response = requests.get(url, timeout=15)
            response.raise_for_status()

            # Create temporary file
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f"torq_e_{datetime.utcnow().timestamp()}.{file_ext}")

            with open(temp_path, 'wb') as f:
                f.write(response.content)

            logger.info(f"Downloaded {url} to {temp_path}")
            return temp_path

        except Exception as e:
            logger.warning(f"Failed to download {url}: {e}")
            return None

    def _should_follow_link(self, url: str) -> bool:
        """
        Determine if we should follow this link
        """
        # Skip common non-data pages
        skip_patterns = [
            "/login", "/signin", "/logout",
            "/search", "/search?",
            "/contact", "/about",
            "/help", "/faq",
            ".pdf", ".doc", ".jpg", ".png", ".gif"
        ]

        url_lower = url.lower()
        for pattern in skip_patterns:
            if pattern in url_lower:
                return False

        return True

    def _generate_schema(self) -> Dict[str, Any]:
        """
        Generate final data schema from discovered and extracted data.
        Includes quality metrics and confidence scores based on real source assessment.
        """
        # Count sources by type
        type_counts = {}
        for data in self.discovered_data:
            dtype = data.get("type", "unknown")
            type_counts[dtype] = type_counts.get(dtype, 0) + 1

        # Calculate extraction statistics
        extracted_count = len([d for d in self.discovered_data if "extracted_data" in d])
        avg_confidence = sum([d.get("confidence", 0.0) for d in self.discovered_data]) / len(self.discovered_data) if self.discovered_data else 0.0

        # Confidence mapping by source quality
        source_confidence_map = {
            "emedny.org": 0.95,          # Official, daily updated
            "health.ny.gov": 0.85,       # Official, weekly updated
            "health.data.ny.gov": 0.80,  # State data portal, varies
            "omig.ny.gov": 0.90,         # Fraud investigation authority
            "ohipdocs.health.ny.gov": 0.85,  # Government documentation
            "its.ny.gov": 0.80,          # IT services portal
            "dashboard": 0.75,           # Interactive dashboards, real-time but unverified
            "table": 0.70,               # HTML tables, format varies
            "api": 0.85,                 # Structured data
            "pdf": 0.60,                 # Static documents, can be outdated
        }

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "schema_version": "1.0",
            "base_repositories": BASE_URLS,
            "reading_engine_integrated": HAS_READING_ENGINE,
            "total_urls_visited": len(self.visited_urls),
            "total_data_sources_discovered": len(self.discovered_data),
            "total_sources_with_extracted_data": extracted_count,
            "average_confidence_score": round(avg_confidence, 3),
            "discovered_data": self.discovered_data,
            "errors": self.errors,
            "summary": {
                "tables": type_counts.get("table", 0),
                "downloads": type_counts.get("download", 0),
                "apis": type_counts.get("api", 0),
                "dashboards": type_counts.get("dashboard", 0),
            },
            "quality_metrics": {
                "extraction_coverage": round(extracted_count / len(self.discovered_data), 2) if self.discovered_data else 0.0,
                "average_confidence": round(avg_confidence, 3),
                "sources_by_confidence": self._summarize_confidence_tiers()
            },
            "confidence_thresholds": {
                "high": 0.85,      # Official government sources
                "medium": 0.70,    # Published data, reputable sources
                "low": 0.50,       # Archived or aggregated data
                "very_low": 0.0    # Unavailable or failed extraction
            }
        }

    def _summarize_confidence_tiers(self) -> Dict[str, int]:
        """
        Summarize data sources by confidence tier.
        """
        tiers = {"high": 0, "medium": 0, "low": 0, "unavailable": 0}

        for data in self.discovered_data:
            confidence = data.get("confidence", 0.0)
            if confidence >= 0.85:
                tiers["high"] += 1
            elif confidence >= 0.70:
                tiers["medium"] += 1
            elif confidence >= 0.50:
                tiers["low"] += 1
            else:
                tiers["unavailable"] += 1

        return tiers


# ============================================================================
# ASYNC WRAPPER FOR FASTAPI
# ============================================================================

async def discover_public_data() -> Dict[str, Any]:
    """
    FastAPI endpoint to trigger data discovery.
    Returns schema of available data from public repositories.
    Stack: httpx + BeautifulSoup + Scrapy + Splash
    """
    crawler = PublicRepositoryCrawler()
    return crawler.crawl()


# ============================================================================
# COMMAND LINE USAGE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    crawler = PublicRepositoryCrawler()
    schema = crawler.crawl()

    # Save schema to file
    with open("public_data_schema.json", "w") as f:
        json.dump(schema, f, indent=2)

    print("\n" + "="*80)
    print("DATA DISCOVERY & EXTRACTION COMPLETE")
    print("="*80)
    print(f"Reading Engine Integrated: {schema['reading_engine_integrated']}")
    print(f"\nRepositories Crawled:")
    for url in BASE_URLS:
        print(f"  - {url}")
    print(f"\nDiscovery Results:")
    print(f"  - URLs Visited: {schema['total_urls_visited']}")
    print(f"  - Data Sources Discovered: {schema['total_data_sources_discovered']}")
    print(f"  - Sources with Extracted Data: {schema['total_sources_with_extracted_data']}")
    print(f"\nData Type Summary:")
    print(f"  - Tables: {schema['summary']['tables']}")
    print(f"  - Downloads: {schema['summary']['downloads']}")
    print(f"  - APIs: {schema['summary']['apis']}")
    print(f"  - Dashboards: {schema['summary']['dashboards']}")
    print(f"\nQuality Metrics:")
    print(f"  - Average Confidence Score: {schema['quality_metrics']['average_confidence']}")
    print(f"  - Extraction Coverage: {schema['quality_metrics']['extraction_coverage']*100:.1f}%")
    print(f"  - High Confidence Sources: {schema['quality_metrics']['sources_by_confidence']['high']}")
    print(f"  - Medium Confidence Sources: {schema['quality_metrics']['sources_by_confidence']['medium']}")
    print(f"  - Low Confidence Sources: {schema['quality_metrics']['sources_by_confidence']['low']}")
    print(f"  - Unavailable Sources: {schema['quality_metrics']['sources_by_confidence']['unavailable']}")
    print(f"\nErrors: {len(schema['errors'])}")
    if schema['errors']:
        print("\nError Details:")
        for error in schema['errors'][:5]:
            print(f"  - {error.get('url', 'Unknown URL')}: {error.get('error', 'Unknown error')}")
    print("\nFull schema saved to: public_data_schema.json")
    print("="*80)
