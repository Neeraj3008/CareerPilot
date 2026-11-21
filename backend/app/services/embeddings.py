import math
import hashlib
import httpx
from typing import List
from app.core.config import settings

def _deterministic_mock_embedding(text: str, dim: int = 768) -> List[float]:
    """Generates a stable, normalized 768-dim vector for testing/offline without API keys."""
    words = text.lower().split()
    vec = [0.0] * dim
    if not words:
        return vec
    for word in words:
        h = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
        idx = h % dim
        vec[idx] += 1.0
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec

def get_embedding(text: str) -> List[float]:
    """
    Returns a 768-dimensional embedding vector for the input text.
    Uses Gemini text-embedding-004 if GEMINI_API_KEY is configured,
    otherwise uses deterministic local hashing.
    """
    if not text or not text.strip():
        return [0.0] * 768

    if settings.GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_EMBEDDING_MODEL}:embedContent?key={settings.GEMINI_API_KEY}"
            payload = {
                "model": f"models/{settings.GEMINI_EMBEDDING_MODEL}",
                "content": {
                    "parts": [{"text": text[:2048]}]
                }
            }
            with httpx.Client(timeout=10.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    values = data.get("embedding", {}).get("values", [])
                    if len(values) == 768:
                        return values
                    elif len(values) > 0:
                        # Pad or slice to 768
                        if len(values) < 768:
                            values = values + [0.0] * (768 - len(values))
                        return values[:768]
        except Exception as e:
            print(f"Warning: Gemini embedding failed, falling back to local: {e}")

    return _deterministic_mock_embedding(text, 768)

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculates cosine similarity between two 1D vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return max(0.0, min(1.0, dot / (norm_a * norm_b)))
