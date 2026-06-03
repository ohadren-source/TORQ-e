"""
NPI Registry API Integration
Fetches real provider details from https://npiregistry.cms.hhs.gov/api/
Enables dynamic provider type detection and authenticity analysis without hardcoding
"""

import httpx
import json
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# NPI Registry API endpoint
NPI_API_BASE = "https://npiregistry.cms.hhs.gov/api/"

# Cache to avoid repeated API calls (24 hour TTL)
_npi_cache: Dict[str, Tuple[Dict, datetime]] = {}
NPI_CACHE_TTL = timedelta(hours=24)


async def fetch_npi_details(npi: str) -> Optional[Dict]:
    """
    Fetch provider details from NPI Registry API.
    Returns provider record or None if not found / API error.

    Returns dict with:
    - npi: National Provider Identifier
    - name: Provider legal name
    - dba_names: List of "doing business as" names
    - provider_type: Individual (1) or Organization (2)
    - organization_type: Taxonomy code (e.g., 302R00000X for HMO)
    - status: Active / Deactivated
    - address: Primary practice address
    - authorized_official: Contact info
    """

    # Check cache first
    if npi in _npi_cache:
        cached_record, cache_time = _npi_cache[npi]
        if datetime.now() - cache_time < NPI_CACHE_TTL:
            logger.info(f"[NPI Cache Hit] {npi}")
            return cached_record

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Query NPI Registry API
            url = f"{NPI_API_BASE}?number={npi}&format=json"
            logger.info(f"[NPI Lookup] Querying {url}")

            response = await client.get(url)
            response.raise_for_status()

            data = response.json()

            # Parse response
            if data.get("result_count", 0) == 0:
                logger.warning(f"[NPI Not Found] {npi}")
                return None

            result = data["results"][0]

            # Extract provider details
            provider_record = {
                "npi": result.get("number"),
                "name": result.get("basic", {}).get("legal_business_name"),
                "dba_names": result.get("basic", {}).get("doing_business_as_name", []),
                "provider_type": "Organization" if result.get("basic", {}).get("organization_subpart") is False else "Individual",
                "organization_type": result.get("basic", {}).get("organization_name"),
                "status": result.get("basic", {}).get("status"),
                "enumeration_date": result.get("basic", {}).get("enumeration_date"),
                "last_update": result.get("basic", {}).get("last_update_date"),
                "address": {
                    "street": result.get("basic", {}).get("first_line_business_address"),
                    "city": result.get("basic", {}).get("business_address_city_name"),
                    "state": result.get("basic", {}).get("business_address_state_code"),
                    "zip": result.get("basic", {}).get("business_address_postal_code")
                },
                "phone": result.get("basic", {}).get("business_phone_number"),
                "taxonomy": None,
                "raw_result": result  # Keep raw for debugging
            }

            # Extract primary taxonomy (provider type code like 302R00000X)
            taxonomies = result.get("taxonomies", [])
            if taxonomies:
                primary = [t for t in taxonomies if t.get("primary") is True]
                if primary:
                    provider_record["taxonomy"] = {
                        "code": primary[0].get("code"),
                        "desc": primary[0].get("desc"),
                        "state": primary[0].get("state"),
                        "license": primary[0].get("license_number")
                    }

            # Cache the result
            _npi_cache[npi] = (provider_record, datetime.now())

            logger.info(f"[NPI Found] {npi} -> {provider_record['name']}")
            return provider_record

    except httpx.HTTPError as e:
        logger.error(f"[NPI API Error] {npi}: {e}")
        return None
    except Exception as e:
        logger.error(f"[NPI Parse Error] {npi}: {e}")
        return None


def detect_provider_type_from_npi(npi: str, npi_record: Dict) -> str:
    """
    Determine provider type from NPI Registry taxonomy code.

    Returns: 'mco', 'hospital', 'pharmacy', 'lab', 'solo_provider', or 'unknown'
    """

    if not npi_record or not npi_record.get("taxonomy"):
        return "unknown"

    taxonomy_code = npi_record["taxonomy"].get("code", "").upper()
    taxonomy_desc = npi_record["taxonomy"].get("desc", "").lower()

    # Map taxonomy codes to provider types
    # Reference: https://taxonomy.cms.hhs.gov/

    # HMO / Managed Care Organization
    if taxonomy_code.startswith("302R") or "health maintenance organization" in taxonomy_desc:
        return "mco"
    if "managed care" in taxonomy_desc or "insurance" in taxonomy_desc:
        return "mco"

    # Hospital
    if taxonomy_code.startswith("283Q") or "hospital" in taxonomy_desc:
        return "hospital"
    if "medical center" in taxonomy_desc or "health system" in taxonomy_desc:
        return "hospital"

    # Pharmacy
    if taxonomy_code.startswith("3362") or "pharmacy" in taxonomy_desc:
        return "pharmacy"
    if "pharmacist" in taxonomy_desc:
        return "pharmacy"

    # Laboratory
    if taxonomy_code.startswith("332B") or "laboratory" in taxonomy_desc:
        return "lab"
    if "pathology" in taxonomy_desc or "diagnostic" in taxonomy_desc:
        return "lab"

    # Solo Provider (Individual NPI)
    if npi_record.get("provider_type") == "Individual":
        return "solo_provider"

    # Fallback: check if organization or individual
    if npi_record.get("provider_type") == "Organization":
        return "unknown"  # Unknown org type

    return "unknown"


async def get_provider_context(npi: str) -> Dict:
    """
    Comprehensive provider context lookup.
    Fetches NPI Registry record and returns structured context for analysis.

    Returns:
    {
        "npi": str,
        "name": str,
        "provider_type": str,  # mco, hospital, pharmacy, lab, solo_provider
        "status": str,  # Active, Deactivated, etc.
        "npi_record": Dict,  # Full NPI Registry record
        "error": str or None  # Error message if lookup failed
    }
    """

    npi_record = await fetch_npi_details(npi)

    if not npi_record:
        return {
            "npi": npi,
            "name": None,
            "provider_type": "unknown",
            "status": None,
            "npi_record": None,
            "error": f"Provider {npi} not found in NPI Registry or API unavailable"
        }

    provider_type = detect_provider_type_from_npi(npi, npi_record)

    return {
        "npi": npi,
        "name": npi_record["name"],
        "dba_names": npi_record.get("dba_names", []),
        "provider_type": provider_type,
        "status": npi_record.get("status"),
        "npi_record": npi_record,
        "error": None
    }


def clear_npi_cache():
    """Clear the NPI cache (useful for testing or forced refresh)"""
    global _npi_cache
    _npi_cache.clear()
    logger.info("[NPI Cache] Cleared")
