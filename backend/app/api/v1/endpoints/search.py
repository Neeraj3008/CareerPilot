from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.models import Job
from app.schemas.schemas import JobResponse, JobSearchQuery
from app.services.embeddings import get_embedding, cosine_similarity

router = APIRouter()

@router.post("/", response_model=List[JobResponse])
def semantic_job_search(
    search_in: JobSearchQuery,
    db: Session = Depends(get_db)
):
    query = db.query(Job).filter(Job.is_active == True)

    if search_in.remote_policy:
        query = query.filter(Job.remote_policy == search_in.remote_policy.upper())
    if search_in.experience_level:
        query = query.filter(Job.experience_level == search_in.experience_level.upper())
    if search_in.location:
        query = query.filter(Job.location.ilike(f"%{search_in.location}%"))
    if search_in.min_salary:
        query = query.filter(Job.max_salary >= search_in.min_salary)

    candidates = query.all()
    if not candidates:
        return []

    if not search_in.query or not search_in.query.strip():
        return candidates[:search_in.limit]

    # Semantic search with query vector
    query_vec = get_embedding(search_in.query)
    scored = []
    q_lower = search_in.query.lower()

    for job in candidates:
        sim = cosine_similarity(query_vec, job.embedding) if job.embedding else 0.0
        # Keyword match boost
        kw_boost = 0.0
        if q_lower in job.title.lower():
            kw_boost += 0.25
        if q_lower in job.description.lower():
            kw_boost += 0.15
        for s in (job.skills or []):
            if q_lower in s.skill_name.lower():
                kw_boost += 0.2
        
        total_score = sim + kw_boost
        scored.append((total_score, job))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [job for _, job in scored[:search_in.limit]]
