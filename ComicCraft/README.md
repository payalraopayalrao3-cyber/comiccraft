# ComicCraft — AI Comic Story Creator

ComicCraft is a FastAPI web application based on the supplied project documentation. It collects a story prompt, character, setting, tone and art style, creates a five-panel outline, expands it into narration/dialogue, generates one image per panel, renders a browser preview, and exports the result as a PDF.

## Architecture

- **Frontend:** HTML + CSS + Jinja2
- **Backend:** FastAPI + Uvicorn
- **Story AI:** Google Gemini
- **Image AI:** Hugging Face Inference Providers or local Hugging Face Diffusers
- **PDF:** fpdf2
- **Storage:** generated JSON/image/PDF files under `static/`

## Project structure

```text
ComicCraft/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── routes.py
│   └── services/
│       ├── __init__.py
│       ├── comic_service.py
│       ├── exporters.py
│       ├── gemini_client.py
│       ├── gemini_flash.py
│       ├── gemini_pro.py
│       ├── image_generator.py
│       └── layout_builder.py
├── static/
│   ├── css/style.css
│   ├── panels/.gitkeep
│   ├── exports/.gitkeep
│   └── comics/.gitkeep
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── comic_preview.html
│   ├── export_success.html
│   └── test_image.html
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Windows VS Code setup

1. Install Python 3.11+ and VS Code.
2. Open this folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Create a virtual environment:

```powershell
py -m venv .venv
```

5. Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

6. Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

7. Copy `.env.example` to `.env`.

## Fastest first test — no AI keys

For a complete UI + backend + PDF pipeline test, set:

```env
IMAGE_BACKEND=mock
GEMINI_API_KEY=
```

The application automatically uses a deterministic mock story when no Gemini key is present. It still creates five panels, stores the comic JSON, renders the preview, and exports a PDF. This lets you verify the project before paying for API usage.

Run:

```powershell
uvicorn app.main:app --reload
```

Open:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health

## Real Gemini + Hugging Face generation

Put your keys in `.env`:

```env
GEMINI_API_KEY=your_key_here
HF_TOKEN=your_huggingface_token_here
IMAGE_BACKEND=huggingface
```

Restart Uvicorn after changing `.env`.

The app uses Gemini for the five-panel outline and story expansion, then Hugging Face for text-to-image generation.

## Local Diffusers mode

If you have a compatible GPU and want image generation to run locally:

1. Install a PyTorch build appropriate for your machine.
2. Install the optional packages:

```powershell
pip install diffusers transformers accelerate
```

3. Set:

```env
IMAGE_BACKEND=diffusers
LOCAL_DIFFUSERS_MODEL=runwayml/stable-diffusion-v1-5
```

The first local run downloads the model weights and can require substantial disk space and VRAM.

## API test

POST to `/generate-comic/json`:

```json
{
  "story_prompt": "A brave fox explores an enchanted forest and discovers a hidden clock tower.",
  "character_name": "Luna",
  "setting": "enchanted forest",
  "tone": "dramatic",
  "art_style": "comic book"
}
```

You can test this directly from `/docs`.

## Image-only test

POST form data to `/test-image` with a `prompt` field.

The route is intended as a developer utility for checking the image backend separately.

## Testing checklist

### 1. Health
Open `/health`. Expected:

```json
{"status":"ok"}
```

### 2. Home page
Open `/`. Verify the five input fields and Generate button.

### 3. Full pipeline
Use `IMAGE_BACKEND=mock` first. Generate a comic. Confirm:
- five panels appear
- images load
- captions/narration appear
- PDF download works

### 4. API
Open `/docs`, expand `POST /generate-comic/json`, click **Try it out**, enter the JSON payload and execute.

### 5. Real AI
Add valid Gemini/HF credentials and change `IMAGE_BACKEND` to `huggingface`. Generate one small test comic before increasing image dimensions/steps.

## Notes about the supplied specification

The original document describes Gemini 1.5 Flash/Pro and `runwayml/stable-diffusion-v1-5`. This implementation keeps those roles but makes model IDs configurable because model availability changes over time. The default configuration uses current configurable model IDs while preserving the same two-stage Gemini architecture and Stable-Diffusion-family image generation concept.

The original specification says the export flow redirects to a success page after download. Browsers normally treat a file download and page navigation as separate responses, so this implementation provides both:
- `/export/{comic_id}` — direct PDF download
- `/export-success?comic_id=...` — export confirmation page with a PDF button

## Security / production notes

For production, add authentication, rate limiting, persistent database storage, background jobs for long AI generations, object storage for images/PDFs, request-size limits, CSRF protection for browser forms, and stronger content moderation.
