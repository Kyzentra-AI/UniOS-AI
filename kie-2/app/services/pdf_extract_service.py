"""
UniOS PDF & OCR Extraction Service
Extracts text from digital PDFs, scanned/image-based PDFs, and syllabus images.
Supports:
  1. Direct text stream extraction via pypdf (fast, lossless for digital PDFs).
  2. Embedded page image extraction + OCR via pytesseract for scanned/image-based PDFs.
  3. Image file OCR (PNG, JPG, JPEG) via Pillow + pytesseract.
  4. Remote URL download extraction via httpx.
"""

import base64
import io
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


class PDFExtractService:
    """Service for extracting plain text from PDF documents and images with OCR fallback."""

    def extract_text_from_pdf_bytes(
        self, pdf_bytes: bytes, filename: Optional[str] = None
    ) -> str:
        """
        Extracts text from PDF bytes.
        First attempts native text extraction (pypdf).
        If the PDF contains negligible text (< 80 chars), attempts OCR on embedded page images.
        """
        if not pdf_bytes:
            return ""

        extracted_text_parts = []
        try:
            import pypdf

            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            total_pages = len(reader.pages)
            logger.info(f"[PDFExtractService] Reading PDF ({total_pages} pages, {len(pdf_bytes)} bytes)")

            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        extracted_text_parts.append(page_text.strip())
                except Exception as p_err:
                    logger.debug(f"[PDFExtractService] Page {page_num} text extraction error: {p_err}")

        except Exception as pdf_err:
            logger.warning(f"[PDFExtractService] Failed to parse PDF with pypdf: {pdf_err}")

        combined_text = "\n\n".join(extracted_text_parts).strip()

        # If digital text extraction extracted sufficient content (>= 80 chars), return it directly
        if len(combined_text) >= 80:
            logger.info(f"[PDFExtractService] Digital text extraction succeeded ({len(combined_text)} chars from {total_pages} pages)")
            return combined_text

        # If text is minimal or 0, the PDF is likely scanned / image-based. Run OCR on embedded images.
        logger.info(f"[PDFExtractService] Minimal text found ({len(combined_text)} chars). Attempting OCR on page images...")
        ocr_text = self._ocr_pdf_images(pdf_bytes)
        if ocr_text and len(ocr_text.strip()) >= 50:
            logger.info(f"[PDFExtractService] OCR extraction succeeded ({len(ocr_text)} chars)")
            return ocr_text.strip()

        if combined_text:
            return combined_text

        # If completely empty, return filename context so downstream domain fallbacks can infer
        clean_name = re.sub(r"\.[a-zA-Z0-9]+$", "", filename or "").replace("_", " ").replace("-", " ")
        logger.warning(f"[PDFExtractService] Zero text extracted via native or OCR for '{filename}'")
        return f"Syllabus Document: {clean_name}" if clean_name else ""

    def _ocr_pdf_images(self, pdf_bytes: bytes) -> str:
        """Extracts images from PDF pages and runs OCR via pytesseract."""
        ocr_results = []
        try:
            import pypdf
            from PIL import Image
            import pytesseract

            reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
            for page_num, page in enumerate(reader.pages):
                images = getattr(page, "images", [])
                for img_idx, img in enumerate(images):
                    try:
                        pil_img = Image.open(io.BytesIO(img.data))
                        # Run OCR
                        text = pytesseract.image_to_string(pil_img)
                        if text and text.strip():
                            ocr_results.append(text.strip())
                    except Exception as img_err:
                        logger.debug(f"[PDFExtractService] OCR failed for page {page_num} image {img_idx}: {img_err}")
        except Exception as ocr_err:
            logger.warning(f"[PDFExtractService] OCR engine unavailable or failed: {ocr_err}")

        return "\n\n".join(ocr_results).strip()

    def extract_text_from_image_bytes(
        self, image_bytes: bytes, filename: Optional[str] = None
    ) -> str:
        """Performs OCR on raw image bytes (PNG, JPG, JPEG)."""
        if not image_bytes:
            return ""

        try:
            from PIL import Image
            import pytesseract

            pil_img = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(pil_img)
            if text and text.strip():
                logger.info(f"[PDFExtractService] Image OCR extracted {len(text)} chars")
                return text.strip()
        except Exception as img_err:
            logger.warning(f"[PDFExtractService] Image OCR failed: {img_err}")

        clean_name = re.sub(r"\.[a-zA-Z0-9]+$", "", filename or "").replace("_", " ").replace("-", " ")
        return f"Syllabus Image Document: {clean_name}" if clean_name else ""

    def extract_text_from_base64(
        self, base64_str: str, filename: Optional[str] = None
    ) -> str:
        """Decodes base64 string and extracts text based on file signature."""
        if not base64_str:
            return ""

        # Strip data URL prefix if present (e.g. 'data:application/pdf;base64,JVBERi...')
        if "," in base64_str and ";base64" in base64_str:
            base64_str = base64_str.split(",", 1)[1]

        try:
            file_bytes = base64.b64decode(base64_str.strip())
        except Exception as b64_err:
            logger.error(f"[PDFExtractService] Invalid Base64 payload: {b64_err}")
            return ""

        return self.extract_from_bytes(file_bytes, filename=filename)

    def extract_from_url(self, url: str, filename: Optional[str] = None) -> str:
        """Downloads document from public / pre-signed URL and extracts text."""
        if not url:
            return ""

        try:
            import httpx

            logger.info(f"[PDFExtractService] Downloading syllabus from URL: {url[:80]}...")
            with httpx.Client(timeout=30.0, follow_redirects=True) as client:
                resp = client.get(url)
                resp.raise_for_status()
                file_bytes = resp.content

            target_filename = filename or url.split("?")[0].split("/")[-1]
            return self.extract_from_bytes(file_bytes, filename=target_filename)
        except Exception as dl_err:
            logger.error(f"[PDFExtractService] Failed to download document from URL: {dl_err}")
            return ""

    def extract_from_bytes(
        self, file_bytes: bytes, filename: Optional[str] = None, content_type: Optional[str] = None
    ) -> str:
        """Routes file bytes to PDF or image extractor based on magic header / filename."""
        if not file_bytes:
            return ""

        # PDF magic bytes: %PDF-
        if file_bytes.startswith(b"%PDF") or (filename and filename.lower().endswith(".pdf")) or (content_type and "pdf" in content_type.lower()):
            return self.extract_text_from_pdf_bytes(file_bytes, filename=filename)

        # Image magic bytes or extensions
        is_image = (
            file_bytes.startswith(b"\x89PNG")
            or file_bytes.startswith(b"\xff\xd8\xff")  # JPEG
            or file_bytes.startswith(b"GIF")
            or (filename and any(filename.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"]))
            or (content_type and "image" in content_type.lower())
        )
        if is_image:
            return self.extract_text_from_image_bytes(file_bytes, filename=filename)

        # Attempt UTF-8 plain text decode fallback
        try:
            decoded = file_bytes.decode("utf-8")
            if len(decoded.strip()) >= 20:
                return decoded.strip()
        except Exception:
            pass

        return self.extract_text_from_pdf_bytes(file_bytes, filename=filename)


_pdf_service_instance: Optional[PDFExtractService] = None


def get_pdf_extract_service() -> PDFExtractService:
    global _pdf_service_instance
    if _pdf_service_instance is None:
        _pdf_service_instance = PDFExtractService()
    return _pdf_service_instance
