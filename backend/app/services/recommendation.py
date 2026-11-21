from typing import List, Dict, Any, Tuple
from app.models.models import Job, CandidateProfile, UserPreference
from app.services.embeddings import cosine_similarity

def calculate_skill_overlap(candidate_skills: List[str], job_skills: List[str]) -> Tuple[float, List[str], List[str]]:
    """Calculates skill match percentage, matching skills list, and missing skills list."""
    cand_norm = {s.strip().lower(): s.strip() for s in (candidate_skills or []) if s.strip()}
    job_norm = {s.strip().lower(): s.strip() for s in (job_skills or []) if s.strip()}

    if not job_norm:
        # If job has no explicit tagged skills, assume neutral 70% match
        return 70.0, list(cand_norm.values())[:3], []

    matched = []
    missing = []

    for j_lower, orig in job_norm.items():
        # Exact match or substring containment (e.g. "React" in "React.js")
        if j_lower in cand_norm or any(j_lower in c or c in j_lower for c in cand_norm):
            matched.append(orig)
        else:
            missing.append(orig)

    score = (len(matched) / len(job_norm)) * 100.0
    return round(score, 1), matched, missing

def calculate_role_alignment(candidate_role: str, desired_roles: List[str], job_title: str) -> float:
    """Calculates how well candidate roles align with job title."""
    title_lower = job_title.lower()
    check_roles = [candidate_role] if candidate_role else []
    if desired_roles:
        check_roles.extend(desired_roles)

    if not check_roles:
        return 50.0

    for role in check_roles:
        if not role:
            continue
        r_lower = role.lower()
        if r_lower in title_lower or title_lower in r_lower:
            return 100.0
        # Check token intersection
        r_tokens = set(re.findall(r"\w+", r_lower))
        t_tokens = set(re.findall(r"\w+", title_lower))
        if r_tokens and t_tokens:
            common = r_tokens.intersection(t_tokens)
            if common:
                return 80.0
    return 30.0

import re

def calculate_location_alignment(candidate_loc: str, preferred_locs: List[str], remote_only: bool, job: Job) -> float:
    """Calculates location alignment."""
    if job.remote_policy == "REMOTE":
        return 100.0
    if remote_only and job.remote_policy != "REMOTE":
        return 10.0

    all_locs = [candidate_loc] if candidate_loc else []
    if preferred_locs:
        all_locs.extend(preferred_locs)

    if not all_locs:
        return 70.0

    job_loc_lower = (job.location or "").lower()
    for loc in all_locs:
        if not loc:
            continue
        loc_lower = loc.lower()
        if loc_lower in job_loc_lower or job_loc_lower in loc_lower:
            return 100.0
        # City/country match
        parts = [p.strip() for p in loc_lower.split(',')]
        if any(p in job_loc_lower for p in parts if len(p) > 2):
            return 85.0

    if job.remote_policy == "HYBRID":
        return 60.0

    return 20.0

def calculate_preference_alignment(pref: UserPreference, job: Job) -> float:
    """Calculates compensation and preference match."""
    score = 100.0
    if not pref:
        return 75.0

    # Salary check
    if pref.min_salary and job.max_salary:
        if job.max_salary < pref.min_salary:
            score -= 40.0
        elif job.min_salary and job.min_salary >= pref.min_salary:
            score += 0.0

    if pref.remote_only and job.remote_policy != "REMOTE":
        score -= 50.0

    return max(0.0, min(100.0, score))

def score_job_for_candidate(
    job: Job,
    profile: CandidateProfile,
    preference: UserPreference = None
) -> Dict[str, Any]:
    """
    Deterministically computes match score and explainable breakdown.
    Never hallucinates or uses non-deterministic LLM scoring.
    """
    # 1. Skill Overlap (Weight 0.35)
    job_skill_names = [s.skill_name for s in (job.skills or [])]
    candidate_skills = profile.skills if profile and profile.skills else []
    skill_score, matching_skills, missing_skills = calculate_skill_overlap(candidate_skills, job_skill_names)

    # 2. Semantic Vector Similarity (Weight 0.30)
    semantic_score = 50.0
    if profile and profile.embedding and job.embedding:
        sim = cosine_similarity(profile.embedding, job.embedding)
        semantic_score = round(sim * 100.0, 1)

    # 3. Role Alignment (Weight 0.15)
    desired_roles = preference.desired_roles if preference and preference.desired_roles else []
    current_role = profile.current_role if profile else ""
    role_score = calculate_role_alignment(current_role, desired_roles, job.title)

    # 4. Location Alignment (Weight 0.10)
    cand_loc = profile.location if profile else ""
    pref_locs = preference.preferred_locations if preference and preference.preferred_locations else []
    remote_only = preference.remote_only if preference else False
    location_score = calculate_location_alignment(cand_loc, pref_locs, remote_only, job)

    # 5. Preference Alignment (Weight 0.10)
    pref_score = calculate_preference_alignment(preference, job)

    # Composite weighted score
    composite = (
        0.35 * skill_score +
        0.30 * semantic_score +
        0.15 * role_score +
        0.10 * location_score +
        0.10 * pref_score
    )
    final_score = round(max(0.0, min(100.0, composite)), 1)

    return {
        "match_score": final_score,
        "score_breakdown": {
            "skill_overlap_score": skill_score,
            "semantic_score": semantic_score,
            "role_score": role_score,
            "location_score": location_score,
            "preference_score": pref_score
        },
        "matching_skills": matching_skills,
        "missing_skills": missing_skills
    }
