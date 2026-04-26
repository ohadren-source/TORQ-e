# Using Extracted Data in Card Query Engines
## Practical Implementation Guide for Cards 1-3

---

## Quick Start: What's Available Now

After `data_crawler.py` runs, your `public_data_schema` contains:

```python
{
  "discovered_data": [
    {
      "type": "table",
      "url": "https://emedny.org/...",
      "format": "HTML",
      "description": "Provider enrollment table",
      "extracted_data": {
        "content": [
          {"provider_id": "123456", "name": "Dr. Smith", "specialty": "Cardiology"},
          {"provider_id": "789012", "name": "Dr. Jones", "specialty": "Pediatrics"},
          ...
        ]
      },
      "confidence": 0.85
    },
    ...
  ]
}
```

---

## How to Search the Schema

### Pattern 1: Filter by Source Type

```python
def find_sources_by_type(public_data_schema, source_type):
    """Find all sources of a specific type"""
    return [
        d for d in public_data_schema.get("discovered_data", [])
        if d.get("type") == source_type
    ]

# Usage
tables = find_sources_by_type(schema, "table")
downloads = find_sources_by_type(schema, "download")
apis = find_sources_by_type(schema, "api")
```

### Pattern 2: Filter by Confidence Level

```python
def find_sources_by_confidence(public_data_schema, min_confidence=0.75):
    """Find sources meeting confidence threshold"""
    return [
        d for d in public_data_schema.get("discovered_data", [])
        if d.get("confidence", 0.0) >= min_confidence
    ]

# Usage
high_confidence = find_sources_by_confidence(schema, 0.85)  # Official sources only
```

### Pattern 3: Filter by URL Pattern

```python
def find_sources_by_domain(public_data_schema, domain):
    """Find sources from a specific domain"""
    return [
        d for d in public_data_schema.get("discovered_data", [])
        if domain in d.get("url", "")
    ]

# Usage
emedny_sources = find_sources_by_domain(schema, "emedny.org")
omig_sources = find_sources_by_domain(schema, "omig.ny.gov")
```

### Pattern 4: Extract Data from Specific Source

```python
def get_extracted_data(source_entry):
    """Get actual content from a discovered source"""
    return source_entry.get("extracted_data", {}).get("raw_data", {})

# Usage
for source in tables:
    data = get_extracted_data(source)
    print(f"From {source['url']}: {len(data)} records")
```

---

## Card 1 (UMID) - Member Identification

### Current Mock Implementation
```python
# card_1_umid/river_path.py
def identify_member(member_id, public_data_schema=None):
    # Current: hardcoded mock data
    return {
        "member_id": member_id,
        "confidence": 0.95,  # Fake
        "source": "eMedNY"   # Hardcoded
    }
```

### Updated with Real Data

```python
def identify_member(member_id, public_data_schema=None):
    """
    Identify member using real data from eMedNY repository.
    Uses multi-source consensus for confidence scoring.
    """
    if not public_data_schema:
        return {"confidence": 0.0, "error": "No public data available"}
    
    # Find all member data sources
    member_sources = [
        d for d in public_data_schema.get("discovered_data", [])
        if "member" in d.get("description", "").lower()
        and d.get("confidence", 0.0) >= 0.75
    ]
    
    matches = []
    
    for source in member_sources:
        extracted = source.get("extracted_data", {})
        source_data = extracted.get("raw_data", {})
        
        # Search for member ID in this source
        if isinstance(source_data, list):
            for record in source_data:
                if record.get("member_id") == member_id:
                    matches.append({
                        "source_url": source["url"],
                        "source_confidence": source["confidence"],
                        "record": record
                    })
        elif isinstance(source_data, dict):
            # Handle different data structures
            if source_data.get("member_id") == member_id:
                matches.append({
                    "source_url": source["url"],
                    "source_confidence": source["confidence"],
                    "record": source_data
                })
    
    # Calculate consensus confidence
    if not matches:
        return {"confidence": 0.0, "error": "Member not found"}
    
    source_confidences = [m["source_confidence"] for m in matches]
    consensus_confidence = sum(source_confidences) / len(source_confidences)
    
    return {
        "member_id": member_id,
        "matches": matches,
        "consensus_confidence": consensus_confidence,
        "source_count": len(matches),
        "sources": [m["source_url"] for m in matches]
    }
```

### Usage in Routes

```python
@router.post("/umid/lookup")
async def member_lookup(
    member_id: str = Body(...),
    public_data_schema: Optional[Dict] = Depends(get_public_data_schema)
):
    result = identify_member(member_id, public_data_schema)
    
    if result.get("confidence", 0) == 0:
        return {
            "status": "not_found",
            "message": result.get("error")
        }
    
    return {
        "status": "found",
        "member_id": member_id,
        "confidence": result["consensus_confidence"],
        "sources_checked": result["source_count"],
        "details": result["matches"][0]["record"] if result["matches"] else None
    }
```

---

## Card 2 (UPID) - Provider Identification

### Updated with Real Data

```python
def identify_provider(provider_id, public_data_schema=None):
    """
    Identify provider using real enrollment data from eMedNY.
    Cross-references with MCO directory for verification.
    """
    if not public_data_schema:
        return {"confidence": 0.0, "error": "No public data available"}
    
    # Find provider enrollment sources (highest confidence)
    provider_sources = [
        d for d in public_data_schema.get("discovered_data", [])
        if "provider" in d.get("description", "").lower()
        and "enrollment" in d.get("description", "").lower()
        and d.get("confidence", 0.0) >= 0.80
    ]
    
    matches = []
    
    for source in provider_sources:
        extracted = source.get("extracted_data", {})
        source_data = extracted.get("raw_data", {})
        
        # Search in this source
        if isinstance(source_data, list):
            for record in source_data:
                if record.get("provider_id") == provider_id or record.get("npi") == provider_id:
                    matches.append({
                        "source_url": source["url"],
                        "source_confidence": source["confidence"],
                        "record": record,
                        "source_type": source["type"]
                    })
    
    if not matches:
        return {"confidence": 0.0, "error": "Provider not found"}
    
    # Provider match confidence = source confidence
    # (single source is authoritative for provider enrollment)
    primary_match = matches[0]
    
    return {
        "provider_id": provider_id,
        "confidence": primary_match["source_confidence"],
        "details": primary_match["record"],
        "source_url": primary_match["source_url"],
        "source_type": primary_match["source_type"],
        "verified_sources": len(matches)
    }
```

### Validate Claims Against Provider Data

```python
def validate_claim_provider(provider_id, claim, public_data_schema=None):
    """
    Validate provider is enrolled and authorized for claim service.
    Uses extracted provider enrollment data.
    """
    provider_info = identify_provider(provider_id, public_data_schema)
    
    if provider_info.get("confidence", 0) < 0.75:
        return {
            "valid": False,
            "reason": "Provider not verified in enrollment data",
            "confidence": provider_info.get("confidence", 0)
        }
    
    # Check if provider is active
    details = provider_info.get("details", {})
    status = details.get("status", "")
    
    if status != "Active":
        return {
            "valid": False,
            "reason": f"Provider status: {status}",
            "confidence": provider_info["confidence"]
        }
    
    # Check specialty matches claim type (future enhancement)
    # specialty = details.get("specialty", "")
    
    return {
        "valid": True,
        "confidence": provider_info["confidence"],
        "provider_details": details
    }
```

---

## Card 3 (WHUP) - Programs & Plans

### Updated Plan Lookup with Real Data

```python
def find_plans_by_location(zipcode, public_data_schema=None):
    """
    Find available MCO plans for a zipcode.
    Uses extracted MCO Directory data from health.ny.gov.
    """
    if not public_data_schema:
        return {"plans": [], "confidence": 0.0}
    
    # Find MCO plan data sources
    plan_sources = [
        d for d in public_data_schema.get("discovered_data", [])
        if "plan" in d.get("description", "").lower()
        and d.get("confidence", 0.0) >= 0.75
    ]
    
    available_plans = []
    source_confidences = []
    
    for source in plan_sources:
        extracted = source.get("extracted_data", {})
        source_data = extracted.get("raw_data", {})
        
        if isinstance(source_data, list):
            for plan_record in source_data:
                # Check if plan serves this zipcode
                plan_zips = plan_record.get("service_areas", [])
                
                if zipcode in plan_zips or not plan_zips:  # Empty = all areas
                    available_plans.append({
                        "plan_name": plan_record.get("name", ""),
                        "mco": plan_record.get("mco_name", ""),
                        "plan_type": plan_record.get("type", "HMO"),
                        "source_url": source["url"],
                        "source_confidence": source["confidence"]
                    })
                    source_confidences.append(source["confidence"])
    
    # Calculate average confidence across plan sources
    avg_confidence = (
        sum(source_confidences) / len(source_confidences)
        if source_confidences else 0.0
    )
    
    return {
        "zipcode": zipcode,
        "plans": available_plans,
        "plan_count": len(available_plans),
        "confidence": avg_confidence
    }
```

### Plan Comparison with Real Data

```python
def compare_plans(plan_ids, public_data_schema=None):
    """
    Compare multiple MCO plans side-by-side.
    Extracts real features from discovered plan data.
    """
    if not public_data_schema:
        return {"error": "No public data available"}
    
    comparison = []
    
    for plan_id in plan_ids:
        # Find this plan in discovered sources
        plan_data = find_plan_by_id(plan_id, public_data_schema)
        
        if plan_data:
            comparison.append({
                "plan_id": plan_id,
                "name": plan_data.get("name", ""),
                "mco": plan_data.get("mco", ""),
                "type": plan_data.get("type", ""),
                "networks": plan_data.get("networks", []),
                "formulary": plan_data.get("formulary_url", ""),
                "enrollment_status": plan_data.get("enrollment_status", ""),
                "source_confidence": plan_data.get("confidence", 0.75)
            })
    
    return {
        "comparison": comparison,
        "count": len(comparison),
        "average_confidence": sum(p["source_confidence"] for p in comparison) / len(comparison) if comparison else 0
    }
```

---

## Card 4 (USHI) - Governance Queries

### Detect Fraud Signals Using Real Data

```python
def detect_fraud_signals_real(
    entity_type: str,
    threshold_sigma: float,
    public_data_schema=None
):
    """
    Detect statistical anomalies from real OMIG/fraud data.
    Uses extracted data from OMIG fraud investigation repository.
    """
    if not public_data_schema:
        return {"signals": [], "confidence": 0.0}
    
    # Find fraud-related sources (high confidence)
    fraud_sources = [
        d for d in public_data_schema.get("discovered_data", [])
        if "fraud" in d.get("description", "").lower()
        or "omig" in d.get("url", "").lower()
        and d.get("confidence", 0.0) >= 0.85
    ]
    
    signals = []
    
    for source in fraud_sources:
        extracted = source.get("extracted_data", {})
        source_data = extracted.get("raw_data", {})
        
        # Analyze data for anomalies
        if isinstance(source_data, list):
            # Statistical analysis on entity metrics
            signals.extend(
                analyze_anomalies(source_data, entity_type, threshold_sigma)
            )
    
    return {
        "entity_type": entity_type,
        "signals_detected": len(signals),
        "signals": signals,
        "average_confidence": 0.85,  # OMIG is authoritative
        "recommendation": "Escalate to Card 5" if signals else None
    }
```

---

## Pattern: Search Across Sources

### Generic Multi-Source Search

```python
def search_across_sources(
    public_data_schema,
    search_key: str,
    search_value: str,
    min_confidence: float = 0.75
):
    """
    Search for a value across all available sources.
    Returns all matches with source information.
    """
    results = []
    
    for source in public_data_schema.get("discovered_data", []):
        if source.get("confidence", 0) < min_confidence:
            continue  # Skip low-confidence sources
        
        extracted = source.get("extracted_data", {})
        source_data = extracted.get("raw_data", {})
        
        # Handle different data structures
        matches = find_in_data(source_data, search_key, search_value)
        
        if matches:
            results.append({
                "source_url": source["url"],
                "source_type": source["type"],
                "source_confidence": source["confidence"],
                "matches": matches,
                "match_count": len(matches)
            })
    
    return {
        "search_key": search_key,
        "search_value": search_value,
        "total_matches": sum(r["match_count"] for r in results),
        "sources_with_matches": len(results),
        "results": results
    }
```

---

## Best Practices

### 1. Always Check Confidence
```python
if source["confidence"] >= 0.85:
    # Use for high-stakes decisions (enrollment, claims approval)
    pass
elif source["confidence"] >= 0.70:
    # Use for supporting evidence, cross-reference
    pass
else:
    # Don't use; archive status or unavailable data
    pass
```

### 2. Handle Missing Extracted Data
```python
extracted = source.get("extracted_data", {})
if not extracted:
    # Fall back to metadata or skip
    logger.warning(f"No extracted data for {source['url']}")
    continue
```

### 3. Cross-Reference Multiple Sources
```python
# Member lookup: find in 2+ sources for high confidence
if len(matches) >= 2:
    confidence = 0.95  # Multi-source verification
elif len(matches) == 1:
    confidence = matches[0]["source_confidence"]  # Single source
else:
    confidence = 0.0  # Not found
```

### 4. Log Source for Audit Trail
```python
# Always record which source provided the data
response["data_source"] = {
    "url": source["url"],
    "type": source["type"],
    "confidence": source["confidence"],
    "extracted_at": source.get("discovered_at")
}
```

---

## Testing Your Integration

### Test 1: Verify Schema Structure
```python
import json

with open("public_data_schema.json") as f:
    schema = json.load(f)

# Check for extracted data
extracted_count = len([
    d for d in schema["discovered_data"]
    if "extracted_data" in d
])

print(f"Sources with extracted data: {extracted_count}")
print(f"Average confidence: {schema['average_confidence_score']}")
```

### Test 2: Test Lookup Functions
```python
# Test member lookup
from card_1_umid.river_path import identify_member

result = identify_member("NY123456", schema)
print(f"Found: {result['confidence']}")

# Test provider lookup
from card_2_upid.provider_lookup import identify_provider

result = identify_provider("NPI123456", schema)
print(f"Provider confidence: {result['confidence']}")
```

### Test 3: Test Plan Lookup
```python
from card_3_uhwp.plans import find_plans_by_location

plans = find_plans_by_location("11201", schema)
print(f"Plans in Brooklyn: {plans['plan_count']}")
print(f"Confidence: {plans['confidence']}")
```

---

## Summary

Your extracted data schema is now a **real data backend** for TORQ-e. Each Card's query engine can:

✅ Search for actual member/provider/plan data  
✅ Cross-reference across multiple government repositories  
✅ Score confidence based on real source quality  
✅ Return audit trails showing data sources  
✅ Combine axiomatic knowledge with specific real data  

Ready for production testing on Railway.
