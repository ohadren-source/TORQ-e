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
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import logging
import os

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

# Mount static files (HTML, CSS, images, etc.)
# Serve from the project root directory where landing.html, login-*.html, etc. are located
static_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Root endpoint - serve landing.html
@app.get("/", include_in_schema=False)
async def root():
    """Serve the landing page"""
    landing_path = os.path.join(static_dir, "landing.html")
    if os.path.exists(landing_path):
        return FileResponse(landing_path, media_type="text/html")
    # Fallback to JSON if landing.html not found
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

# Catch-all for HTML files (login, chat, tutorial pages)
@app.get("/{file_path:path}", include_in_schema=False)
async def serve_html(file_path: str):
    """Serve HTML files (login-card*.html, chat-card*.html, tutorial-card*.html)"""
    # Only serve .html files
    if not file_path.endswith('.html'):
        return JSONResponse({"detail": "Not Found"}, status_code=404)

    file_full_path = os.path.join(static_dir, file_path)
    if os.path.exists(file_full_path):
        return FileResponse(file_full_path, media_type="text/html")

    return JSONResponse({"detail": "Not Found"}, status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
