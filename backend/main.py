"""
FastAPI main application entry point.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from backend.config import settings
from backend.api import auth_router, calibrations_router, mfa_router
import os
import structlog
import time
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from backend.utils.limiter import limiter
from backend.logging_config import configure_logging

# Seguridad A09: Configurar Logging Estructurado
configure_logging()
logger = structlog.get_logger()

# Seguridad A07: Configuración de Rate Limiting
app = FastAPI(
    title=settings.APP_NAME,
    description="A web application for Hand-Eye calibration in camera-robot systems",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Seguridad A05: Headers de seguridad HTTP
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    # Relaxed CSP for Swagger UI
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https://fastapi.tiangolo.com; "
        "font-src 'self' https://cdn.jsdelivr.net; "
        "connect-src 'self';"
    )
    response.headers["Content-Security-Policy"] = csp
    return response

# Seguridad A09: Logging de Auditoría (Quién, Qué, Cuándo, Dónde)
@app.middleware("http")
async def audit_logging_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Extract user info if available (this is tricky in middleware before auth, 
    # but we can log the request path and method)
    # For authenticated endpoints, the user is extracted in the dependency.
    # We'll log the request details here.
    
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host,
        request_id=request.headers.get("X-Request-ID"),
    )
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    status_code = response.status_code
    
    # Log audit event
    logger.info(
        "http_request",
        status_code=status_code,
        process_time=process_time,
        # Seguridad A09: NUNCA guardar contraseñas o tokens
        # We are not logging body here, so safe.
    )
    
    return response

# Seguridad A05: Manejo de errores seguro (no exponer info sensible)
@app.exception_handler(500)
async def internal_exception_handler(request: Request, exc: Exception):
    logger.error("internal_error", error=str(exc))
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error. Please contact support."}
    )

# Configure CORS for frontend access
# Seguridad A05: Configuración CORS restrictiva
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (required for WebSockets)
    allow_headers=["*"], # Allow all headers (Reflex sends custom headers)
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
        port=8001,
        reload=settings.DEBUG
    )
