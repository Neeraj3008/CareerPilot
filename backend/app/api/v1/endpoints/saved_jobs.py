from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.models.models import User, SavedJob, Job
from app.schemas.schemas import SavedJobResponse, SavedJobCreate, SavedJobUpdate

router = APIRouter()

@router.get("/", response_model=List[SavedJobResponse])
def get_saved_jobs(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return db.query(SavedJob).filter(
        SavedJob.user_id == current_user.id
    ).order_by(SavedJob.created_at.desc()).all()

@router.post("/", response_model=SavedJobResponse, status_code=status.HTTP_201_CREATED)
def save_job(
    saved_in: SavedJobCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == saved_in.job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    existing = db.query(SavedJob).filter(
        SavedJob.user_id == current_user.id,
        SavedJob.job_id == saved_in.job_id
    ).first()
    if existing:
        return existing

    saved = SavedJob(
        user_id=current_user.id,
        job_id=saved_in.job_id,
        notes=saved_in.notes,
        status=saved_in.status
    )
    db.add(saved)
    db.commit()
    db.refresh(saved)
    return saved

@router.put("/{saved_id}", response_model=SavedJobResponse)
def update_saved_job(
    saved_id: str,
    update_in: SavedJobUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    saved = db.query(SavedJob).filter(
        SavedJob.id == saved_id,
        SavedJob.user_id == current_user.id
    ).first()
    if not saved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved job not found")

    if update_in.status:
        saved.status = update_in.status
    if update_in.notes is not None:
        saved.notes = update_in.notes

    db.commit()
    db.refresh(saved)
    return saved

@router.delete("/{saved_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_job(
    saved_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    saved = db.query(SavedJob).filter(
        SavedJob.id == saved_id,
        SavedJob.user_id == current_user.id
    ).first()
    if not saved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved job not found")

    db.delete(saved)
    db.commit()
    return None
