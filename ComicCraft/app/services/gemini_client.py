from functools import lru_cache
from google import genai
from google.genai import types

from app.config import get_settings


@lru_cache
def get_client():
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. Set it in .env or use "
            "GEMINI_API_KEY plus IMAGE_BACKEND=mock for local testing."
        )
    return genai.Client(api_key=settings.gemini_api_key)


def generate_text(
    model: str,
    prompt: str,
    *,
    temperature: float = 0.8,
    max_output_tokens: int = 3000,
    response_mime_type: str | None = None,
) -> str:
    client = get_client()
    config = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_output_tokens,
    )
    if response_mime_type:
        config.response_mime_type = response_mime_type

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=config,
    )
    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("Gemini returned an empty response.")
    return text.strip()
