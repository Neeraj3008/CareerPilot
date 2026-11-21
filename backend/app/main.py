from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db, SessionLocal
from app.api.v1.router import api_router
from app.scripts.seed_jobs import seed_jobs_dataset

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB tables and seed dataset
    init_db()
    db = SessionLocal()
    try:
        seed_jobs_dataset(db)
    finally:
        db.close()
    yield
    # Shutdown

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="CareerPilot: Production-Oriented AI Job Search & Career Recommendation Agent API",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root level health checks for Render / Kubernetes
@app.get("/healthz", tags=["Health"])
def root_healthz():
    return {"status": "healthy", "service": "careerpilot-api"}

@app.get("/readyz", tags=["Health"])
def root_readyz():
    return {"status": "ready"}

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
