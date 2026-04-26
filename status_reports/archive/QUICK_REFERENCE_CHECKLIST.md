# TORQ-e Deployment: Quick Reference Checklist
**Last Updated:** April 25, 2026 | **All Code Changes Complete** ✅

---

## WHAT'S BEEN COMPLETED

### Code Changes (Ready to Deploy)
- ✅ **Card 1:** schemas.py + routes.py with confidence_score fields and computation
- ✅ **Card 2:** schemas.py + routes.py with confidence_score fields and computation  
- ✅ **Card 5:** Complete rewrite to match Card 4 architecture with Card 5 data

### Documentation Generated
- ✅ **CARD_4_5_ARCHITECTURE_BLUEPRINT.md** - 470+ line comprehensive architecture
- ✅ **DEPLOYMENT_STATUS_SUMMARY.md** - Complete status of all work
- ✅ **RAILWAY_DEPLOYMENT_GUIDE.md** - Step-by-step deployment procedures
- ✅ **TEST_MATRIX_9_INQUIRIES.md** - 9 specific tests with pass/fail criteria
- ✅ **QUICK_REFERENCE_CHECKLIST.md** - This file

---

## PRE-DEPLOYMENT VERIFICATION (5 min)

### 1. Local Files Exist
```
[ ] C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\card_1_umid\schemas.py     ✅
[ ] C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\card_1_umid\routes.py      ✅
[ ] C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\card_2_upid\schemas.py     ✅
[ ] C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\card_2_upid\routes.py      ✅
[ ] C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\chat-card5.html            ✅
```

### 2. Quick Grep Verification (Optional - to verify changes)
```bash
# Card 1 - should find 4 confidence_score fields in schemas
grep -c "confidence_score: float" C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\card_1_umid\schemas.py
# Expected: 4

# Card 2 - should find 2 confidence_score fields in schemas
grep -c "confidence_score: float" C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\card_2_upid\schemas.py
# Expected: 2

# Card 5 - should find Card 5 dimensions
grep "Claims Data Quality" C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\chat-card5.html
# Expected: Should find the line
```

---

## DEPLOYMENT (15 min)

### Step 1: Navigate to Railway Repo
```bash
cd ~/projects/torq-e-production
```

### Step 2: Copy Files
```bash
# Copy Card 1
cp "C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\card_1_umid\schemas.py" card_1_umid/
cp "C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\card_1_umid\routes.py" card_1_umid/

# Copy Card 2
cp "C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\card_2_upid\schemas.py" card_2_upid/
cp "C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\card_2_upid\routes.py" card_2_upid/

# Copy Card 5
cp "C:\Users\ohado\Documents\3_6_Nife.pi\TORQ-e\chat-card5.html" static/cards/

# Copy Documentation (optional)
mkdir -p docs
cp "C:\Users\ohado\Downloads\SNGBOTME\CARD_4_5_ARCHITECTURE_BLUEPRINT.md" docs/
cp "C:\Users\ohado\Downloads\SNGBOTME\DEPLOYMENT_STATUS_SUMMARY.md" docs/
```

### Step 3: Git Commit
```bash
git add -A
git commit -m "Phase 2 Complete: Cards 1-5 Architecture & Confidence Scores

CARDS 1 & 2: confidence_score fields + computation logic
CARDS 4 & 5: Card 5 rewritten for architectural parity
READY: 9-inquiry test matrix, regulatory review"
git push origin main
```

### Step 4: Monitor Railway
- Go to https://railway.app/
- Watch deployment (2-5 min)
- Verify all services green ✅

---

## POST-DEPLOYMENT VERIFICATION (10 min)

### Quick Smoke Tests

#### Card 1 - Load & Type
```
URL: https://torq-e-production.up.railway.app/static/cards/chat-card1.html
Test: Ask "What member ID does John Doe have?"
Verify: Response includes confidence_score in API + traffic light in Claude response
```

#### Card 2 - Load & Type
```
URL: https://torq-e-production.up.railway.app/static/cards/chat-card2.html
Test: Ask "Is provider UPID123456 enrolled in FFS?"
Verify: Response includes confidence_score in API + traffic light in Claude response
```

#### Card 4 - Load & Interact
```
URL: https://torq-e-production.up.railway.app/static/cards/chat-card4.html
Test: Ask "What is system coherence?"
Verify: Spectrum Analyzer displays, can click to collapse/expand sections
```

#### Card 5 - Load & Verify
```
URL: https://torq-e-production.up.railway.app/static/cards/chat-card5.html
Test: Ask "What is claims data quality?"
Verify: Dimensions are Card 5 specific (Claims Data Quality, Outlier Detection, etc.)
Verify: Dev notice says "Card 5 backend ready"
Verify: Initial message says "Data Analyst & authenticity investigation"
```

---

## EXECUTE FULL TEST MATRIX (30-45 min)

### Use TEST_MATRIX_9_INQUIRIES.md
```
Complete all 9 tests:
  [ ] 1a: Member Lookup
  [ ] 1b: Eligibility Check  
  [ ] 1c: Recertification
  [ ] 2a: Provider Lookup
  [ ] 2b: Enrollment Check
  [ ] 2c: Claim Validation
  [ ] 4: Card 4 Governance Metrics
  [ ] 5a: Card 5 Investigation Metrics
  [ ] 5b: Card 5 Elaborate + Sources

Document:
  [ ] Each test result (PASS/FAIL)
  [ ] Confidence score values
  [ ] Traffic light colors displayed
  [ ] Screenshots of each result
```

---

## REGULATORY APPROVAL (Submit to Bob Pollock)

### Package for Submission
```
[ ] DEPLOYMENT_STATUS_SUMMARY.md (executive summary)
[ ] CARD_4_5_ARCHITECTURE_BLUEPRINT.md (technical architecture)
[ ] TEST_MATRIX_9_INQUIRIES.md with all tests marked PASS
[ ] Screenshots of 9 test results
[ ] Console logs showing confidence_score fields
```

### Required Gate
- ✅ All 9 tests must PASS
- ✅ All critical success criteria met
- ✅ Bob Pollock regulatory sign-off obtained

---

## CONFIDENCE SCORE MAPPING REFERENCE

### How Claude Displays Lights

```
Backend returns: confidence_score (float, 0.0 to 1.0)
                     ↓
Claude extracts: veracity level from _confidence_metadata
                     ↓
Claude displays: Traffic light
                 🟢 if >= 0.85 (HIGH confidence)
                 🟡 if >= 0.60 (MEDIUM confidence)
                 🔴 if  < 0.60 (LOW confidence)
```

### Card 1 Confidence Score Logic
```
check_eligibility():
  - Confidence based on data source agreement + verification status
  - Returned in EligibilityStatusResponse

check_recertification():
  - 0.85 if days_until_recert > 30 days (ON_TRACK)
  - 0.65 if days_until_recert > 0 days (URGENT)
  - 0.45 if overdue
  - Returned in RecertificationStatusResponse
```

### Card 2 Confidence Score Logic
```
check_enrollment():
  - 0.90 if credentials valid + FFS enrolled + MCOs active
  - 0.75 if any valid
  - 0.50 if none
  - Returned in ProviderEnrollmentStatusResponse

validate_claim():
  - 0.95 if no errors and no warnings
  - 0.75 if no errors but has warnings
  - 0.40 if has errors
  - Returned in ClaimValidationResponse
```

---

## TROUBLESHOOTING QUICK GUIDE

### Problem: API Returns 500 Error
**Solution:** Check Railway logs for Python syntax errors in updated files
```bash
# Verify imports in schemas.py
grep -E "from pydantic|from typing" card_1_umid/schemas.py
# Should find imports

# Verify confidence_score= in routes.py
grep "confidence_score=" card_1_umid/routes.py
# Should find return statements
```

### Problem: Confidence Scores Not Showing
**Solution:** 
1. Verify schemas.py was copied (has `confidence_score: float` fields)
2. Verify routes.py was copied (has `confidence_score=` in returns)
3. Hard refresh browser (Ctrl+F5)
4. Check Railway deployment status (should be green)

### Problem: Card 5 Shows Wrong Dimensions
**Solution:**
1. Verify chat-card5.html was copied to `static/cards/`
2. Check file contains "Claims Data Quality" not "Enrollment Rate"
3. Hard refresh browser cache
4. Check browser console for JavaScript errors

### Problem: Cards Not Loading
**Solution:**
1. Verify Railway services all green in dashboard
2. Check URL is correct: `https://torq-e-production.up.railway.app/`
3. Check firewall isn't blocking Railway domain
4. Try different browser or incognito mode

---

## SUCCESS INDICATORS

### Deployment Successful When:
- ✅ All 5 cards load without JavaScript errors
- ✅ Card 1 API returns `"confidence_score"` field in response
- ✅ Card 2 API returns `"confidence_score"` field in response
- ✅ Card 4 Spectrum Analyzer displays and is interactive
- ✅ Card 5 dimensions are Card 5-specific (not Card 4)
- ✅ All 9 tests PASS with traffic lights displaying
- ✅ Claude extracts veracity and shows 🟢/🟡/🔴 for external source queries

### Ready for Regulatory Review When:
- ✅ All success indicators met
- ✅ All 9 tests documented with PASS results
- ✅ Screenshots captured and organized
- ✅ Architecture blueprint reviewed
- ✅ No unresolved errors or issues

---

## TIMELINE AT A GLANCE

```
TODAY (April 25):
  [ ] Code changes complete (✅ done)
  [ ] Documentation complete (✅ done)
  [ ] Ready for deployment

TOMORROW (April 26):
  [ ] Deploy to Railway
  [ ] Quick smoke tests (10 min)
  [ ] Execute full 9-inquiry matrix (45 min)
  [ ] Prepare for Bob Pollock review

NEXT WEEK (April 28-30):
  [ ] Regulatory review with Bob Pollock
  [ ] Approval gate
  [ ] Begin Phase 3 planning

PHASE 3 (Rest of 2026 → Early 2027):
  [ ] Proof-of-concept at scale
  [ ] Full production rollout
  [ ] Training and documentation
```

---

## KEY CONTACTS & RESOURCES

### Support
- **Railway Dashboard:** https://railway.app/
- **API Base URL:** https://torq-e-production.up.railway.app
- **Issues/Errors:** Check Railway logs first

### Regulatory
- **Approval Gate:** Bob Pollock (Government Stakeholder)
- **Required Deliverables:** Test results, architecture blueprint, screenshots

### Documentation
- **Architecture:** CARD_4_5_ARCHITECTURE_BLUEPRINT.md
- **Deployment:** RAILWAY_DEPLOYMENT_GUIDE.md
- **Testing:** TEST_MATRIX_9_INQUIRIES.md
- **Status:** DEPLOYMENT_STATUS_SUMMARY.md

---

## COMPLETION CHECKLIST

### Pre-Deployment
- [ ] All 5 local files verified
- [ ] No breaking changes to existing functionality
- [ ] Documentation complete

### Deployment
- [ ] Files copied to Railway repo
- [ ] Git commit with clear message
- [ ] Push to main branch
- [ ] Railway deployment completes (green status)

### Post-Deployment
- [ ] Smoke tests all pass
- [ ] 9-inquiry test matrix all PASS
- [ ] Screenshots captured
- [ ] Console logs documented
- [ ] Ready for Bob Pollock review

### Regulatory
- [ ] Submit all deliverables
- [ ] Bob Pollock approves
- [ ] Proceed to Phase 3

---

**CURRENT STATUS:** All code complete ✅ | Ready for deployment | Ready for testing | Awaiting regulatory approval

