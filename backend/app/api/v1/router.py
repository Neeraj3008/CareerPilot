from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, profiles, resumes, jobs, search, 
    recommendations, chat, saved_jobs, preferences, health
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["Profiles"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["Resumes"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
api_router.include_router(search.router, prefix="/search", tags=["Semantic Search"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
api_router.include_router(chat.router, prefix="/chat", tags=["AI Agent Chat"])
api_router.include_router(saved_jobs.router, prefix="/saved-jobs", tags=["Saved Jobs"])
api_router.include_router(preferences.router, prefix="/preferences", tags=["Preferences"])
