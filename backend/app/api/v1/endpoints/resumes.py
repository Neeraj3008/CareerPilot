import io
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from pypdf import PdfReader

from app.api.deps import get_db, get_current_active_user
from app.models.models import User, Resume, CandidateProfile
from app.schemas.schemas import ResumeResponse
from app.services.llm import parse_resume_with_gemini
from app.services.embeddings import get_embedding

router = APIRouter()

@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Validate extension
    file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    if file_ext not in ["pdf", "txt"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Currently PDF and TXT resume files are supported."
        )

    content = await file.read()
    raw_text = ""

    if file_ext == "pdf":
        try:
            reader = PdfReader(io.BytesIO(content))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    raw_text += page_text + "\n"
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to read PDF file: {str(e)}"
            )
    else:
        raw_text = content.decode("utf-8", errors="ignore")

    if not raw_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded resume file contains no readable text."
        )

    # Parse resume into structured profile using Gemini (or fallback)
    parsed_data = parse_resume_with_gemini(raw_text)

    # Save Resume record
    resume_record = Resume(
        user_id=current_user.id,
        file_name=file.filename,
        file_type=file_ext.upper(),
        raw_text=raw_text,
        parsed_json=parsed_data,
        parsing_status="COMPLETED"
    )
    db.add(resume_record)

    # Sync parsed information directly into CandidateProfile
    profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.id).first()
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.add(profile)

    if parsed_data.get("headline"):
        profile.headline = parsed_data["headline"]
    if parsed_data.get("summary"):
        profile.summary = parsed_data["summary"]
    if parsed_data.get("total_experience_years") is not None:
        profile.total_experience_years = float(parsed_data["total_experience_years"])
    if parsed_data.get("current_role"):
        profile.current_role = parsed_data["current_role"]
    if parsed_data.get("skills"):
        profile.skills = parsed_data["skills"]
    if parsed_data.get("location"):
        profile.location = parsed_data["location"]
    if parsed_data.get("education"):
        profile.education = parsed_data["education"]
    if parsed_data.get("experience"):
        profile.experience = parsed_data["experience"]
    if parsed_data.get("projects"):
        profile.projects = parsed_data["projects"]

    # Generate and store pgvector dense embedding for semantic matching
    skills_text = ", ".join(profile.skills or [])
    embed_content = f"Title: {profile.current_role or ''}. Summary: {profile.summary or ''}. Skills: {skills_text}."
    profile.embedding = get_embedding(embed_content)

    db.commit()
    db.refresh(resume_record)
    return resume_record

@router.get("/", response_model=List[ResumeResponse])
def get_user_resumes(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    return db.query(Resume).filter(Resume.user_id == current_user.id).order_by(Resume.created_at.desc()).all()
