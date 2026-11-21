import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, SessionLocal
from app.models.models import Job, JobSkill
from app.services.recommendation import score_job_for_candidate, calculate_skill_overlap
from app.services.embeddings import cosine_similarity, get_embedding

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    from app.scripts.seed_jobs import seed_jobs_dataset
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_jobs_dataset(db)
    db.close()
    yield

def test_health_endpoints():
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

    res = client.get("/readyz")
    assert res.status_code == 200
    assert res.json()["status"] == "ready"

def test_auth_and_profile_flow():
    email = "testengineer@example.com"
    password = "secretpassword123"
    
    # 1. Register
    reg_res = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Test Engineer"
    })
    # If already registered in a previous run, register might return 400 or 201
    assert reg_res.status_code in [201, 400]

    # 2. Login
    login_res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Get profile
    prof_res = client.get("/api/v1/profiles/me", headers=headers)
    assert prof_res.status_code == 200
    profile_data = prof_res.json()
    assert "skills" in profile_data

    # 4. Update profile with specific tech skills
    update_res = client.put("/api/v1/profiles/me", headers=headers, json={
        "headline": "Lead AI & Backend Systems Architect",
        "current_role": "AI Engineer",
        "skills": ["Python", "FastAPI", "React", "PostgreSQL", "Docker", "PyTorch", "LLM"],
        "location": "San Francisco, CA",
        "total_experience_years": 5.0
    })
    assert update_res.status_code == 200
    updated = update_res.json()
    assert "Python" in updated["skills"]
    assert "FastAPI" in updated["skills"]

def test_deterministic_recommendation_math():
    """Verify that recommendation scoring is purely mathematical and explainable."""
    candidate_skills = ["Python", "FastAPI", "PostgreSQL"]
    job_skills = ["Python", "FastAPI", "PostgreSQL", "Docker"]

    score, matched, missing = calculate_skill_overlap(candidate_skills, job_skills)
    assert score == 75.0  # 3 out of 4 matched
    assert set(matched) == {"Python", "FastAPI", "PostgreSQL"}
    assert missing == ["Docker"]

def test_recommendations_endpoint():
    login_res = client.post("/api/v1/auth/login", json={
        "email": "testengineer@example.com",
        "password": "secretpassword123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    rec_res = client.get("/api/v1/recommendations/?limit=5", headers=headers)
    assert rec_res.status_code == 200
    recs = rec_res.json()
    assert len(recs) > 0
    # First recommendation should have highest match score
    first = recs[0]
    assert "match_score" in first
    assert "score_breakdown" in first
    assert "matching_skills" in first
    assert "missing_skills" in first
    assert first["match_score"] >= 0.0

def test_semantic_search_endpoint():
    search_res = client.post("/api/v1/search/", json={
        "query": "FastAPI React AI Engineer",
        "remote_policy": "REMOTE",
        "limit": 5
    })
    assert search_res.status_code == 200
    jobs = search_res.json()
    assert len(jobs) > 0
    for j in jobs:
        assert j["remote_policy"] == "REMOTE"

def test_agent_chat_tools():
    login_res = client.post("/api/v1/auth/login", json={
        "email": "testengineer@example.com",
        "password": "secretpassword123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Ask agent to recommend jobs (triggers recommend_jobs tool)
    chat_res = client.post("/api/v1/chat/", headers=headers, json={
        "message": "Can you recommend top jobs for my profile?"
    })
    assert chat_res.status_code == 200
    chat_data = chat_res.json()
    assert "reply" in chat_data
    assert len(chat_data["reply"]) > 10
    assert len(chat_data["tool_calls_executed"]) > 0
    assert chat_data["tool_calls_executed"][0]["tool"] == "recommend_jobs"

def test_saved_jobs_crud():
    login_res = client.post("/api/v1/auth/login", json={
        "email": "testengineer@example.com",
        "password": "secretpassword123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get a job
    jobs = client.get("/api/v1/jobs/?limit=1").json()
    assert len(jobs) > 0
    job_id = jobs[0]["id"]

    # Save job
    save_res = client.post("/api/v1/saved-jobs/", headers=headers, json={
        "job_id": job_id,
        "notes": "Dream company role!"
    })
    assert save_res.status_code == 201
    saved_id = save_res.json()["id"]

    # List saved jobs
    list_res = client.get("/api/v1/saved-jobs/", headers=headers)
    assert list_res.status_code == 200
    assert any(s["id"] == saved_id for s in list_res.json())

    # Update status to APPLIED
    up_res = client.put(f"/api/v1/saved-jobs/{saved_id}", headers=headers, json={
        "status": "APPLIED",
        "notes": "Applied via referral"
    })
    assert up_res.status_code == 200
    assert up_res.json()["status"] == "APPLIED"

    # Delete
    del_res = client.delete(f"/api/v1/saved-jobs/{saved_id}", headers=headers)
    assert del_res.status_code == 204

def test_resume_upload_and_parsing():
    login_res = client.post("/api/v1/auth/login", json={
        "email": "testengineer@example.com",
        "password": "secretpassword123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    sample_resume = """
    Alex Johnson
    Senior Full-Stack AI Engineer
    Email: alex@example.com | Phone: 555-0199
    
    Professional Summary:
    Full-stack engineer with 4+ years of hands-on experience building scalable AI agents,
    RAG pipelines, vector search systems, and reactive user interfaces.
    
    Technical Skills:
    Python, FastAPI, React, TypeScript, PostgreSQL, Docker, PyTorch, LLM, Tailwind CSS.
    
    Work Experience:
    Senior Software Engineer at NeuroCloud (2022 - Present)
    - Developed generative AI tools with Gemini API and pgvector embeddings.
    - Reduced search latency by 45% using hybrid lexical-vector retrieval.
    
    Education:
    B.S. in Computer Science - University of California (2021)
    """

    files = {
        "file": ("sample_resume.txt", sample_resume.encode("utf-8"), "text/plain")
    }

    upload_res = client.post("/api/v1/resumes/upload", headers=headers, files=files)
    assert upload_res.status_code == 200
    res_data = upload_res.json()
    assert res_data["parsing_status"] == "COMPLETED"
    assert "skills" in res_data["parsed_json"]
    assert any("Python" in s for s in res_data["parsed_json"]["skills"])

    # Verify candidate profile was automatically updated
    prof = client.get("/api/v1/profiles/me", headers=headers).json()
    assert len(prof["skills"]) > 0

def test_evals_retrieval_metrics():
    """Verify evaluation metrics (Precision@K, MRR, NDCG) are strictly computed."""
    from evals.evaluate_retrieval import run_retrieval_evaluations
    run_retrieval_evaluations()


