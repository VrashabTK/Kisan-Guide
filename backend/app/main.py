import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.core.config import settings
from backend.app.core.security import init_firebase
from backend.app.api.routes import (
    auth,
    crops,
    weather,
    storage,
    ai,
    saved,
    notifications,
    farms
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("kissan_guide")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Full-Stack Agricultural Assistance Platform for Dakshina Kannada Farmers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing KISSAN GUIDE Backend...")
    init_firebase()
    logger.info("KISSAN GUIDE Backend ready.")

@app.get("/", tags=["Root"])
async def root():
    return {
        "app": settings.PROJECT_NAME,
        "description": "Dakshina Kannada Agricultural Assistance Platform",
        "supported_crops": ["Coconut", "Rice", "Arecanut", "Cocoa"],
        "taluks": [
            "Mangaluru", "Bantwal", "Belthangady", "Puttur",
            "Sullia", "Moodbidri", "Kadaba", "Mulki", "Ullal"
        ],
        "status": "healthy",
        "docs": "/docs",
    }

@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "weather_provider": settings.WEATHER_PROVIDER,
        "ai_provider": settings.AI_PROVIDER,
    }

# Include API v1 routers
api_prefix = settings.API_V1_STR
app.include_router(auth.router, prefix=api_prefix)
app.include_router(crops.router, prefix=api_prefix)
app.include_router(weather.router, prefix=api_prefix)
app.include_router(storage.router, prefix=api_prefix)
app.include_router(ai.router, prefix=api_prefix)
app.include_router(saved.router, prefix=api_prefix)
app.include_router(notifications.router, prefix=api_prefix)
app.include_router(farms.router, prefix=api_prefix)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global unhandled error at {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please try again later."}
    )
