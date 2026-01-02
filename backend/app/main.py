from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.api.v1 import api_router
from app.db.database import engine
from app.db import models
import os

# Create database tables (only if database is available)
try:
    models.Base.metadata.create_all(bind=engine)
except Exception:
    pass  # Database will be created via migrations

app = FastAPI(
    title="AI Video Generation API",
    description="Automated product video generation platform",
    version="1.0.0",
    docs_url="/api/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT == "development" else None
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address, default_limits=["1000/hour"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Add rate limiting middleware (must be after router includes)
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Apply rate limiting to all routes except health check
    if request.url.path != "/health":
        try:
            await limiter.check(request)
        except RateLimitExceeded:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."}
            )
    response = await call_next(request)
    return response

# Serve local storage files (must be before route includes to avoid conflicts)
local_storage_dir = os.path.join(os.getcwd(), 'local_storage')
os.makedirs(local_storage_dir, exist_ok=True)
try:
    app.mount("/local_storage", StaticFiles(directory=local_storage_dir), name="local_storage")
except Exception:
    pass  # Already mounted or error


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


