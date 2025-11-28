"""
FastAPI main application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.config import settings
from backend.api import auth_router, calibrations_router, mfa_router
import os

app = FastAPI(
    title=settings.APP_NAME,
    description="A web application for Hand-Eye calibration in camera-robot systems",
    version="0.1.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving uploaded images
uploads_base_dir = "uploads"
if not os.path.exists(uploads_base_dir):
    os.makedirs(uploads_base_dir, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=uploads_base_dir), name="uploads")

# Include routers
app.include_router(auth_router, prefix="/api/v1", tags=["authentication"])
app.include_router(calibrations_router, prefix="/api/v1", tags=["calibrations"])
app.include_router(mfa_router, prefix="/api/v1/mfa", tags=["mfa"])


@app.get("/")
async def root():
    """
    Root endpoint - basic health check.
    """
    return {
        "message": "Hand-Eye Calibration System API",
        "status": "operational",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
