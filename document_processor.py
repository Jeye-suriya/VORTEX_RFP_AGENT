import os
from pypdf import PdfReader


def extract_text_from_pdf(path: str) -> str:
    """Extracts text from PDF. If text extraction yields very little text, attempts OCR if dependencies are available."""
    text_parts = []
    reader = PdfReader(path)
    for page_num, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text()
            if text and len(text.strip()) > 30:
                text_parts.append(text)
            else:
                # placeholder for OCR fallback
                text_parts.append(f"[Page {page_num}: extracted no text]")
        except Exception:
            text_parts.append(f"[Page {page_num}: extraction error]")

    combined = "\n\n".join(text_parts)

    # If no meaningful extracted text, try optional OCR if available
    if combined.strip().count('\n') < 2:
        try:
            from pdf2image import convert_from_path
            import pytesseract

            images = convert_from_path(path, dpi=200)
            ocr_text = []
            for i, img in enumerate(images):
                ocr_text.append(pytesseract.image_to_string(img))
            combined = "\n\n".join(ocr_text)
        except Exception:
            # OCR not available or failed; continue with what we have
            pass

    return combined
