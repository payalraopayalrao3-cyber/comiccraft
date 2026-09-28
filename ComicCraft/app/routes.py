from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app.schemas import ComicRequest
from app.services.comic_service import generate_comic, load_comic
from app.services.image_generator import generate_image


BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"error": None},
    )


@router.post("/generate", response_class=HTMLResponse)
def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        payload = ComicRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )
        comic = generate_comic(payload)
        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={"comic": comic, "error": None},
        )
    except (ValidationError, ValueError) as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": f"Please check your input: {exc}"},
            status_code=400,
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": str(exc)},
            status_code=500,
        )


@router.post("/generate-comic/json")
def generate_comic_json(payload: ComicRequest):
    try:
        comic = generate_comic(payload)
        return {
            "success": True,
            "comic_id": comic.comic_id,
            "request": comic.request.model_dump(),
            "panels": [
                {**panel.model_dump()}
                for panel in comic.panels
            ],
            "pdf_path": comic.pdf_path,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/comic/{comic_id}", response_class=HTMLResponse)
def comic_preview(request: Request, comic_id: str):
    try:
        comic = load_comic(comic_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return templates.TemplateResponse(
        request=request,
        name="comic_preview.html",
        context={"comic": comic, "error": None},
    )


@router.get("/export/{comic_id}")
def export_comic(comic_id: str):
    try:
        comic = load_comic(comic_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if not comic.pdf_path:
        raise HTTPException(status_code=404, detail="PDF is not available.")

    pdf_path = BASE_DIR / comic.pdf_path.removeprefix("/static/")
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF file is missing.")

    return FileResponse(
        str(pdf_path),
        media_type="application/pdf",
        filename=pdf_path.name,
    )


@router.get("/export-success", response_class=HTMLResponse)
def export_success(request: Request, comic_id: str):
    try:
        comic = load_comic(comic_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={"comic": comic},
    )


@router.post("/test-image")
def test_image(prompt: str = Form(...)):
    try:
        image_path = generate_image(prompt, 0)
        return RedirectResponse(
            url=f"/test-image/result?path={quote(image_path)}",
            status_code=303,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/test-image/result", response_class=HTMLResponse)
def test_image_result(request: Request, path: str):
    return templates.TemplateResponse(
        request=request,
        name="test_image.html",
        context={"image_path": path},
    )


@router.get("/health")
def health():
    return {"status": "ok"}
