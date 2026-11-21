from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.models import Job, JobSkill, User
from app.schemas.schemas import JobResponse, JobCreate
from app.services.embeddings import get_embedding

router = APIRouter()

@router.get("/", response_model=List[JobResponse])
def get_jobs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    remote_policy: Optional[str] = None,
    experience_level: Optional[str] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Job).filter(Job.is_active == True)
    if remote_policy:
        query = query.filter(Job.remote_policy == remote_policy.upper())
    if experience_level:
        query = query.filter(Job.experience_level == experience_level.upper())
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))

    offset = (page - 1) * limit
    return query.order_by(Job.created_at.desc()).offset(offset).limit(limit).all()

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job

@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job_in: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Compute job vector embedding for semantic search
    skills_text = ", ".join(job_in.skills)
    embed_text = f"Title: {job_in.title}. Company: {job_in.company}. Location: {job_in.location}. Requirements: {skills_text}. Description: {job_in.description}"
    job_embedding = get_embedding(embed_text)

    job = Job(
        title=job_in.title,
        company=job_in.company,
        description=job_in.description,
        location=job_in.location,
        remote_policy=job_in.remote_policy,
        job_type=job_in.job_type,
        min_salary=job_in.min_salary,
        max_salary=job_in.max_salary,
        currency=job_in.currency,
        experience_level=job_in.experience_level,
        source_url=job_in.source_url,
        embedding=job_embedding
    )
    db.add(job)
    db.flush()

    for skill in job_in.skills:
        js = JobSkill(job_id=job.id, skill_name=skill, is_required=True)
        db.add(js)

    db.commit()
    db.refresh(job)
    return job
