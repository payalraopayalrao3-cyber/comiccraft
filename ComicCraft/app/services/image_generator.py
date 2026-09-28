from pathlib import Path
import re
import uuid

from PIL import Image, ImageDraw, ImageFont

from app.config import get_settings


BASE_DIR = Path(__file__).resolve().parents[2]
PANELS_DIR = BASE_DIR / "static" / "panels"


def _safe_name(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_")
    return value[:60] or "panel"


def _mock_image(prompt: str, output_path: Path, panel_number: int) -> None:
    # Useful for testing the full FastAPI/Jinja/PDF pipeline without any AI key.
    image = Image.new("RGB", (768, 512), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((20, 20, 748, 492), outline="black", width=6)
    draw.text((45, 45), f"ComicCraft • Panel {panel_number}", fill="black")
    wrapped = prompt[:520]
    draw.text((45, 100), wrapped, fill="black")
    draw.text((45, 450), "MOCK IMAGE — configure AI image generation for real art", fill="black")
    image.save(output_path, format="PNG")


def _huggingface_image(prompt: str, output_path: Path) -> None:
    from huggingface_hub import InferenceClient

    settings = get_settings()
    if not settings.hf_token:
        raise RuntimeError("HF_TOKEN is required when IMAGE_BACKEND=huggingface.")

    client = InferenceClient(
        api_key=settings.hf_token,
        provider="auto",
    )
    image = client.text_to_image(
        prompt=prompt,
        model=settings.image_model_id,
        width=settings.image_width,
        height=settings.image_height,
        num_inference_steps=settings.image_steps,
        guidance_scale=settings.image_guidance_scale,
    )
    image.save(output_path)


def _diffusers_image(prompt: str, output_path: Path) -> None:
    import torch
    from diffusers import DiffusionPipeline

    settings = get_settings()
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    pipe = DiffusionPipeline.from_pretrained(
        settings.local_diffusers_model,
        torch_dtype=dtype,
    )
    if torch.cuda.is_available():
        pipe = pipe.to("cuda")

    image = pipe(
        prompt=prompt,
        width=settings.image_width,
        height=settings.image_height,
        num_inference_steps=settings.image_steps,
        guidance_scale=settings.image_guidance_scale,
    ).images[0]
    image.save(output_path)


def generate_image(image_prompt: str, panel_number: int) -> str:
    settings = get_settings()
    PANELS_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"{panel_number}_{_safe_name(image_prompt)}_{uuid.uuid4().hex[:8]}.png"
    output_path = PANELS_DIR / filename

    enriched_prompt = (
        f"{image_prompt}. Comic panel illustration, cohesive recurring character, "
        "clear subject separation, expressive faces, polished composition, no speech bubbles, "
        "no captions, no readable text."
    )

    backend = settings.image_backend.lower()
    if backend == "mock":
        _mock_image(enriched_prompt, output_path, panel_number)
    elif backend == "huggingface":
        _huggingface_image(enriched_prompt, output_path)
    elif backend == "diffusers":
        _diffusers_image(enriched_prompt, output_path)
    else:
        raise RuntimeError(
            f"Unsupported IMAGE_BACKEND={settings.image_backend}. "
            "Use mock, huggingface, or diffusers."
        )

    return f"/static/panels/{filename}"
