import time
from fastapi import FastAPI, Depends, Request
from app.api.v1 import endpoints
from app.core.config import get_settings
import structlog

# Initialize logging
structlog.configure()
logger = structlog.get_logger()

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="""
    High-throughput Notification Service optimized for Antigravity environment.
    
    ### Features
    * **Asynchronous Notifications**: Offload delivery to Pub/Sub to maintain <100ms API latency.
    * **Secure OTP Management**: Cryptographically secure generator with atomic Firestore lifecycle.
    * **Modular Notifiers**: Pluggable adapters for Twilio, SendGrid, and more.
    """,
    version="1.0.0",
    contact={
        "name": "Kgatle Empire Services",
        "url": "https://example.com/support",
        "email": "support@example.com",
    },
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware for structured logging and performance tracking
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    logger.info(
        "request_processed",
        path=request.url.path,
        method=request.method,
        status_code=response.status_code,
        duration=f"{duration:.4f}s"
    )
    return response

@app.get("/healthz")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

# Include API router
app.include_router(endpoints.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
