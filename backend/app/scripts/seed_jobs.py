from sqlalchemy.orm import Session
from app.models.models import Job, JobSkill
from app.services.embeddings import get_embedding

INITIAL_JOBS = [
    {
        "title": "Senior AI / Machine Learning Engineer",
        "company": "Anthropic AI Labs",
        "location": "San Francisco, CA",
        "remote_policy": "HYBRID",
        "job_type": "FULL_TIME",
        "min_salary": 180000,
        "max_salary": 240000,
        "currency": "USD",
        "experience_level": "SENIOR",
        "description": "Lead the development of next-generation LLM agent architectures, RAG pipelines, and high-throughput vector retrieval systems. Build scalable inference microservices using FastAPI, PyTorch, and pgvector.",
        "skills": ["Python", "PyTorch", "LLM", "RAG", "FastAPI", "Vector Databases", "Docker"]
    },
    {
        "title": "Full-Stack AI Engineer",
        "company": "Nexus Cognitive",
        "location": "Remote",
        "remote_policy": "REMOTE",
        "job_type": "FULL_TIME",
        "min_salary": 140000,
        "max_salary": 190000,
        "currency": "USD",
        "experience_level": "MID",
        "description": "Design and build user-facing AI applications using React, TypeScript, Tailwind CSS on the frontend and FastAPI, PostgreSQL, and Gemini / OpenAI APIs on the backend.",
        "skills": ["React", "TypeScript", "Tailwind CSS", "Python", "FastAPI", "PostgreSQL", "Gemini"]
    },
    {
        "title": "Backend Python Platform Engineer",
        "company": "ScaleStream Cloud",
        "location": "New York, NY",
        "remote_policy": "HYBRID",
        "job_type": "FULL_TIME",
        "min_salary": 150000,
        "max_salary": 200000,
        "currency": "USD",
        "experience_level": "SENIOR",
        "description": "Architect high-reliability distributed REST APIs and event-driven data ingestion microservices. Optimize SQL queries and PostgreSQL indexes.",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Redis", "SQLAlchemy", "CI/CD"]
    },
    {
        "title": "Frontend React / TypeScript Architect",
        "company": "Vivid Interface Systems",
        "location": "Remote",
        "remote_policy": "REMOTE",
        "job_type": "FULL_TIME",
        "min_salary": 135000,
        "max_salary": 175000,
        "currency": "USD",
        "experience_level": "SENIOR",
        "description": "Build high-performance, accessible enterprise web applications with React 18, Vite, TypeScript, and modern component libraries. Optimize rendering and client-side state.",
        "skills": ["React", "TypeScript", "JavaScript", "HTML", "CSS", "Tailwind CSS", "Vite"]
    },
    {
        "title": "DevOps & Cloud Infrastructure Engineer",
        "company": "Apex Infrastructure",
        "location": "Austin, TX",
        "remote_policy": "REMOTE",
        "job_type": "FULL_TIME",
        "min_salary": 145000,
        "max_salary": 185000,
        "currency": "USD",
        "experience_level": "MID",
        "description": "Automate containerized deployments with Docker, Kubernetes, GitHub Actions, and Render/AWS. Maintain observability, Prometheus monitoring, and database backup routines.",
        "skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "PostgreSQL", "Python"]
    },
    {
        "title": "Data Scientist & NLP Specialist",
        "company": "Quantix Intelligence",
        "location": "Boston, MA",
        "remote_policy": "HYBRID",
        "job_type": "FULL_TIME",
        "min_salary": 130000,
        "max_salary": 170000,
        "currency": "USD",
        "experience_level": "MID",
        "description": "Extract structured insights and semantic representations from unstructured textual documents and resumes using NLP models, sentence transformers, and semantic embeddings.",
        "skills": ["Python", "NLP", "Pandas", "Scikit-Learn", "Machine Learning", "SQL", "PyTorch"]
    },
    {
        "title": "Junior Python / FastAPI Developer",
        "company": "Seedling Technologies",
        "location": "Remote",
        "remote_policy": "REMOTE",
        "job_type": "FULL_TIME",
        "min_salary": 85000,
        "max_salary": 115000,
        "currency": "USD",
        "experience_level": "ENTRY",
        "description": "Great opportunity for early-career developers with strong foundational Python skills. Work on backend REST endpoints, write automated pytest unit tests, and integrate 3rd party APIs.",
        "skills": ["Python", "FastAPI", "Git", "SQL", "Docker", "REST API"]
    },
    {
        "title": "Staff Search & Recommendation Systems Engineer",
        "company": "Hyperion Commerce",
        "location": "Seattle, WA",
        "remote_policy": "HYBRID",
        "job_type": "FULL_TIME",
        "min_salary": 200000,
        "max_salary": 260000,
        "currency": "USD",
        "experience_level": "LEAD",
        "description": "Design and scale deterministic and multi-stage recommendation engines, hybrid lexical/vector search, and personalized candidate matching algorithms across millions of records.",
        "skills": ["Python", "Vector Databases", "PostgreSQL", "Machine Learning", "System Design", "Algorithms"]
    }
]

def seed_jobs_dataset(db: Session):
    existing_count = db.query(Job).count()
    if existing_count > 0:
        return existing_count

    print("Seeding initial jobs dataset...")
    for item in INITIAL_JOBS:
        job_data = dict(item)
        skills = job_data.pop("skills")
        skills_text = ", ".join(skills)
        embed_text = f"Title: {job_data['title']}. Company: {job_data['company']}. Location: {job_data['location']}. Skills: {skills_text}. Description: {job_data['description']}"
        job_emb = get_embedding(embed_text)

        job = Job(
            **job_data,
            embedding=job_emb
        )
        db.add(job)
        db.flush()

        for s in skills:
            js = JobSkill(job_id=job.id, skill_name=s, is_required=True)
            db.add(js)

    db.commit()
    print(f"Successfully seeded {len(INITIAL_JOBS)} jobs.")
    return len(INITIAL_JOBS)
