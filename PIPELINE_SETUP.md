# TORQ-E Data Ingestion Pipeline - Setup & Usage Guide

## Overview

The TORQ-E Data Ingestion Pipeline automatically extracts public Medicaid plan data from multiple sources, transforms it into a unified schema, validates quality, and loads it into the Card 3 database.

**Daily process (2 AM ET):**
1. Extract from CMS API, eMedNY portal, state APIs
2. Transform to TORQ-E format
3. Validate completeness and accuracy
4. Deduplicate
5. Load into database
6. Verify success
7. Generate audit trail

**Result:** Card 3 marketplace always has current, verified Medicaid plan data.

---

## Prerequisites

### Required
- Node.js >= 16.0.0
- PostgreSQL database
- Internet access (for API calls and web scraping)

### Recommended
- Docker (for running PostgreSQL locally)
- `psql` command-line tool (for database administration)

---

## Installation

### 1. Install Node.js Dependencies

```bash
npm install
# Or use the provided package.json
npm install --from-file pipeline-package.json
```

### 2. Set Up PostgreSQL Database

#### Option A: Local PostgreSQL

```bash
# Create database and user
createdb torq_e_card3
createuser torq_e_user
psql torq_e_card3
  CREATE ROLE torq_e_user WITH LOGIN PASSWORD 'secure_password';
  GRANT ALL PRIVILEGES ON DATABASE torq_e_card3 TO torq_e_user;
```

#### Option B: Docker

```bash
docker run -d \
  --name torq-e-postgres \
  -e POSTGRES_USER=torq_e_user \
  -e POSTGRES_PASSWORD=secure_password \
  -e POSTGRES_DB=torq_e_card3 \
  -p 5432:5432 \
  postgres:15
```

### 3. Create Database Schema

```bash
# Run the Card 3 database schema (from card3-database-schema.sql)
psql -U torq_e_user -d torq_e_card3 -f card3-database-schema.sql
```

### 4. Create Audit Log Table

```bash
psql -U torq_e_user -d torq_e_card3 << 'EOF'

-- Immutable append-only audit log
CREATE TABLE IF NOT EXISTS data_ingestion_audit_log (
  id UUID PRIMARY KEY,
  timestamp TIMESTAMP NOT NULL,
  action VARCHAR(50) NOT NULL,
  entry_json JSONB NOT NULL,
  hash VARCHAR(64) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  
  -- Immutability enforcement
  CONSTRAINT audit_log_immutable CHECK (true)
);

-- Prevent updates and deletes
CREATE OR REPLACE FUNCTION prevent_audit_log_modification()
RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'Audit log is immutable - no modifications allowed';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_log_no_update
BEFORE UPDATE ON data_ingestion_audit_log
FOR EACH ROW EXECUTE FUNCTION prevent_audit_log_modification();

CREATE TRIGGER audit_log_no_delete
BEFORE DELETE ON data_ingestion_audit_log
FOR EACH ROW EXECUTE FUNCTION prevent_audit_log_modification();

-- Index for performance
CREATE INDEX idx_audit_log_timestamp ON data_ingestion_audit_log(timestamp DESC);
CREATE INDEX idx_audit_log_action ON data_ingestion_audit_log(action);

EOF
```

### 5. Get CMS API Key

1. Visit https://api.cms.gov/
2. Sign up for free API access
3. Get your API key
4. Save for use in .env file

---

## Configuration

### Create `.env` file

```bash
# Database connection
DATABASE_URL=postgresql://torq_e_user:secure_password@localhost:5432/torq_e_card3

# CMS API
CMS_API_KEY=your_cms_api_key_here

# Environment
NODE_ENV=production

# Schedule time (cron format, default: 2 AM daily)
SCHEDULE_TIME=0 2 * * *
```

### Cron Format

```
Minute (0-59)  Hour (0-23)  Day (1-31)  Month (1-12)  Day of Week (0-6)

0 2 * * *  = Every day at 2:00 AM
0 0 * * 0  = Every Sunday at midnight
30 14 * * * = Every day at 2:30 PM
0 */6 * * * = Every 6 hours
```

---

## Usage

### Run Pipeline Once

```bash
npm start
# or
node pipeline-main.js --run-once
```

**Output:**
```
TORQ-E Data Ingestion Pipeline
Started: 2026-04-25T02:00:00Z
Environment: production

[Config] Configuration loaded
[Database] Connecting to PostgreSQL...
[Database] Connected successfully

[Pipeline] STAGE 1: EXTRACT
[Extract] Pulling from CMS API...
[Extract] CMS API: 150 programs
[Extract] Scraping eMedNY portal...
[Extract] eMedNY: 245 programs

[Pipeline] STAGE 2: TRANSFORM
[Transform] Processing CMS_API...
[Transform] CMS_API: Transformed 150 programs

[Pipeline] STAGE 3: VALIDATE
[Validate] Validating 395 programs...
[Validate] PASSED (99.7% valid records)

[Pipeline] STAGE 4: DEDUPLICATE
[Deduplicate] Removed 45 duplicates, 350 unique programs

[Pipeline] STAGE 5: LOAD
[Load] Loading 350 programs into database...
[Load] Inserted: 125, Updated: 225, Errors: 0

[Pipeline] STAGE 6: VERIFY
[Verify] Database contains: 1,250 total, 1,100 active

Pipeline Execution Summary:
  Status: ✓ SUCCESS
  Duration: 45.23s
  Programs Loaded: 350 (Inserted: 125, Updated: 225)
  Errors: 0
```

### Schedule Daily Execution

```bash
npm run schedule
# or
node pipeline-main.js --schedule
```

**Output:**
```
[Main] Starting pipeline scheduler...
[Pipeline] Scheduling daily execution at 0 2 * * *...
[Pipeline] Daily schedule active
[Main] Pipeline will run daily at: 0 2 * * *
[Main] (Schedule format: minute hour day month dayofweek)
[Main] Scheduler is now running. Press Ctrl+C to stop.
```

The pipeline will then run automatically every day at 2 AM ET.

### Health Check

```bash
npm run health
# or
node pipeline-main.js --health-check
```

**Output:**
```
[Health] Running system health checks...

[Health] Checking database...
[Health] Database: ✓ OK

[Health] Checking audit log...
[Health] Audit log: ✓ OK
[Health]   Total entries: 1,245
[Health]   Valid entries: 1,245
[Health]   Invalid entries: 0

[Health] Checking CMS API access...
[Health] CMS API: ✓ Key configured

[Health] Health check complete
```

### Generate Compliance Report

```bash
npm run report
# or
node pipeline-main.js --audit-report
```

**Output:**
```
[Report] Generating compliance report...

[Report] Period: 2026-03-26 to 2026-04-25

[Report] Activity Summary:
  DATA_EXTRACTED: 30 events (30 days)
  DATA_TRANSFORMED: 30 events (30 days)
  DATA_VALIDATED: 30 events (30 days)
  PROGRAMS_LOADED: 30 events (30 days)
  PIPELINE_COMPLETED: 30 events (30 days)

[Report] Audit Trail Integrity:
  Total entries: 15,042
  Valid entries: 15,042
  Invalid entries: 0
  Integrity status: ✓ OK

[Report] Report complete
```

---

## File Organization

```
pipeline/
├── cms-api-extractor.js         # Extract from CMS API
├── emedny-scraper.js            # Scrape eMedNY portal
├── data-transformer.js          # Transform to TORQ-E schema
├── program-validator.js         # Validate data quality
├── postgres-loader.js           # Load into database
├── pipeline-orchestrator.js     # Coordinate ETL stages
├── audit-logger.js              # Immutable audit logging
├── pipeline-main.js             # Entry point
├── pipeline-package.json        # Node.js dependencies
├── .env                         # Configuration (create manually)
└── PIPELINE_SETUP.md            # This file
```

---

## Data Quality

### Validation Rules

Every program must pass:
- **Required fields:** name, state, type, eligibility_criteria, benefits, cost_sharing, network_type, coverage_start_date, status
- **Data types:** All fields match expected types (string, number, boolean, object, date)
- **Enum values:** type, network_type, status match allowed values
- **Business logic:** age_min < age_max, cost values >= 0, dates are valid

### Quality Target

- **Completeness:** 99.5% of required fields populated
- **Accuracy:** 99% of values match source data
- **Validity:** 100% pass validation rules

If completeness drops below 99.5%, pipeline warns but continues. This ensures bad data doesn't block the system.

---

## Monitoring

### View Audit Trail

```bash
psql -U torq_e_user -d torq_e_card3 << 'EOF'

-- Last 10 events
SELECT timestamp, action, entry_json 
FROM data_ingestion_audit_log 
ORDER BY timestamp DESC 
LIMIT 10;

-- Events by action
SELECT action, COUNT(*) as count 
FROM data_ingestion_audit_log 
GROUP BY action 
ORDER BY count DESC;

-- Events in last 24 hours
SELECT timestamp, action, entry_json 
FROM data_ingestion_audit_log 
WHERE timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;

EOF
```

### Monitor Program Count

```bash
psql -U torq_e_user -d torq_e_card3 << 'EOF'

-- Total programs
SELECT COUNT(*) as total FROM programs;

-- Programs by status
SELECT status, COUNT(*) as count 
FROM programs 
GROUP BY status;

-- Programs by state
SELECT state, COUNT(*) as count 
FROM programs 
GROUP BY state 
ORDER BY count DESC;

EOF
```

---

## Troubleshooting

### CMS API Connection Fails

**Problem:** "CMS API extraction failed"

**Solution:**
1. Verify CMS_API_KEY is set: `echo $CMS_API_KEY`
2. Check API key is valid at https://api.cms.gov/
3. Verify internet connection
4. Check firewall allows outbound HTTPS

### eMedNY Scraper Fails

**Problem:** "eMedNY scrape failed"

**Solution:**
1. Check eMedNY website is accessible: `curl https://www.emedny.org/plans`
2. Verify Puppeteer is installed: `npm ls puppeteer`
3. Check system has Chrome/Chromium for Puppeteer
4. Increase timeout in config if eMedNY is slow

### Database Connection Fails

**Problem:** "Database connection failed"

**Solution:**
1. Verify PostgreSQL is running: `pg_isready`
2. Check DATABASE_URL in .env
3. Test connection: `psql $DATABASE_URL`
4. Verify user has permissions: `psql -U torq_e_user -d torq_e_card3 -c "SELECT 1"`

### Validation Fails (>10% Invalid)

**Problem:** "Validation below 99.5% threshold"

**Solution:**
1. Check source data for quality issues
2. Review validation errors in audit log
3. Adjust transformer rules if needed
4. Report specific validation issues to governance team

### Audit Log Integrity Issues

**Problem:** "Invalid entries: X"

**Solution:**
1. This indicates potential tampering
2. Stop pipeline immediately
3. Generate compliance report
4. Contact compliance/security team
5. Investigate database access logs

---

## Production Deployment

### Running as Background Service

#### Systemd (Linux)

```ini
# /etc/systemd/system/torq-e-pipeline.service

[Unit]
Description=TORQ-E Data Ingestion Pipeline
After=network.target postgresql.service

[Service]
Type=simple
User=torq-e
WorkingDirectory=/opt/torq-e-pipeline
EnvironmentFile=/opt/torq-e-pipeline/.env
ExecStart=/usr/bin/node pipeline-main.js --schedule
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable torq-e-pipeline
sudo systemctl start torq-e-pipeline
sudo systemctl status torq-e-pipeline
```

#### Docker

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY . .
RUN npm install

ENV NODE_ENV=production

CMD ["node", "pipeline-main.js", "--schedule"]
```

```bash
docker build -t torq-e-pipeline .
docker run -d \
  --name torq-e-pipeline \
  --env-file .env \
  --link torq-e-postgres:postgres \
  torq-e-pipeline
```

### Logging

Capture logs to file:

```bash
node pipeline-main.js --schedule >> /var/log/torq-e-pipeline.log 2>&1 &
```

### Monitoring & Alerts

Set up monitoring for:
- Pipeline success/failure
- Validation failures
- Audit log integrity
- Database connectivity
- API access

Example monitoring script:

```bash
#!/bin/bash
# Check if pipeline ran in last 24 hours

LAST_RUN=$(psql -U torq_e_user -d torq_e_card3 -t -c \
  "SELECT MAX(timestamp) FROM data_ingestion_audit_log WHERE action = 'PIPELINE_COMPLETED'")

if [ -z "$LAST_RUN" ]; then
  echo "CRITICAL: Pipeline has never run"
  # Send alert
fi

HOURS_AGO=$(echo "SELECT EXTRACT(EPOCH FROM (NOW() - '$LAST_RUN'::timestamp)) / 3600" | psql -t)

if [ "$HOURS_AGO" -gt 26 ]; then
  echo "CRITICAL: Pipeline last ran $HOURS_AGO hours ago"
  # Send alert
fi
```

---

## Support & Documentation

- **DR (Design Repository):** `/TORQ-E_Data_Ingestion_Architecture_DR.md`
- **AN (Architecture for Audience):** `/TORQ-E_Data_Ingestion_Architecture_AN.md`
- **Implementation DR:** `/TORQ-E_Data_Ingestion_Implementation_DR.md`
- **Implementation AN:** `/TORQ-E_Data_Ingestion_Implementation_AN.md`

---

## Success Indicators

Pipeline is working correctly when:

✓ Runs daily without errors
✓ Validation rate > 99.5%
✓ All audit log entries have valid hashes
✓ Database contains >1,000 active programs
✓ No CMS API or eMedNY scraper failures
✓ Compliance report shows all events logged
✓ Card 3 marketplace loads current plans
✓ Members can search and enroll in plans

---

End of Pipeline Setup & Usage Guide
