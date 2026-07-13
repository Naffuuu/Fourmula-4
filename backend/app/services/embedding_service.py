"""Semantic search over the seeded rulebook for Mission 6.

Uses OpenAI embeddings + cosine similarity when `OPENAI_API_KEY` is set.
Otherwise falls back to a TF-IDF vector space model (scikit-learn), which
runs entirely offline/on-CPU — appropriate for a hackathon demo where venue
wifi to an embeddings API isn't guaranteed. Both paths return the same shape
so the fact-checker endpoint doesn't need to know which one ran.
"""

import numpy as np
import httpx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import get_settings

settings = get_settings()


async def embed_text_openai(texts: list[str]) -> list[list[float]]:
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            "https://api.openai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            json={"model": "text-embedding-3-small", "input": texts},
        )
        resp.raise_for_status()
        data = resp.json()["data"]
        return [row["embedding"] for row in data]


class RulebookIndex:
    """In-memory TF-IDF index rebuilt from whatever's in `rulebook_entries`.
    Rebuilding on each cold start is fine at rulebook scale (dozens to low
    hundreds of rules); a real production index would cache this."""

    def __init__(self):
        self._vectorizer: TfidfVectorizer | None = None
        self._matrix = None
        self._rules: list[dict] = []

    def build(self, rules: list[dict]):
        self._rules = rules
        self._vectorizer = TfidfVectorizer(stop_words="english")
        self._matrix = self._vectorizer.fit_transform([r["rule_text"] for r in rules])

    def best_match(self, claim: str) -> tuple[dict, float] | None:
        if not self._rules or self._vectorizer is None:
            return None
        claim_vec = self._vectorizer.transform([claim])
        scores = cosine_similarity(claim_vec, self._matrix)[0]
        best_idx = int(np.argmax(scores))
        return self._rules[best_idx], float(scores[best_idx])


async def best_match_openai(claim: str, rules: list[dict]) -> tuple[dict, float] | None:
    if not rules:
        return None
    claim_embedding, *rule_embeddings = await embed_text_openai([claim] + [r["rule_text"] for r in rules])
    claim_vec = np.array(claim_embedding).reshape(1, -1)
    rule_matrix = np.array(rule_embeddings)
    scores = cosine_similarity(claim_vec, rule_matrix)[0]
    best_idx = int(np.argmax(scores))
    return rules[best_idx], float(scores[best_idx])
