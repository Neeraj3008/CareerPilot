from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Auth Schemas ---
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- Profile Schemas ---
class EducationItem(BaseModel):
    degree: str
    institution: str
    year: Optional[str] = None

class ExperienceItem(BaseModel):
    role: str
    company: str
    duration: Optional[str] = None
    description: Optional[str] = None

class ProjectItem(BaseModel):
    title: str
    description: Optional[str] = None
    technologies: List[str] = []

class CandidateProfileUpdate(BaseModel):
    headline: Optional[str] = None
    summary: Optional[str] = None
    total_experience_years: Optional[float] = None
    current_role: Optional[str] = None
    skills: Optional[List[str]] = None
    location: Optional[str] = None
    education: Optional[List[Dict[str, Any]]] = None
    experience: Optional[List[Dict[str, Any]]] = None
    projects: Optional[List[Dict[str, Any]]] = None

class CandidateProfileResponse(BaseModel):
    id: str
    user_id: str
    headline: Optional[str] = None
    summary: Optional[str] = None
    total_experience_years: float = 0.0
    current_role: Optional[str] = None
    skills: List[str] = []
    location: Optional[str] = None
    education: List[Dict[str, Any]] = []
    experience: List[Dict[str, Any]] = []
    projects: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Resume Schemas ---
class ResumeResponse(BaseModel):
    id: str
    user_id: str
    file_name: str
    file_type: str
    parsing_status: str
    parsed_json: Dict[str, Any] = {}
    created_at: datetime

    class Config:
        from_attributes = True

# --- Job Schemas ---
class JobSkillResponse(BaseModel):
    id: str
    skill_name: str
    is_required: bool
    importance_weight: float

    class Config:
        from_attributes = True

class JobCreate(BaseModel):
    title: str
    company: str
    description: str
    location: str
    remote_policy: str = "REMOTE"
    job_type: str = "FULL_TIME"
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    currency: str = "USD"
    experience_level: str = "MID"
    skills: List[str] = []
    source_url: Optional[str] = None

class JobResponse(BaseModel):
    id: str
    title: str
    company: str
    description: str
    location: str
    remote_policy: str
    job_type: str
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    currency: str = "USD"
    experience_level: str
    skills: List[JobSkillResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True

class JobSearchQuery(BaseModel):
    query: Optional[str] = None
    location: Optional[str] = None
    remote_policy: Optional[str] = None
    experience_level: Optional[str] = None
    min_salary: Optional[float] = None
    limit: int = 20

# --- Recommendation Schemas ---
class ScoreBreakdown(BaseModel):
    skill_overlap_score: float
    semantic_score: float
    role_score: float
    location_score: float
    preference_score: float

class RecommendationResponse(BaseModel):
    id: str
    job: JobResponse
    match_score: float
    score_breakdown: Dict[str, float]
    matching_skills: List[str]
    missing_skills: List[str]
    generated_at: datetime

    class Config:
        from_attributes = True

# --- Preference Schemas ---
class UserPreferenceUpdate(BaseModel):
    desired_roles: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    remote_only: Optional[bool] = None
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    preferred_industries: Optional[List[str]] = None

class UserPreferenceResponse(BaseModel):
    id: str
    user_id: str
    desired_roles: List[str] = []
    preferred_locations: List[str] = []
    remote_only: bool = False
    min_salary: Optional[float] = None
    max_salary: Optional[float] = None
    preferred_industries: List[str] = []

    class Config:
        from_attributes = True

# --- Saved Job Schemas ---
class SavedJobCreate(BaseModel):
    job_id: str
    notes: Optional[str] = None
    status: str = "SAVED"

class SavedJobUpdate(BaseModel):
    notes: Optional[str] = None
    status: Optional[str] = None

class SavedJobResponse(BaseModel):
    id: str
    user_id: str
    job_id: str
    status: str
    notes: Optional[str] = None
    job: JobResponse
    created_at: datetime

    class Config:
        from_attributes = True

# --- Chat Schemas ---
class ChatMessageCreate(BaseModel):
    conversation_id: Optional[str] = None
    message: str

class MessageResponse(BaseModel):
    id: str
    role: str
    content: Optional[str] = None
    tool_calls: Optional[Any] = None
    name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: str
    title: str
    messages: List[MessageResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    tool_calls_executed: List[Dict[str, Any]] = []
