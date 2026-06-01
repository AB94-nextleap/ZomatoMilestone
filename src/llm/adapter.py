"""LLM adapter abstraction and Groq implementation."""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from typing import Any
from urllib import error, request

from src.config.loader import get_settings


class LLMAdapter(ABC):
    @abstractmethod
    def complete(self, messages: list[dict[str, str]]) -> str:
        """Return raw completion text."""


class GroqLLMAdapter(LLMAdapter):
    """Groq chat-completions adapter using standard library HTTP client."""

    endpoint = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        temperature: float = 0.2,
        timeout_seconds: int = 45,
    ) -> None:
        settings = get_settings()
        self.api_key = api_key or os.getenv("GROQ_API_KEY") or os.getenv("LLM_API_KEY")
        self.model = model or str(settings.get("llm_model", "llama-3.3-70b-versatile"))
        self.temperature = temperature
        self.timeout_seconds = timeout_seconds
        if not self.api_key:
            raise ValueError(
                "Missing GROQ_API_KEY or LLM_API_KEY. Set it in environment before running Phase 4."
            )

    def _payload(self, messages: list[dict[str, str]]) -> dict[str, Any]:
        return {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "response_format": {"type": "json_object"},
        }

    def complete(self, messages: list[dict[str, str]]) -> str:
        body = json.dumps(self._payload(messages)).encode("utf-8")
        req = request.Request(
            self.endpoint,
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Groq HTTP error {exc.code}: {detail}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"Groq request failed: {exc}") from exc

        try:
            return payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("Groq response missing choices/message/content") from exc
