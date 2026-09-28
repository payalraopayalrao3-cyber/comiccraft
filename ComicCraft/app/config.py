from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    environment: str = "development"

    gemini_api_key: str = ""
    gemini_flash_model: str = "gemini-2.5-flash"
    gemini_pro_model: str = "gemini-2.5-pro"

    # "mock" works without external API keys and is useful for UI testing.
    # "huggingface" uses HF Inference Providers.
    # "diffusers" loads a local Diffusers pipeline and normally needs a GPU.
    image_backend: str = "huggingface"
    hf_token: str = ""
    image_model_id: str = "stabilityai/stable-diffusion-3.5-large-turbo"
    local_diffusers_model: str = "runwayml/stable-diffusion-v1-5"

    image_width: int = 768
    image_height: int = 512
    image_steps: int = 20
    image_guidance_scale: float = 7.0

    max_prompt_length: int = 1200
    max_character_length: int = 80
    max_setting_length: int = 120

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
