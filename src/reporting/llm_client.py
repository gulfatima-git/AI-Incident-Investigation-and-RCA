"""LLM client abstractions for RCA report generation."""

from __future__ import annotations

import abc
import os
import time
from dataclasses import dataclass

from src.utils.logger import get_logger

from dotenv import load_dotenv

load_dotenv()

logger = get_logger(__name__)


class LLMClient(abc.ABC):
    """Abstract LLM client interface."""

    @abc.abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate text from a prompt."""


@dataclass
class AnthropicClient(LLMClient):
    """Anthropic-powered client.

    Update the default model id here if Anthropic changes the recommended
    Claude Sonnet release; do not assume a fixed public model name forever.
    """

    model: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")
    max_retries: int = 3

    def generate(self, prompt: str) -> str:
        from anthropic import Anthropic

        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = client.messages.create(
                    model=self.model,
                    max_tokens=1200,
                    temperature=0.2,
                    messages=[{"role": "user", "content": prompt}],
                )
                return "".join(block.text for block in response.content if getattr(block, "text", None))
            except Exception as exc:  # retry with backoff, then surface the error
                last_error = exc
                logger.warning("Anthropic request failed on attempt %s/%s: %s", attempt, self.max_retries, exc)
                time.sleep(1.5 * attempt)
        raise RuntimeError("Anthropic generation failed.") from last_error


@dataclass
class OllamaClient(LLMClient):
    """Ollama-powered local client."""

    model: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    max_retries: int = 3

    def generate(self, prompt: str) -> str:
        import ollama

        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = ollama.chat(model=self.model, messages=[{"role": "user", "content": prompt}])
                return response["message"]["content"]
            except Exception as exc:
                last_error = exc
                logger.warning("Ollama request failed on attempt %s/%s: %s", attempt, self.max_retries, exc)
                time.sleep(1.5 * attempt)
        raise RuntimeError("Ollama generation failed.") from last_error


def get_llm_client() -> LLMClient:
    """Return the configured LLM client implementation."""
    provider = os.getenv("LLM_PROVIDER", "anthropic").lower().strip()
    if provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY is missing; falling back to Ollama.")
            return OllamaClient()
        return AnthropicClient()
    if provider == "gemini":
        return GeminiClient()
    if provider == "ollama":
        return OllamaClient()
    raise ValueError(f"Unsupported LLM provider: {provider}")

@dataclass
class GeminiClient(LLMClient):
    """Google Gemini-powered client."""

    model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    max_retries: int = 3

    def generate(self, prompt: str) -> str:
        from google import genai

        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )
                return response.text
            except Exception as exc:
                last_error = exc
                logger.warning("Gemini request failed on attempt %s/%s: %s", attempt, self.max_retries, exc)
                time.sleep(1.5 * attempt)
        raise RuntimeError("Gemini generation failed.") from last_error