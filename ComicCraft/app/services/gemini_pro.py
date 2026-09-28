import json
from app.config import get_settings
from app.schemas import ComicRequest, PanelOutline, StoryPanel
from app.services.gemini_client import generate_text


def generate_story(request: ComicRequest, outlines: list[PanelOutline]) -> list[StoryPanel]:
    settings = get_settings()
    outline_json = json.dumps([p.model_dump() for p in outlines], ensure_ascii=False)

    prompt = f"""
You are the story/dialogue writer for ComicCraft.
Expand this five-panel outline into a polished comic script.

User details:
- Idea: {request.story_prompt}
- Character: {request.character_name}
- Setting: {request.setting}
- Tone: {request.tone}
- Art style: {request.art_style}

Outline:
{outline_json}

Return ONLY valid JSON:
{{
  "panels": [
    {{
      "panel_number": 1,
      "title": "...",
      "scene_description": "...",
      "image_prompt": "...",
      "caption": "...",
      "narration": "..."
    }}
  ]
}}

Rules:
- Exactly five panels.
- Preserve the outline's events and image prompts.
- Narration should be concise enough for a comic page.
- Caption can contain ambient/action text.
- Dialogue may be included inside narration using quotation marks.
- Keep character behavior and visual details consistent across panels.
"""
    raw = generate_text(
        settings.gemini_pro_model,
        prompt,
        temperature=0.85,
        max_output_tokens=4500,
        response_mime_type="application/json",
    )

    try:
        data = json.loads(raw)
        panels = [StoryPanel.model_validate(item) for item in data["panels"]]
    except Exception as exc:
        raise RuntimeError(f"Could not parse Gemini story JSON: {exc}") from exc

    if len(panels) != 5:
        raise RuntimeError("Gemini story did not contain exactly 5 panels.")

    return panels
