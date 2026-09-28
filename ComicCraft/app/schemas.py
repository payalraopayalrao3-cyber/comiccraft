from pydantic import BaseModel, Field, field_validator


class ComicRequest(BaseModel):
    story_prompt: str = Field(min_length=3, max_length=1200)
    character_name: str = Field(min_length=1, max_length=80)
    setting: str = Field(min_length=1, max_length=120)
    tone: str = Field(min_length=1, max_length=40)
    art_style: str = Field(min_length=1, max_length=60)

    @field_validator("*")
    @classmethod
    def strip_values(cls, value: str) -> str:
        return value.strip()


class PanelOutline(BaseModel):
    panel_number: int = Field(ge=1, le=5)
    title: str
    scene_description: str
    image_prompt: str


class StoryPanel(BaseModel):
    panel_number: int = Field(ge=1, le=5)
    title: str
    scene_description: str
    image_prompt: str
    caption: str
    narration: str


class ComicDocument(BaseModel):
    comic_id: str
    request: ComicRequest
    panels: list[StoryPanel]
    pdf_path: str | None = None
