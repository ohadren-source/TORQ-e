"""
DATA CRAWLER SERVICE - TORQ-E
Playwright-based web crawler to discover and map available data from public Medicaid repositories
NO DUMMY DATA - ONLY REAL PUBLIC REPOSITORY DATA

Unified Substrate Repositories (for all Cards 1-5):
- Card 1 & 2 (Member & Provider): eMedNY, Health.NY.gov Medicaid Program
- Card 3 (MCO Plans): MCO Directory, Health Data NY, Managed Care Reports
- Card 4 & 5 (Governance & inauthenticity): OHIP, OMIG, ITS, Medicaid Reference

Integration: Uses reading_engine.py to extract data from discovered sources in multiple formats
- PDF: research papers, regulatory docs, credentials
- Web Pages: general content, watchdog sites, registries
- Dynamic Content: JavaScript-heavy dashboards, interactive tools
- Academic Sources: PubMed, arXiv for research verification
- GitHub: provider background, code transparency, documentation
"""

from playwright.sync_api import sync_playwright
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from urllib.parse import urljoin, urlparse
import logging
import os
import sys

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

    # Card 4 & 5: Government Stakeholder & authenticity investigation
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
        Main entry point: Crawl all base URLs and return data schema
        """
        logger.info("Starting repository crawl...")

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)

            for base_url in BASE_URLS:
                logger.info(f"Crawling: {base_url}")
                try:
                    self._crawl_url(browser, base_url, depth=0)
                except Exception as e:
                    logger.error(f"Failed to crawl {base_url}: {str(e)}")
                    self.errors.append({"url": base_url, "error": str(e)})

            browser.close()

        return self._generate_schema()

    def _crawl_url(self, browser, url: str, depth: int = 0):
        """
        Recursively crawl a URL and discover data
        """
        if depth > MAX_CRAWL_DEPTH:
            return

        if url in self.visited_urls:
            return

        self.visited_urls.add(url)
        logger.info(f"  [Depth {depth}] Analyzing: {url}")

        try:
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Discover data on this page
            self._discover_page_data(page, url)

            # Find links to follow (same domain only)
            domain = urlparse(url).netloc
            links = page.query_selector_all("a[href]")

            for link in links:
                href = link.get_attribute("href")
                if href:
                    absolute_url = urljoin(url, href)
                    link_domain = urlparse(absolute_url).netloc

                    # Only follow links on same domain
                    if link_domain == domain and absolute_url not in self.visited_urls:
                        # Avoid infinite crawling - be selective
                        if self._should_follow_link(absolute_url):
                            self._crawl_url(browser, absolute_url, depth + 1)

            page.close()

        except Exception as e:
            logger.error(f"Error analyzing {url}: {str(e)}")
            self.errors.append({"url": url, "error": str(e)})

    def _discover_page_data(self, page, url: str):
        """
        Analyze a page for available data sources.
        For each discovered source, attempt to extract data using reading_engine.
        """
        # Check for tables
        tables = page.query_selector_all("table")
        if tables:
            for i, table in enumerate(tables):
                table_text = table.text_content()[:200]
                data_entry = {
                    "type": "table",
                    "url": url,
                    "description": f"HTML Table #{i+1}: {table_text}...",
                    "format": "HTML",
                    "discovered_at": datetime.utcnow().isoformat()
                }

                # Extract table content if reading_engine available
                if HAS_READING_ENGINE:
                    extraction = self._extract_source_data(url, "web", parse_type="general")
                    if extraction.get("raw_data"):
                        data_entry["extracted_data"] = extraction.get("raw_data")
                        data_entry["confidence"] = extraction.get("confidence", 0.7)

                self.discovered_data.append(data_entry)
                logger.info(f"    Found table on {url}")

        # Check for download links
        downloads = page.query_selector_all('a[href*=".csv"], a[href*=".xlsx"], a[href*=".xls"], a[href*=".json"], a[href*=".pdf"]')
        for download in downloads:
            href = download.get_attribute("href")
            text = download.text_content().strip()
            if href:
                full_url = urljoin(url, href)
                file_ext = href.split('.')[-1].lower()
                data_entry = {
                    "type": "download",
                    "url": full_url,
                    "description": f"{text} ({file_ext})",
                    "format": file_ext.upper(),
                    "page_url": url,
                    "discovered_at": datetime.utcnow().isoformat()
                }

                # Extract data from PDFs using reading_engine
                if HAS_READING_ENGINE and file_ext == "pdf":
                    try:
                        # Download PDF temporarily
                        pdf_path = self._download_file(full_url, file_ext)
                        if pdf_path:
                            extraction = read_pdf(pdf_path)
                            data_entry["extracted_data"] = extraction.get("raw_data")
                            data_entry["confidence"] = extraction.get("confidence", 0.8)
                            # Clean up temp file
                            try:
                                os.remove(pdf_path)
                            except:
                                pass
                    except Exception as e:
                        logger.warning(f"PDF extraction failed for {full_url}: {e}")

                self.discovered_data.append(data_entry)
                logger.info(f"    Found downloadable data: {text}")

        # Check for API endpoints (look for /api/ in links)
        api_links = page.query_selector_all('a[href*="/api/"]')
        for api_link in api_links:
            href = api_link.get_attribute("href")
            text = api_link.text_content().strip()
            if href:
                api_url = urljoin(url, href)
                data_entry = {
                    "type": "api",
                    "url": api_url,
                    "description": f"API endpoint: {text}",
                    "format": "JSON/API",
                    "page_url": url,
                    "discovered_at": datetime.utcnow().isoformat()
                }

                # Attempt to fetch API endpoint
                if HAS_READING_ENGINE:
                    extraction = self._extract_source_data(api_url, "web", parse_type="general")
                    if extraction.get("raw_data"):
                        data_entry["extracted_data"] = extraction.get("raw_data")
                        data_entry["confidence"] = extraction.get("confidence", 0.85)

                self.discovered_data.append(data_entry)
                logger.info(f"    Found API endpoint: {text}")

        # Check for data dashboards (look for /dashboard, /reports, /data)
        page_text = page.text_content().lower()
        page_title = page.title().lower()

        if any(keyword in page_text or keyword in page_title for keyword in ["dashboard", "report", "statistics", "metrics", "data view"]):
            data_entry = {
                "type": "dashboard",
                "url": url,
                "description": f"Data dashboard/report: {page.title()}",
                "format": "Interactive",
                "discovered_at": datetime.utcnow().isoformat()
            }

            # Extract dashboard content using dynamic reader
            if HAS_READING_ENGINE:
                extraction = read_dynamic_page(url, selector="body")
                if extraction.get("raw_data"):
                    data_entry["extracted_data"] = extraction.get("raw_data")
                    data_entry["confidence"] = extraction.get("confidence", 0.75)

            self.discovered_data.append(data_entry)
            logger.info(f"    Found dashboard: {page.title()}")

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
            "omig.ny.gov": 0.90,         # authenticity investigation authority
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
    FastAPI endpoint to trigger data discovery
    Returns schema of available data from public repositories
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
    print(f"  - Low Confidence Sources: {schema['quality_metrics']