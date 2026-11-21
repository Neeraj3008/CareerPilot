from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_active_user
from app.models.models import User, UserPreference
from app.schemas.schemas import UserPreferenceResponse, UserPreferenceUpdate

router = APIRouter()

@router.get("/", response_model=UserPreferenceResponse)
def get_preferences(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not pref:
        pref = UserPreference(
            user_id=current_user.id,
            desired_roles=[],
            preferred_locations=[],
            remote_only=False
        )
        db.add(pref)
        db.commit()
        db.refresh(pref)
    return pref

@router.put("/", response_model=UserPreferenceResponse)
def update_preferences(
    pref_in: UserPreferenceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not pref:
        pref = UserPreference(user_id=current_user.id)
        db.add(pref)

    update_data = pref_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(pref, field, val)

    db.commit()
    db.refresh(pref)
    return pref
