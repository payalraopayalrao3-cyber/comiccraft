from pathlib import Path
from datetime import datetime
import re

from fpdf import FPDF
from PIL import Image


BASE_DIR = Path(__file__).resolve().parents[2]
EXPORTS_DIR = BASE_DIR / "static" / "exports"


def _safe_pdf_text(text: str) -> str:
    # Core PDF font is Latin-1. Replace unsupported characters rather than failing export.
    return text.encode("latin-1", "replace").decode("latin-1")


def save_pdf(comic_id: str, layout: list[dict]) -> str:
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"comic_{comic_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    output = EXPORTS_DIR / filename

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)

    for index, panel in enumerate(layout):
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.multi_cell(0, 10, _safe_pdf_text(
            f"Panel {panel['panel_number']}: {panel['title']}"
        ))

        image_url = panel["image_path"]
        if image_url:
            image_path = BASE_DIR / image_url.removeprefix("/static/")
            if image_path.exists():
                with Image.open(image_path) as img:
                    width, height = img.size
                max_w, max_h = 180, 105
                ratio = min(max_w / width, max_h / height)
                pdf.image(str(image_path), w=width * ratio, h=height * ratio)
                pdf.ln(5)

        pdf.set_font("Helvetica", "I", 10)
        pdf.multi_cell(0, 6, _safe_pdf_text(panel["scene_description"]))
        pdf.ln(2)

        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 6, _safe_pdf_text("Caption"))
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, _safe_pdf_text(panel["caption"]))
        pdf.ln(2)

        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 6, _safe_pdf_text("Narration"))
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, _safe_pdf_text(panel["narration"]))

    pdf.output(str(output))
    return f"/static/exports/{filename}"
