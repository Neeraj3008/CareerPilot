import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.models import Job, CandidateProfile, UserPreference, SavedJob, Conversation, Message, User
from app.services.recommendation import score_job_for_candidate
from app.services.embeddings import get_embedding, cosine_similarity
from app.core.config import settings
import httpx

AGENT_TOOLS_SCHEMA = [
    {
        "name": "search_jobs",
        "description": "Search for active job listings using query keywords, location, remote status, or salary.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Keywords like 'FastAPI', 'Frontend', 'AI Engineer'"},
                "location": {"type": "string", "description": "City or Country"},
                "remote_only": {"type": "boolean", "description": "Filter only remote positions"},
                "min_salary": {"type": "number", "description": "Minimum acceptable annual salary"}
            }
        }
    },
    {
        "name": "get_job_details",
        "description": "Fetch detailed description, required skills, and compensation for a specific job ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "job_id": {"type": "string", "description": "UUID of the job"}
            },
            "required": ["job_id"]
        }
    },
    {
        "name": "get_user_profile",
        "description": "Fetch the current candidate's profile, including their extracted skills, experience, and current role.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "update_preferences",
        "description": "Update the candidate's career search preferences.",
        "parameters": {
            "type": "object",
            "properties": {
                "desired_roles": {"type": "array", "items": {"type": "string"}},
                "preferred_locations": {"type": "array", "items": {"type": "string"}},
                "remote_only": {"type": "boolean"},
                "min_salary": {"type": "number"}
            }
        }
    },
    {
        "name": "recommend_jobs",
        "description": "Calculate and retrieve the top personalized job recommendations for the user based on deterministic skill matching and semantic similarity.",
        "parameters": {
            "type": "object",
            "properties": {
                "top_k": {"type": "integer", "description": "Number of recommendations to return, default 5"}
            }
        }
    },
    {
        "name": "save_job",
        "description": "Save a job to the user's tracker for later application.",
        "parameters": {
            "type": "object",
            "properties": {
                "job_id": {"type": "string", "description": "UUID of the job to save"},
                "notes": {"type": "string", "description": "Optional notes"}
            },
            "required": ["job_id"]
        }
    }
]

class ToolExecutor:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user

    def search_jobs(self, query: str = None, location: str = None, remote_only: bool = False, min_salary: float = None, limit: int = 5) -> List[Dict[str, Any]]:
        q = self.db.query(Job).filter(Job.is_active == True)
        if remote_only:
            q = q.filter(Job.remote_policy == "REMOTE")
        if min_salary:
            q = q.filter(Job.max_salary >= min_salary)
        if location:
            q = q.filter(Job.location.ilike(f"%{location}%"))
        
        jobs = q.all()
        
        # If query specified, rank by semantic/keyword relevance
        if query and jobs:
            query_emb = get_embedding(query)
            scored = []
            for j in jobs:
                sim = cosine_similarity(query_emb, j.embedding) if j.embedding else 0.0
                # keyword boost
                kw_boost = 0.2 if (query.lower() in j.title.lower() or query.lower() in j.description.lower()) else 0.0
                scored.append((sim + kw_boost, j))
            scored.sort(key=lambda x: x[0], reverse=True)
            jobs = [j for _, j in scored]

        return [
            {
                "id": j.id,
                "title": j.title,
                "company": j.company,
                "location": j.location,
                "remote_policy": j.remote_policy,
                "salary": f"${int(j.min_salary):,} - ${int(j.max_salary):,}" if j.min_salary and j.max_salary else "Competitive",
                "skills": [s.skill_name for s in (j.skills or [])]
            }
            for j in jobs[:limit]
        ]

    def get_job_details(self, job_id: str) -> Dict[str, Any]:
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return {"error": f"Job with ID '{job_id}' not found."}
        return {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "remote_policy": job.remote_policy,
            "job_type": job.job_type,
            "salary": f"${int(job.min_salary):,} - ${int(job.max_salary):,}" if job.min_salary and job.max_salary else "Competitive",
            "description": job.description,
            "skills": [s.skill_name for s in (job.skills or [])],
            "source_url": job.source_url
        }

    def get_user_profile(self) -> Dict[str, Any]:
        profile = self.db.query(CandidateProfile).filter(CandidateProfile.user_id == self.user.id).first()
        if not profile:
            return {"message": "User has not uploaded a resume or created a profile yet."}
        return {
            "headline": profile.headline,
            "current_role": profile.current_role,
            "skills": profile.skills or [],
            "experience_years": profile.total_experience_years,
            "location": profile.location,
            "summary": profile.summary
        }

    def update_preferences(self, desired_roles: List[str] = None, preferred_locations: List[str] = None, remote_only: bool = None, min_salary: float = None) -> Dict[str, Any]:
        pref = self.db.query(UserPreference).filter(UserPreference.user_id == self.user.id).first()
        if not pref:
            pref = UserPreference(user_id=self.user.id)
            self.db.add(pref)
        
        if desired_roles is not None:
            pref.desired_roles = desired_roles
        if preferred_locations is not None:
            pref.preferred_locations = preferred_locations
        if remote_only is not None:
            pref.remote_only = remote_only
        if min_salary is not None:
            pref.min_salary = min_salary

        self.db.commit()
        return {"status": "success", "message": "Preferences updated successfully."}

    def recommend_jobs(self, top_k: int = 5) -> List[Dict[str, Any]]:
        profile = self.db.query(CandidateProfile).filter(CandidateProfile.user_id == self.user.id).first()
        pref = self.db.query(UserPreference).filter(UserPreference.user_id == self.user.id).first()
        all_jobs = self.db.query(Job).filter(Job.is_active == True).all()

        if not all_jobs:
            return []

        scored_jobs = []
        for j in all_jobs:
            score_data = score_job_for_candidate(j, profile, pref)
            scored_jobs.append({
                "id": j.id,
                "title": j.title,
                "company": j.company,
                "location": j.location,
                "remote_policy": j.remote_policy,
                "salary": f"${int(j.min_salary):,} - ${int(j.max_salary):,}" if j.min_salary and j.max_salary else "Competitive",
                "match_score": score_data["match_score"],
                "matching_skills": score_data["matching_skills"],
                "missing_skills": score_data["missing_skills"]
            })

        scored_jobs.sort(key=lambda x: x["match_score"], reverse=True)
        return scored_jobs[:top_k]

    def save_job(self, job_id: str, notes: str = None) -> Dict[str, Any]:
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return {"error": "Job not found."}
        
        existing = self.db.query(SavedJob).filter(SavedJob.user_id == self.user.id, SavedJob.job_id == job_id).first()
        if existing:
            return {"status": "info", "message": f"Job '{job.title}' at {job.company} is already saved."}

        saved = SavedJob(user_id=self.user.id, job_id=job_id, notes=notes, status="SAVED")
        self.db.add(saved)
        self.db.commit()
        return {"status": "success", "message": f"Saved job '{job.title}' at {job.company} to your tracker."}

    def execute_tool(self, name: str, args: Dict[str, Any]) -> Any:
        if name == "search_jobs":
            return self.search_jobs(**args)
        elif name == "get_job_details":
            return self.get_job_details(**args)
        elif name == "get_user_profile":
            return self.get_user_profile()
        elif name == "update_preferences":
            return self.update_preferences(**args)
        elif name == "recommend_jobs":
            return self.recommend_jobs(**args)
        elif name == "save_job":
            return self.save_job(**args)
        return {"error": f"Tool '{name}' is not recognized."}

def run_agent_turn(db: Session, user: User, conversation_id: str, user_prompt: str) -> Dict[str, Any]:
    """
    Executes an intelligent agent turn:
    1. Loads conversation history
    2. Identifies relevant tools or uses Gemini API with tools declaration
    3. Executes genuine backend tools
    4. Records messages and returns grounded answer
    """
    executor = ToolExecutor(db, user)
    executed_tools = []
    
    # Check for direct intents to execute genuine backend functionality
    prompt_lower = user_prompt.lower()
    
    tool_to_call = None
    tool_args = {}

    if any(k in prompt_lower for k in ["recommend", "match", "best fit", "suggestions"]):
        tool_to_call = "recommend_jobs"
        tool_args = {"top_k": 5}
    elif any(k in prompt_lower for k in ["my profile", "my skills", "what are my skills", "resume details"]):
        tool_to_call = "get_user_profile"
        tool_args = {}
    elif any(k in prompt_lower for k in ["save job", "bookmark job"]):
        # Look for uuid or job in prompt
        all_jobs = db.query(Job).limit(10).all()
        for j in all_jobs:
            if j.title.lower() in prompt_lower or j.id in prompt_lower:
                tool_to_call = "save_job"
                tool_args = {"job_id": j.id}
                break
    elif any(k in prompt_lower for k in ["search", "find", "looking for", "jobs for", "developer", "engineer"]):
        # Extract keywords
        tool_to_call = "search_jobs"
        remote = "remote" in prompt_lower
        tool_args = {"query": user_prompt, "remote_only": remote, "limit": 5}

    tool_result = None
    if tool_to_call:
        tool_result = executor.execute_tool(tool_to_call, tool_args)
        executed_tools.append({
            "tool": tool_to_call,
            "args": tool_args,
            "result": tool_result
        })

    # Generate answer grounded in the executed tool data
    if settings.GEMINI_API_KEY:
        try:
            profile_data = executor.get_user_profile()
            system_context = f"""
            You are CareerPilot, a senior career advisor and technical recruiter.
            The user profile is: {json.dumps(profile_data)}
            If tool execution happened, here is the verified backend data:
            {json.dumps(executed_tools)}

            Rules:
            1. Never fabricate jobs, salaries, or match scores.
            2. Ground your answer in the verified tool results.
            3. Highlight matching skills and suggest actionable steps.
            """
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
            payload = {
                "contents": [
                    {"parts": [{"text": system_context}]},
                    {"parts": [{"text": f"User: {user_prompt}"}]}
                ]
            }
            with httpx.Client(timeout=15.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    reply = data["candidates"][0]["content"]["parts"][0]["text"]
                    return {"reply": reply, "tool_calls_executed": executed_tools}
        except Exception as e:
            print(f"Gemini agent call error, falling back: {e}")

    # Deterministic fallback response synthesis
    if tool_to_call == "recommend_jobs" and tool_result:
        lines = ["Here are your top deterministic job recommendations based on your profile and skills:\n"]
        for idx, rec in enumerate(tool_result, 1):
            matching = ", ".join(rec['matching_skills']) if rec['matching_skills'] else 'Profile overlap'
            lines.append(
                f"{idx}. **{rec['title']}** at **{rec['company']}**\n"
                f"   - Match Score: **{rec['match_score']}%**\n"
                f"   - Location: {rec['location']} ({rec['remote_policy']}) | Salary: {rec['salary']}\n"
                f"   - Matched Skills: {matching}\n"
                f"   - Skills to develop: {', '.join(rec['missing_skills'][:3]) if rec['missing_skills'] else 'None'}\n"
            )
        reply = "\n".join(lines)
    elif tool_to_call == "search_jobs" and tool_result:
        lines = [f"Found {len(tool_result)} matching positions for your query:\n"]
        for idx, job in enumerate(tool_result, 1):
            skills = ", ".join(job['skills']) if job['skills'] else "General"
            lines.append(
                f"{idx}. **{job['title']}** at **{job['company']}**\n"
                f"   - Location: {job['location']} ({job['remote_policy']})\n"
                f"   - Salary: {job['salary']}\n"
                f"   - Skills: {skills}\n"
            )
        reply = "\n".join(lines)
    elif tool_to_call == "get_user_profile" and tool_result:
        skills = ", ".join(tool_result.get('skills', []))
        reply = (
            f"### Your Candidate Profile\n\n"
            f"- **Role:** {tool_result.get('current_role', 'Software Engineer')}\n"
            f"- **Headline:** {tool_result.get('headline', 'N/A')}\n"
            f"- **Experience:** {tool_result.get('experience_years', 0)} years\n"
            f"- **Skills:** {skills}\n"
            f"- **Summary:** {tool_result.get('summary', 'N/A')}\n"
        )
    elif tool_to_call == "save_job" and tool_result:
        reply = tool_result.get("message", "Job status updated.")
    else:
        reply = (
            f"Hello! I am your CareerPilot AI Advisor. I can search jobs, analyze your resume skills, "
            f"calculate deterministic recommendation scores, and update your career preferences. "
            f"Try asking 'What jobs match my profile?', 'Search for remote Python jobs', or 'Show my skills'."
        )

    return {"reply": reply, "tool_calls_executed": executed_tools}
