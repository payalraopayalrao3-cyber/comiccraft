from app.schemas import StoryPanel


def build_comic_layout(panels: list[StoryPanel]) -> list[dict]:
    return [
        {
            "panel_number": panel.panel_number,
            "title": panel.title,
            "image_path": getattr(panel, "image_path", None),
            "scene_description": panel.scene_description,
            "image_prompt": panel.image_prompt,
            "caption": panel.caption,
            "narration": panel.narration,
        }
        for panel in panels
    ]
