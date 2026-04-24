# TORQ-e: Medicaid Clarity System

**Version:** 1.1.0  
**Status:** ✅ LIVE IN PRODUCTION  
**Deployed:** https://torq-e-production.up.railway.app/

---

## Overview

TORQ-E is a unified identity system that transforms Medicaid enrollment, eligibility verification, and provider management across New York State. Instead of 5+ fragmented systems with zero integration, TORQ-E provides:

- **Card 1 (UMID):** Member Unified Identity & Eligibility ✅ LIVE
- **Card 2 (UPID):** Provider Unified Identity & Claims ✅ LIVE
- **Card 3 (UHWP):** Plan Administrator Network Management 📋 PLANNED
- **Card 4 (USHI):** Government Stakeholder Operations 📋 PLANNED
- **Card 5 (UBADA):** Data Analyst & Fraud Detection 📋 PLANNED

---

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   cd torq-e-code
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Initialize database**
   ```bash
   python -c "from database import init_db; init_db()"
   ```

6. **Start the API**
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`

---

## API Documentation

### Interactive API Docs

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Card 1 (UMID) Endpoints

#### Member Identification
```bash
POST /api/card1/lookup
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-15",
  "ssn": "123456789"
}

Response: {UMID, name, data_source, confidence_score, flags}
```

#### Eligibility Check (Member View)
```bash
POST /api/card1/eligibility/check
Content-Type: application/json

{
  "umid": "UMID-abc12345-6789"
}

Response: {are_you_covered, coverage_until, recertification_date, your_plan, caveats}
```

#### Eligibility Check (Provider/Analyst View)
```bash
POST /api/card1/eligibility/detailed
```

#### Recertification Status
```bash
POST /api/card1/recertification/status
```

#### Document Upload
```bash
POST /api/card1/documents/upload
Content-Type: application/json

{
  "umid": "UMID-abc12345-6789",
  "document_type": "ID",
  "document_filename": "drivers_license.jpg",
  "document_base64": "[base64-encoded image]"
}
```

#### Income Report
```bash
POST /api/card1/income/report
Content-Type: application/json

{
  "umid": "UMID-abc12345-6789",
  "new_income": 2500,
  "income_source": "Wages",
  "effective_date": "2026-04-01"
}

Response: {impact_on_coverage, member_message, recommendation}
```

---

### Card 2 (UPID) Endpoints

#### Provider Identification
```bash
POST /api/card2/lookup
Content-Type: application/json

{
  "npi": "1234567890",
  "first_name": "Jane",
  "last_name": "Smith"
}

Response: {UPID, NPI, specialty, data_source, confidence_score}
```

#### Enrollment Check
```bash
POST /api/card2/enrollment/check
Content-Type: application/json

{
  "upid": "UPID-xyz98765-4321"
}

Response: {FFS status, MCO enrollments, credentials_valid, message}
```

#### Claim Validation
```bash
POST /api/card2/claims/validate
Content-Type: application/json

{
  "member_umid": "UMID-abc12345-6789",
  "provider_upid": "UPID-xyz98765-4321",
  "service_date": "2026-04-15",
  "procedure_code": "99213",
  "diagnosis_code": "J06.9",
  "amount": 150.00
}

Response: {valid, errors, warnings, message}
```

#### Submit Claim
```bash
POST /api/card2/claims/submit
```

#### Check Claim Status
```bash
POST /api/card2/claims/status
Content-Type: application/json

{
  "claim_id": "CLM-abc12345"
}

Response: {status, days_since_submission, expected_payment_date, escalation}
```

#### Fraud Analysis
```bash
POST /api/card2/fraud/analyze
Content-Type: application/json

{
  "claim_data": {...},
  "provider_upid": "UPID-xyz98765-4321",
  "member_umid": "UMID-abc12345-6789"
}

Response: {risk_score, risk_level, signals, recommendation}
```

---

## Architecture

### Data Models

#### Card 1 (UMID)
- **Member:** Core member identity (name, DOB, SSN, UMID)
- **MemberEligibility:** Eligibility status, coverage period, income/assets
- **MemberPlanAssignment:** Plan assignment (FFS or MCO), network status
- **MemberDocument:** Uploaded documents (ID, pay stub, address proof)
- **AuditLog:** Query audit trail

#### Card 2 (UPID)
- **Provider:** Core provider identity (NPI, UPID, credentials)
- **ProviderMCOEnrollment:** Enrollment status in each MCO
- **Claim:** Submitted claims with routing, status, fraud signals
- **ProviderAuditLog:** Query audit trail

### Key Algorithms

#### River Path (Multi-Source Member/Provider Identification)
1. **Attempt 1:** Official state system (highest confidence: 0.95)
2. **Attempt 2:** Backup system (medium confidence: 0.85)
3. **Attempt 3:** Fallback system (lower confidence: 0.70)
4. **Escalate:** If all fail, escalate with caveat

#### Confidence Scoring
Uses signal-processing framework based on ClaudeShannon++ transmission model:
```
CONFIDENCE = [Quality/Quantity] × [(Understanding - Dependence - Misunderstanding - Unknown) / Time]
```

Simpler implementation:
- **High (≥0.85):** Approve automatically
- **Medium (0.60-0.85):** Manual review recommended
- **Low (<0.60):** Escalate to supervisor/caseworker

#### Intelligent Claim Routing
Routes claims to correct MCO/FFS portal with validations:
1. Member eligibility on service date
2. Required fields present
3. Valid procedure/diagnosis codes
4. Amount reasonableness check
5. Prior authorization verification

#### Fraud Detection
Real-time pattern detection for:
- Provider billing anomalies (concentration, amount variance, frequency)
- Member utilization anomalies (multiple providers/day, high frequency)
- Known fraud database lookup

---

## Project Structure

```
torq-e-code/
├── main.py                     # FastAPI application entry point
├── config.py                   # Configuration settings
├── models.py                   # SQLAlchemy ORM models
├── database.py                 # Database initialization
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── README.md                  # This file
│
├── card_1_umid/               # Card 1: Member Eligibility
│   ├── __init__.py
│   ├── river_path.py          # Multi-source member lookup
│   ├── eligibility.py         # Eligibility determination logic
│   ├── confidence.py          # Signal-based confidence scoring
│   ├── schemas.py             # Request/response models
│   └── routes.py              # API endpoints
│
└── card_2_upid/               # Card 2: Provider System
    ├── __init__.py
    ├── provider_lookup.py     # Multi-source provider lookup
    ├── claims_routing.py      # Intelligent claim routing & monitoring
    ├── fraud_detection.py     # Real-time fraud signal analysis
    ├── schemas.py             # Request/response models
    └── routes.py              # API endpoints
```

---

## Development Guide

### Adding a New Endpoint

1. **Create schema** in `card_X_umid/schemas.py` or `card_X_upid/schemas.py`
2. **Add business logic** in appropriate module
3. **Add route** in `routes.py`
4. **Test** with curl or Swagger UI

### Running Tests

```bash
# (Tests coming soon)
pytest
```

### Database Migrations

Currently using SQLAlchemy auto-migration. For production, implement Alembic:
```bash
alembic init migrations
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

---

## Production Deployment

### Prerequisites for Production

1. **PostgreSQL Server**
   - SSL/TLS enabled
   - Backups configured
   - Connection pooling (pgBouncer)

2. **API Server**
   - Gunicorn WSGI server (not uvicorn development)
   - Nginx reverse proxy
   - SSL/TLS certificates
   - Rate limiting

3. **Monitoring**
   - Application logging (ELK stack or CloudWatch)
   - Database monitoring
   - API health checks

4. **Data Protection**
   - Encryption at rest (database-level)
   - Encryption in transit (TLS 1.3+)
   - PII masking in logs
   - Audit logging for all queries

### Production Checklist

- [ ] Update `DATABASE_URL` to production database
- [ ] Set `DEBUG=false` in config
- [ ] Configure SSL certificates
- [ ] Set up monitoring and alerting
- [ ] Enable rate limiting
- [ ] Configure CORS appropriately
- [ ] Set up backup strategy
- [ ] Test failover procedures

---

## Integration with External Systems

### State Medicaid API
Update `settings.state_medicaid_api_url` in config.py to connect to official NY Medicaid systems.

### MCO Systems
Card 2 aggregates enrollments from MCO panel managers. Configure MCO endpoints in production.

### NPI Database
Fallback lookup uses NPI registry. No credentials required.

---

## Known Limitations (Current)

- River Path uses simulated data sources (real APIs not yet integrated)
- Fraud detection uses simulated patterns (real claim history not yet available)
- Document OCR not implemented (placeholder)
- No multi-user authentication yet (assuming secure API gateway)

---

## Roadmap

### Card 1 & 2 (Current)
- ✅ Member identity and eligibility
- ✅ Provider enrollment verification
- ✅ Claim submission and routing
- ✅ Real-time fraud signal detection
- 🔨 Integration with real state APIs
- 🔨 Document OCR and verification

### Card 3 (Plan Administrator)
- 📋 Network management
- 📋 Plan parameter configuration
- 📋 Network adequacy monitoring

### Card 4 (Government Stakeholder)
- 📋 Program oversight dashboard
- 📋 Regulatory compliance monitoring
- 📋 Performance metrics

### Card 5 (Data Analyst/Fraud Investigator)
- 📋 Advanced fraud investigation tools
- 📋 Trend analysis and reporting
- 📋 Case management integration

---

## Support & Contributions

For questions or issues:
1. Check this README
2. Review API docs at `/docs`
3. Consult project documentation (TORQ_E_ARCHITECTURAL_PROTOCOL.md)

---

## License

Confidential - NY Department of Health

---

**Last Updated:** April 24, 2026
