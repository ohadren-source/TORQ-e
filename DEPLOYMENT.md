# 🚀 DEPLOYMENT GUIDE: Local & Railway

TORQ-e runs on FastAPI + PostgreSQL. Deploy locally for development or on Railway for production.

---

## OPTION 1: RAILWAY PRODUCTION (RECOMMENDED)

TORQ-e is already deployed on Railway. This is the fastest and simplest approach.

### Access Production

**Live URL:**
```
https://torq-e-production.up.railway.app/
```

### Required Environment Variables

Set these in Railway Variables panel:

```
DATABASE_URL=postgresql+psycopg://user:password@host:5432/torq_e
ANTHROPIC_API_KEY=sk-ant-xxxxx... (your Claude API key)
```

**How to get ANTHROPIC_API_KEY:**
1. Go to https://console.anthropic.com/
2. Create/retrieve your API key
3. Copy it to Railway Variables as `ANTHROPIC_API_KEY`

### Redeployment

After code changes:

```bash
git push origin main
```

Railway automatically redeploys on push. Watch the deployment log in the Railway dashboard.

### Health Check

```bash
curl https://torq-e-production.up.railway.app/api/chat/health
```

Expected response:
```json
{
  "status": "healthy",
  "claude_api_configured": true
}
```

If `claude_api_configured` is `false`, the `ANTHROPIC_API_KEY` env var isn't set.

---

## OPTION 2: LOCAL DEVELOPMENT

Run TORQ-e on your machine for development/testing.

### Prerequisites

- **Python 3.9+** (tested on 3.13)
- **PostgreSQL 13+**
- **Git** (to clone/pull the repo)
- **pip** (Python package manager)

### Step 1: Install PostgreSQL

**Windows:**
- Download: https://www.postgresql.org/download/windows/
- Run installer, remember the password you set for `postgres` user
- Verify: Open cmd, run `psql --version`

**Mac:**
```bash
brew install postgresql@16
brew services start postgresql@16
```

**Linux (Ubuntu):**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### Step 2: Create Database

```bash
# Open PostgreSQL command line
psql -U postgres

# Create database
CREATE DATABASE torq_e;

# Verify
\l  # Lists all databases, should see torq_e

# Exit
\q
```

### Step 3: Clone/Pull Repository

```bash
cd C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e

# If you haven't cloned yet:
# git clone <repo-url> TORQ-e

# If already cloned, pull latest:
git pull origin main
```

### Step 4: Create Python Virtual Environment

```bash
# Create venv
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal line.

### Step 5: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI (web framework)
- SQLAlchemy (database ORM)
- psycopg (PostgreSQL driver)
- anthropic (Claude API)
- And others

### Step 6: Configure Environment Variables

Create `.env` file in the TORQ-e root directory:

```bash
# Create .env
touch .env  # On Mac/Linux
# On Windows, create manually: right-click → New → Text Document → rename to .env
```

Add these to `.env`:

```
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/torq_e
ANTHROPIC_API_KEY=sk-ant-xxxxx... (your Claude API key)
```

Replace `YOUR_PASSWORD` with the PostgreSQL password you set during installation.

### Step 7: Initialize Database

```bash
python -c "from database import init_db; init_db()"
```

This creates all 27 database tables.

### Step 8: Start the API

```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 9: Access Your Local Instance

**Web App:**
```
http://localhost:8000/
```

**Interactive API Docs (Swagger):**
```
http://localhost:8000/docs
```

**Chat Health Check:**
```
http://localhost:8000/api/chat/health
```

---

## TROUBLESHOOTING

### "Connection refused" when starting

**Cause:** PostgreSQL not running

**Fix:**
- **Windows:** Start PostgreSQL from Services (services.msc)
- **Mac:** `brew services start postgresql@16`
- **Linux:** `sudo systemctl start postgresql`

### "ModuleNotFoundError: No module named 'fastapi'"

**Cause:** Dependencies not installed

**Fix:**
```bash
pip install -r requirements.txt
```

### "Database error: torq_e not found"

**Cause:** Database not created

**Fix:**
```bash
psql -U postgres -c "CREATE DATABASE torq_e;"
```

### "ANTHROPIC_API_KEY not configured"

**Cause:** Claude API key not set in env vars

**Fix:**
1. Get key from https://console.anthropic.com/
2. Add to `.env` file: `ANTHROPIC_API_KEY=sk-ant-xxxxx...`
3. Restart the API: `python main.py`

### Chat returns 500 error

**Cause:** Usually ANTHROPIC_API_KEY is missing or invalid

**Check:**
```bash
curl http://localhost:8000/api/chat/health
```

If `claude_api_configured` is `false`, the key isn't set.

### Changes not appearing

**Cause:** Code changes need restart

**Fix:**
1. Stop the API: `Ctrl+C`
2. Pull latest: `git pull origin main`
3. Restart: `python main.py`

---

## PROJECT STRUCTURE

```
TORQ-e/
├── main.py                           # FastAPI app (start here)
├── config.py                         # Settings (reads from .env)
├── database.py                       # PostgreSQL connection
├── models.py                         # 27 database models
├── chat.py                           # Claude API integration
│
├── card_1_umid/                      # Member system
│   ├── routes.py                     # 7 endpoints
│   ├── river_path.py                 # Multi-source lookup
│   ├── eligibility.py                # Eligibility logic
│   ├── confidence.py                 # Confidence scoring
│   └── schemas.py                    # Data models
│
├── card_2_upid/                      # Provider system
│   ├── routes.py                     # 6 endpoints
│   ├── provider_lookup.py            # Provider lookup
│   ├── claims_routing.py             # Claims handling
│   ├── fraud_detection.py            # Fraud detection
│   └── schemas.py                    # Data models
│
├── static/                           # Frontend assets
│   ├── branding/logo/TdST.png       # TORQ-e logo
│
├── landing.html                      # Landing page
├── login-card{1-5}.html             # Login pages
├── chat-card{1-5}.html              # Chat interfaces
├── tutorial-card{1-5}.html          # Tutorials
│
├── .env.example                      # Example env file
├── requirements.txt                  # Python dependencies
├── README.md                         # API documentation
├── BUILD_SUMMARY.md                  # Build summary
└── START_HERE.md                     # Start here (you read this first)
```

---

## PRODUCTION DEPLOYMENT ON RAILWAY

Already set up, but here's how it works:

### Auto-Deploy on Push

```bash
git push origin main
```

Railway watches your repo and automatically:
1. Pulls latest code
2. Installs dependencies: `pip install -r requirements.txt`
3. Starts the app: `python main.py`
4. Routes traffic to it

### Monitor Deployment

1. Go to https://railway.app/
2. Click your TORQ-e project
3. Watch the Deployments tab
4. Check logs in the "Logs" panel

### Environment Variables

1. Go to Railway dashboard
2. Click "Variables"
3. Set:
   - `DATABASE_URL` (your PostgreSQL connection string)
   - `ANTHROPIC_API_KEY` (your Claude API key)

### View Logs

In Railway dashboard → "Logs" tab:

```bash
# View real-time logs
tail -f logs

# Search for errors
grep error logs

# Check chat health
curl https://torq-e-production.up.railway.app/api/chat/health
```

### Scale Up

1. Go to "Settings"
2. Adjust "Memory" and "CPU"
3. Set "Concurrent Connections" limits

---

## DATABASE BACKUP

### Local Backup

```bash
# Backup
pg_dump -U postgres torq_e > backup.sql

# Restore
psql -U postgres torq_e < backup.sql
```

### Railway Backup

Railway automatically backs up PostgreSQL daily.

To restore:
1. Go to Railway dashboard
2. Click Database
3. Click "Backups" tab
4. Select backup and restore

---

## MONITORING

### Health Check Endpoint

```bash
# Local
curl http://localhost:8000/api/chat/health

# Production
curl https://torq-e-production.up.railway.app/api/chat/health
```

Response:
```json
{
  "status": "healthy",
  "claude_api_configured": true
}
```

### Database Connection Check

```bash
# Local (if you need to debug)
python -c "from database import settings; print(settings.database_url)"
```

### API Logs

**Local:**
```bash
# Watch logs while running
python main.py
```

**Railway:**
Go to Railway dashboard → Logs tab → search logs

---

## NEXT STEPS

### Local Development
1. ✅ PostgreSQL running
2. ✅ `.env` configured
3. ✅ `pip install -r requirements.txt`
4. ✅ Database initialized
5. ✅ `python main.py` started

Visit http://localhost:8000/ to test

### Production (Railway)
1. ✅ Code pushed to main branch
2. ✅ Environment variables set
3. ✅ Check deployment logs
4. ✅ Visit https://torq-e-production.up.railway.app/

---

**Last Updated:** April 24, 2026

**Status:** ✅ DEPLOYED & RUNNING

💥 **Deploy with confidence.** 💥
