# Railway Deployment Guide - TORQ-e Cards 1-5
**Updated:** April 25, 2026

---

## PRE-DEPLOYMENT CHECKLIST

### 1. Verify All Local Files Are Ready
```bash
# Card 1 (UMID) - Member Eligibility
C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\card_1_umid\schemas.py  ✅
C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\card_1_umid\routes.py   ✅

# Card 2 (UPID) - Provider System
C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\card_2_upid\schemas.py  ✅
C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\card_2_upid\routes.py   ✅

# Card 5 (UBADA) - Fraud Investigation
C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\chat-card5.html         ✅

# Documentation
C:\Users\ohado\Downloads\SNGBOTME\CARD_4_5_ARCHITECTURE_BLUEPRINT.md  ✅
C:\Users\ohado\Downloads\SNGBOTME\DEPLOYMENT_STATUS_SUMMARY.md        ✅
```

### 2. Identify Your Railway Repo Location
The production Railway repo should be cloned locally. Typical location:
```
~/projects/torq-e-production
```

---

## STEP-BY-STEP DEPLOYMENT

### PHASE 1: Update Backend Files (Cards 1 & 2)

#### Step 1.1: Copy Card 1 Updated Files
```bash
# Source files (where they are now)
C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\card_1_umid\schemas.py
C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\card_1_umid\routes.py

# Destination in Railway repo
~/projects/torq-e-production/card_1_umid/schemas.py
~/projects/torq-e-production/card_1_umid/routes.py

# Commands
cp "C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\card_1_umid\schemas.py" ~/projects/torq-e-production/card_1_umid/
cp "C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\card_1_umid\routes.py" ~/projects/torq-e-production/card_1_umid/
```

#### Step 1.2: Copy Card 2 Updated Files
```bash
# Source files
C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\card_2_upid\schemas.py
C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\card_2_upid\routes.py

# Destination in Railway repo
~/projects/torq-e-production/card_2_upid/schemas.py
~/projects/torq-e-production/card_2_upid/routes.py

# Commands
cp "C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\card_2_upid\schemas.py" ~/projects/torq-e-production/card_2_upid/
cp "C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\card_2_upid\routes.py" ~/projects/torq-e-production/card_2_upid/
```

#### Verification After Copy
```bash
# In Railway repo, verify the files have confidence_score changes
cd ~/projects/torq-e-production

# Check Card 1 schemas
grep "confidence_score: float" card_1_umid/schemas.py
# Expected: Should find 4 lines (EligibilityStatusResponse, EligibilityDetailedResponse, RecertificationStatusResponse, IncomeChangeResponse)

# Check Card 1 routes
grep "confidence_score=" card_1_umid/routes.py
# Expected: Should find 2 lines (check_eligibility_member_view, check_recertification_status)

# Check Card 2 schemas
grep "confidence_score: float" card_2_upid/schemas.py
# Expected: Should find 2 lines (ProviderEnrollmentStatusResponse, ClaimValidationResponse)

# Check Card 2 routes
grep "confidence_score=" card_2_upid/routes.py
# Expected: Should find 2 lines (check_enrollment_status, validate_claim)
```

### PHASE 2: Update Frontend Files (Cards 4 & 5)

#### Step 2.1: Copy Updated Card 5 HTML
```bash
# Source file
C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\chat-card5.html

# Destination in Railway repo
~/projects/torq-e-production/static/cards/chat-card5.html

# Command
cp "C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\chat-card5.html" ~/projects/torq-e-production/static/cards/
```

#### Verification After Copy
```bash
# Check API endpoint
grep "API_BASE = " ~/projects/torq-e-production/static/cards/chat-card5.html
# Expected output: const API_BASE = 'https://torq-e-production.up.railway.app/api/card5';

# Check dimensions
grep "Claims Data Quality" ~/projects/torq-e-production/static/cards/chat-card5.html
# Expected: Should find references to Card 5 dimensions

# Check function names
grep "processInvestigationQuery" ~/projects/torq-e-production/static/cards/chat-card5.html
# Expected: Should find multiple references to investigation query routing
```

### PHASE 3: Update Documentation (Optional but Recommended)

#### Step 3.1: Add Architecture Documentation
```bash
# Create docs folder if it doesn't exist
mkdir -p ~/projects/torq-e-production/docs

# Copy architecture blueprint
cp "C:\Users\ohado\Downloads\SNGBOTME\CARD_4_5_ARCHITECTURE_BLUEPRINT.md" ~/projects/torq-e-production/docs/

# Copy deployment status
cp "C:\Users\ohado\Downloads\SNGBOTME\DEPLOYMENT_STATUS_SUMMARY.md" ~/projects/torq-e-production/docs/
```

---

## GIT COMMIT & PUSH

### Step 4: Stage All Changes
```bash
cd ~/projects/torq-e-production

# Stage all changes
git add -A

# Verify staged files
git status
```

**Expected Output Should Show:**
```
modified:   card_1_umid/schemas.py
modified:   card_1_umid/routes.py
modified:   card_2_upid/schemas.py
modified:   card_2_upid/routes.py
modified:   static/cards/chat-card5.html
new file:   docs/CARD_4_5_ARCHITECTURE_BLUEPRINT.md
new file:   docs/DEPLOYMENT_STATUS_SUMMARY.md
```

### Step 5: Create Commit Message
```bash
git commit -m "Phase 2 Complete: Cards 1-5 Architecture & Confidence Scores

CARDS 1 & 2 (Confidence Scores):
- Added confidence_score field to all external-source-requiring response schemas
- Card 1: EligibilityStatusResponse, RecertificationStatusResponse return confidence
- Card 2: ProviderEnrollmentStatusResponse, ClaimValidationResponse return confidence
- Confidence scoring logic: 0.90-1.0 HIGH | 0.60-0.89 MEDIUM | <0.60 LOW

CARDS 4 & 5 (Architectural Parity):
- Card 5 completely rewritten to match Card 4 architecture
- Only differences: API endpoints, role context, dimension names, breakdown data
- 100% UI/UX parity: Spectrum Analyzer, collapse/expand, breakdown panels, source removal
- Added comprehensive architecture blueprint (CARD_4_5_ARCHITECTURE_BLUEPRINT.md)

TESTING READY:
- 9-inquiry test matrix defined
- All backend endpoints returning confidence scores
- All frontend UI components architecturally identical

DEPLOYMENT TARGET: Railway production environment"
```

### Step 6: Push to Railway
```bash
# Push to main branch (or your deployment branch)
git push origin main

# Verify push successful
git log --oneline -5
# Should show your new commit at the top
```

---

## POST-DEPLOYMENT VERIFICATION (Railway)

### Step 7: Monitor Railway Deployment
1. Go to https://railway.app/
2. Select TORQ-e project
3. Watch deployment progress (should take 2-5 minutes)
4. Verify all services are running (green status)

### Step 8: Smoke Test All Cards

#### Card 1 Smoke Test
```bash
curl -X POST https://torq-e-production.up.railway.app/api/card1/lookup \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-15",
    "ssn": "123456789"
  }'

# Expected: Response should include "confidence_score" field
```

#### Card 2 Smoke Test
```bash
curl -X POST https://torq-e-production.up.railway.app/api/card2/enrollment/check \
  -H "Content-Type: application/json" \
  -d '{"upid": "UPID123456"}'

# Expected: Response should include "confidence_score" field
```

#### Card 4 Smoke Test
```bash
# Just load the card in browser
https://torq-e-production.up.railway.app/static/cards/chat-card4.html

# Verify: Spectrum Analyzer loads, can click to collapse/expand
```

#### Card 5 Smoke Test
```bash
# Load the card in browser
https://torq-e-production.up.railway.app/static/cards/chat-card5.html

# Verify:
# - Dev notice shows "Card 5 backend ready"
# - Initial message shows "Data Analyst & Fraud Investigation"
# - Dimensions show Card 5 context (Claims Data Quality, Outlier Detection, etc.)
# - Can type queries and get responses
```

---

## TROUBLESHOOTING

### Issue: Deployment Fails
**Solution:**
1. Check Railway logs: https://railway.app/ → TORQ-e project → Logs tab
2. Look for Python errors in card_1_umid/schemas.py or card_2_upid/routes.py
3. Common issue: Missing imports (ensure `from typing import Optional, List, Dict`)

### Issue: Confidence Scores Not Showing in Responses
**Solution:**
1. Verify schemas.py was copied correctly (check for `confidence_score: float` lines)
2. Verify routes.py includes `confidence_score=` in return statements
3. Restart Railway deployment after copying files

### Issue: Card 5 Shows Wrong Dimensions
**Solution:**
1. Verify chat-card5.html was copied to correct location
2. Check that file contains "Claims Data Quality", "Outlier Detection", etc.
3. Hard refresh browser (Ctrl+F5 or Cmd+Shift+R)

### Issue: API Endpoint Returns 404
**Solution:**
1. Verify Railway services are running (Railway dashboard → green status)
2. Check that you're using correct API base URL: `https://torq-e-production.up.railway.app`
3. Verify endpoints match routes.py definitions

---

## ROLLBACK PLAN

If deployment has critical issues:

### Quick Rollback
```bash
cd ~/projects/torq-e-production

# Revert to previous commit
git revert HEAD
git push origin main

# Railway will auto-redeploy with previous version
```

### Manual Rollback
1. Go to Railway dashboard
2. Select TORQ-e project
3. Go to Deployments tab
4. Click on previous successful deployment
5. Click "Redeploy"

---

## SUCCESS CRITERIA

✅ All 4 services running in Railway (green status)
✅ Card 1 endpoints return confidence_score field
✅ Card 2 endpoints return confidence_score field
✅ Card 4 Spectrum Analyzer displays and is interactive
✅ Card 5 loads with Card 5-specific dimensions and breakdown data
✅ All 9 test inquiries execute successfully
✅ Claude system prompts extract confidence scores and display traffic lights

---

## POST-DEPLOYMENT NEXT STEPS

1. **Smoke Test Results:** Document 9-inquiry test results
2. **Regulatory Review:** Present findings to Bob Pollock
3. **Approval Gate:** Get governmental stakeholder sign-off
4. **Scale Planning:** Begin Phase 3 proof-of-concept scaling
5. **Timeline:** Rest of 2026 through early 2027 for full production rollout

