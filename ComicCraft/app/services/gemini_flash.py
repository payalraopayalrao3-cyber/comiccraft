import json
from app.config import get_settings
from app.schemas import ComicRequest, PanelOutline
from app.services.gemini_client import generate_text


def generate_outline(request: ComicRequest) -> list[PanelOutline]:
    settings = get_settings()
    prompt = f"""
You are the outline writer for ComicCraft.
Create exactly 5 connected comic panels.

User idea: {request.story_prompt}
Main character: {request.character_name}
Setting: {request.setting}
Tone: {request.tone}
Art style: {request.art_style}

Return ONLY valid JSON in this exact shape:
{{
  "panels": [
    {{
      "panel_number": 1,
      "title": "short title",
      "scene_description": "1-2 sentence visual scene description",
      "image_prompt": "detailed image-generation prompt"
    }}
  ]
}}

Rules:
- Exactly five panels, numbered 1 through 5.
- Keep the same main character and setting throughout.
- Create a clear beginning, development, conflict, climax, and ending.
- Image prompts must describe composition, characters, environment, lighting and the requested art style.
- Do not put dialogue text inside image prompts.
"""
    raw = generate_text(
        settings.gemini_flash_model,
        prompt,
        temperature=0.9,
        max_output_tokens=2500,
        response_mime_type="application/json",
    )

    try:
        data = json.loads(raw)
        panels = [PanelOutline.model_validate(item) for item in data["panels"]]
    except Exception as exc:
        raise RuntimeError(f"Could not parse Gemini outline JSON: {exc}") from exc

    if len(panels) != 5:
        raise RuntimeError("Gemini outline did not contain exactly 5 panels.")

    return panels
