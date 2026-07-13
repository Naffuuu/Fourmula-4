"""Pluggable LLM provider for Mission 3 (syllabus summarization + RAG
filtering) and Mission 6's confidence phrasing. Talks to OpenAI or Gemini
depending on `LLM_PROVIDER`, and falls back to a deterministic extractive
summarizer if no API key is configured — so the mission still works end to
end on a laptop with no internet during a demo, it's just less clever.
"""

import json
import re

import httpx

from app.core.config import get_settings

settings = get_settings()


class LLMService:
    def __init__(self):
        self.provider = settings.llm_provider
        self.available = bool(settings.openai_api_key) if self.provider == "openai" else bool(settings.gemini_api_key)

    async def complete_json(self, system_prompt: str, user_prompt: str) -> dict:
        """Asks the model for a JSON object and parses it. Falls back to a
        naive extractive summary if no provider key is configured."""
        if not self.available:
            return self._offline_fallback(user_prompt)

        if self.provider == "openai":
            return await self._openai_complete(system_prompt, user_prompt)
        if self.provider == "gemini":
            return await self._gemini_complete(system_prompt, user_prompt)
        return self._offline_fallback(user_prompt)

    async def _openai_complete(self, system_prompt: str, user_prompt: str) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.2,
                },
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            return json.loads(content)

    async def _gemini_complete(self, system_prompt: str, user_prompt: str) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
                params={"key": settings.gemini_api_key},
                json={
                    "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}],
                    "generationConfig": {"response_mime_type": "application/json"},
                },
            )
            resp.raise_for_status()
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)

    def _offline_fallback(self, user_prompt: str) -> dict:
        """Deterministic, dependency-free fallback: splits on sentence
        boundaries / line breaks, keeps the first clause of each as a
        pseudo-bullet. Clearly worse than a real LLM, but keeps the feature
        demoable with zero network access."""
        text = re.search(r"TEXT:\s*(.*)", user_prompt, re.DOTALL)
        raw = text.group(1) if text else user_prompt
        chunks = [c.strip() for c in re.split(r"[.\n]", raw) if len(c.strip()) > 8]
        bullets = chunks[:12]
        return {
            "summary_bullets": bullets,
            "examinable_topics": bullets,
            "dropped_topics": [],
        }


llm_service = LLMService()
