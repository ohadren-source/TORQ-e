"""
TORQ-e: Medicaid Clarity System
Main FastAPI Application

Card 1 (UMID): Member Eligibility System
Card 2 (UPID): Provider System [In Development]
Card 3 (UHWP): Plan Administrator [Planned]
Card 4 (USHI): Government Stakeholder [Planned]
Card 5 (UBADA): Data Analyst & Fraud Investigation [Planned]
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from config import settings
from database import init_db
from card_1_umid import router as card1_router
from card_2_upid import router as card2_router
from chat import router as chat_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version
)

# CORS middleware (enable cross-origin requests for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing TORQ-E database...")
    try:
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

# Include Card 1 & 2 routes
app.include_router(card1_router)
app.include_router(card2_router)

# Include Chat router (Claude API integration)
app.include_router(chat_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "TORQ-e: Medicaid Clarity System",
        "version": settings.api_version,
        "cards": {
            "1": {
                "name": "UMID (Member Eligibility)",
                "status": "✅ LIVE",
                "endpoints": [
                    "POST /api/card1/lookup",
                    "POST /api/card1/eligibility/check",
                    "POST /api/card1/eligibility/detailed",
                    "POST /api/card1/recertification/status",
                    "POST /api/card1/documents/upload",
                    "POST /api/card1/income/report",
                    "GET /api/card1/health"
                ]
            },
            "2": {
                "name": "UPID (Provider System)",
                "status": "✅ LIVE",
                "endpoints": [
                    "POST /api/card2/lookup",
                    "POST /api/card2/enrollment/check",
                    "POST /api/card2/claims/validate",
                    "POST /api/card2/claims/submit",
                    "POST /api/card2/claims/status",
                    "POST /api/card2/fraud/analyze"
                ]
            },
            "3": {
                "name": "UHWP (Plan Administrator)",
                "status": "📋 PLANNED"
            },
            "4": {
                "name": "USHI (Government Stakeholder)",
                "status": "📋 PLANNED"
            },
            "5": {
                "name": "UBADA (Data Analyst/Fraud)",
                "status": "📋 PLANNED"
            }
        }
    }

# 404 handler
@app.get("/api/card1/docs", include_in_schema=False)
async def swagger_ui():
    """Redirect to OpenAPI docs"""
    return JSONResponse({"redirect": "/docs"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
