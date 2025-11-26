"""
FastAPI main application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.api import auth_router, calibrations_router

app = FastAPI(
    title=settings.APP_NAME,
    description="A web application for Hand-Eye calibration in camera-robot systems",
    version="0.1.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1", tags=["authentication"])
app.include_router(calibrations_router, prefix="/api/v1", tags=["calibrations"])


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
