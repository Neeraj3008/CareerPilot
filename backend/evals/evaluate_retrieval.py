import json
import math
import os
import sys
from typing import List, Dict, Any

# Ensure backend path is loaded
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal, init_db
from app.models.models import Job
from app.services.embeddings import get_embedding, cosine_similarity
from app.services.llm import parse_resume_with_gemini
from app.schemas.schemas import CandidateProfileResponse

def dcg_at_k(relevance_scores: List[int], k: int) -> float:
    relevance_scores = relevance_scores[:k]
    return sum((2**rel - 1) / math.log2(idx + 2) for idx, rel in enumerate(relevance_scores))

def ndcg_at_k(relevance_scores: List[int], k: int) -> float:
    dcg = dcg_at_k(relevance_scores, k)
    ideal_scores = sorted(relevance_scores, reverse=True)
    idcg = dcg_at_k(ideal_scores, k)
    if idcg == 0.0:
        return 0.0
    return dcg / idcg

def run_retrieval_evaluations(k_values=[1, 3, 5]):
    db = SessionLocal()
    try:
        jobs = db.query(Job).filter(Job.is_active == True).all()
        if not jobs:
            print("No jobs found in database to evaluate.")
            return

        dataset_path = os.path.join(os.path.dirname(__file__), 'benchmark_dataset.json')
        with open(dataset_path, 'r') as f:
            data = json.load(f)
        queries = data['queries']

        print(f"\n=======================================================")
        print(f"      CAREERPILOT RETRIEVAL EVALUATION BENCHMARK       ")
        print(f"=======================================================\n")
        print(f"Total Benchmark Queries: {len(queries)}")
        print(f"Total Database Job Corpus: {len(jobs)}")

        precisions = {k: [] for k in k_values}
        recalls = {k: [] for k in k_values}
        ndcgs = {k: [] for k in k_values}
        reciprocal_ranks = []

        for q in queries:
            query_text = q['query']
            relevant_titles = set(q['relevant_titles'])
            query_vec = get_embedding(query_text)

            # Score each job
            scored = []
            for j in jobs:
                sim = cosine_similarity(query_vec, j.embedding) if j.embedding else 0.0
                # keyword match boost
                boost = 0.25 if any(kw in j.title.lower() for kw in query_text.lower().split() if len(kw) > 3) else 0.0
                scored.append((sim + boost, j.title))

            scored.sort(key=lambda x: x[0], reverse=True)
            retrieved_titles = [s[1] for s in scored]

            # Calculate MRR
            rr = 0.0
            for rank_idx, title in enumerate(retrieved_titles, 1):
                if title in relevant_titles:
                    rr = 1.0 / rank_idx
                    break
            reciprocal_ranks.append(rr)

            # Calculate P@K, R@K, NDCG@K
            for k in k_values:
                top_k = retrieved_titles[:k]
                rel_in_top_k = [1 if t in relevant_titles else 0 for t in top_k]
                hit_count = sum(rel_in_top_k)

                p_k = hit_count / k
                r_k = hit_count / len(relevant_titles) if len(relevant_titles) > 0 else 0.0
                n_k = ndcg_at_k(rel_in_top_k, k)

                precisions[k].append(p_k)
                recalls[k].append(r_k)
                ndcgs[k].append(n_k)

        # Output Summary Table
        mrr = sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0
        print("\n--- Retrieval Metrics ---")
        for k in k_values:
            mean_p = sum(precisions[k]) / len(precisions[k])
            mean_r = sum(recalls[k]) / len(recalls[k])
            mean_ndcg = sum(ndcgs[k]) / len(ndcgs[k])
            print(f"K = {k}:  Precision@{k}: {mean_p:.3f} | Recall@{k}: {mean_r:.3f} | NDCG@{k}: {mean_ndcg:.3f}")
        print(f"Mean Reciprocal Rank (MRR): {mrr:.3f}")

        # Structured Output Schema Validity Test
        print("\n--- Structured-Output Schema Validity Test ---")
        sample_resume = """
        Jordan Lee - Staff AI Platform Architect
        Experience: 6 years building distributed agents, RAG, and vector pipelines.
        Skills: Python, FastAPI, React, Docker, Kubernetes, PostgreSQL, pgvector.
        Education: M.S. Computer Engineering, Stanford University 2019.
        """
        extracted = parse_resume_with_gemini(sample_resume)
        
        # Verify required keys and types
        required_keys = ["headline", "summary", "total_experience_years", "current_role", "skills", "education", "experience"]
        valid_keys = all(k in extracted for k in required_keys)
        valid_skills = isinstance(extracted.get("skills"), list) and len(extracted["skills"]) > 0
        valid_years = isinstance(extracted.get("total_experience_years"), (int, float))

        validity_score = 100.0 if (valid_keys and valid_skills and valid_years) else 0.0
        print(f"Schema Conformance: {validity_score:.1f}%")
        print(f"Extracted Skills Count: {len(extracted.get('skills', []))}")
        print(f"Extracted Role: '{extracted.get('current_role')}'")
        print(f"=======================================================\n")

        assert mrr > 0.6, "MRR benchmark failed"
        assert validity_score == 100.0, "Schema validity check failed"
        print("✅ ALL BENCHMARK & SCHEMA EVALUATION CHECKS PASSED.")

    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    run_retrieval_evaluations()
