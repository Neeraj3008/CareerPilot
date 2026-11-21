from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.models.models import User, Job, CandidateProfile, UserPreference, Recommendation
from app.schemas.schemas import RecommendationResponse, JobResponse
from app.services.recommendation import score_job_for_candidate

router = APIRouter()

@router.get("/", response_model=List[RecommendationResponse])
def get_recommendations(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    preference = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    jobs = db.query(Job).filter(Job.is_active == True).all()

    if not jobs:
        return []

    results = []
    for job in jobs:
        score_data = score_job_for_candidate(job, profile, preference)
        results.append({
            "id": f"rec-{job.id}",
            "job": job,
            "match_score": score_data["match_score"],
            "score_breakdown": score_data["score_breakdown"],
            "matching_skills": score_data["matching_skills"],
            "missing_skills": score_data["missing_skills"],
            "generated_at": profile.updated_at if profile else job.created_at
        })

    # Sort deterministically by highest match score
    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results[:limit]
