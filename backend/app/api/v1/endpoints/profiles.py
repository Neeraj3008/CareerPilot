from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.models.models import User, CandidateProfile
from app.schemas.schemas import CandidateProfileResponse, CandidateProfileUpdate
from app.services.embeddings import get_embedding

router = APIRouter()

@router.get("/me", response_model=CandidateProfileResponse)
def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id, skills=[], education=[], experience=[], projects=[])
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.put("/me", response_model=CandidateProfileResponse)
def update_my_profile(
    profile_in: CandidateProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)

    update_data = profile_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(profile, field, val)

    # Recalculate embedding from updated profile data
    skills_str = ", ".join(profile.skills or [])
    embed_text = f"Role: {profile.current_role or ''}. Headline: {profile.headline or ''}. Summary: {profile.summary or ''}. Skills: {skills_str}."
    profile.embedding = get_embedding(embed_text)

    db.commit()
    db.refresh(profile)
    return profile
