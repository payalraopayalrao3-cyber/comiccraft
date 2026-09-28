import json
import uuid
from pathlib import Path

from app.config import get_settings
from app.schemas import ComicDocument, ComicRequest, StoryPanel
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout
from app.services.exporters import save_pdf


BASE_DIR = Path(__file__).resolve().parents[2]
COMICS_DIR = BASE_DIR / "static" / "comics"


def _mock_outline(request: ComicRequest):
    from app.schemas import PanelOutline
    return [
        PanelOutline(
            panel_number=i,
            title=[
                "The Idea",
                "Into the World",
                "Trouble Appears",
                "The Turning Point",
                "A New Beginning",
            ][i - 1],
            scene_description=f"{request.character_name} faces the next stage of the adventure in {request.setting}.",
            image_prompt=(
                f"{request.character_name} in {request.setting}, panel {i}, "
                f"{request.art_style} comic art, {request.tone} mood, cinematic composition"
            ),
        )
        for i in range(1, 6)
    ]


def _mock_story(request: ComicRequest, outlines):
    return [
        StoryPanel(
            **outline.model_dump(),
            caption=f"{request.tone.title()} moment in {request.setting}.",
            narration=(
                f'{request.character_name}: "Every step brings me closer to the answer." '
                f"The adventure continues."
            ),
        )
        for outline in outlines
    ]


def _persist(document: ComicDocument) -> None:
    COMICS_DIR.mkdir(parents=True, exist_ok=True)
    path = COMICS_DIR / f"{document.comic_id}.json"
    path.write_text(document.model_dump_json(indent=2), encoding="utf-8")


def load_comic(comic_id: str) -> ComicDocument:
    path = COMICS_DIR / f"{comic_id}.json"
    if not path.exists():
        raise FileNotFoundError("Comic not found.")
    return ComicDocument.model_validate_json(path.read_text(encoding="utf-8"))


def generate_comic(request: ComicRequest) -> ComicDocument:
    settings = get_settings()
    comic_id = uuid.uuid4().hex[:12]

    if settings.gemini_api_key:
        outlines = generate_outline(request)
        story = generate_story(request, outlines)
    else:
        outlines = _mock_outline(request)
        story = _mock_story(request, outlines)

    final_panels = []
    for panel in story:
        image_path = generate_image(panel.image_prompt, panel.panel_number)
        panel_data = panel.model_dump()
        panel_data["image_path"] = image_path
        final_panels.append(panel_data)

    panels = [StoryPanel.model_validate(p) for p in final_panels]
    layout = build_comic_layout(panels)
    pdf_path = save_pdf(comic_id, layout)

    document = ComicDocument(
        comic_id=comic_id,
        request=request,
        panels=panels,
        pdf_path=pdf_path,
    )
    _persist(document)
    return document
