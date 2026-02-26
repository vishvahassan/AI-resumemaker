"""
Resume text extraction from PDF and plain text files.

- PDF: First tries normal text extraction (pdfplumber / PyPDF2).
  If extracted text is too short (< 100 chars), assumes a scanned/image PDF
  and falls back to OCR (pdf2image + pytesseract).
- TXT: Reads file as UTF-8 (with latin-1 fallback).
"""

import io
import os
from pathlib import Path

# Minimum text length below which we assume the PDF is image-based and try OCR.
OCR_FALLBACK_THRESHOLD = 100


def extract_text_from_pdf(file) -> str:
    """
    Extract text from an uploaded PDF file using pdfplumber.

    Args:
        file: File-like object (e.g. request.FILES['resume_file']) opened in binary mode.

    Returns:
        Extracted text as a string. Returns empty string if no text could be extracted.
    """
    file.seek(0)
    import pdfplumber
    with pdfplumber.open(io.BytesIO(file.read())) as pdf:
        parts = []
        for page in pdf.pages:
            text = page.extract_text()
            if text and text.strip():
                parts.append(text.strip())
    return "\n\n".join(parts).strip() or ""


def extract_resume_text(file_path: str | os.PathLike) -> str:
    """
    Reusable function: extract text from a resume file at the given path.

    - PDF: Tries normal extraction first; if result is too short, uses OCR fallback
      for scanned/image-based PDFs.
    - TXT: Reads file as UTF-8 (with latin-1 fallback).

    Args:
        file_path: Path to the resume file (PDF or .txt) on disk.

    Returns:
        Extracted text as a string.

    Raises:
        FileNotFoundError: If file_path does not exist.
        ValueError: If file type is not supported or extraction (including OCR) fails.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Resume file not found: {file_path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _extract_from_pdf_path(path)
    if suffix == ".txt":
        return _extract_from_text_path(path)
    raise ValueError(f"Unsupported file type: {suffix}. Use .pdf or .txt")


def _extract_from_pdf_path(path: Path) -> str:
    """
    Extract text from PDF: try normal extraction first, then OCR fallback for scanned PDFs.

    Step 1: Try normal text extraction using pdfplumber or PyPDF2.
    Step 2: If extracted text length < 100 characters, assume it is a scanned/image PDF.
    Step 3–5: Use pdf2image to convert pages to images, then pytesseract to OCR each image;
              combine and return the OCR text. If OCR fails, raise ValueError.
    """
    # Step 1: Try normal text extraction (pdfplumber or PyPDF2)
    try:
        text = _extract_pdf_normal(path)
    except Exception as e:
        raise ValueError(f"Could not read PDF: {e!s}") from e

    # Step 2: If we got very little text, assume scanned/image PDF and use OCR fallback
    if len(text.strip()) < OCR_FALLBACK_THRESHOLD:
        text = _extract_from_pdf_ocr(path)

    return text.strip() or ""


def _extract_pdf_normal(path: Path) -> str:
    """Normal PDF text extraction using pdfplumber, with PyPDF2 fallback."""
    try:
        import pdfplumber
    except ImportError:
        pass
    else:
        return _extract_pdf_pdfplumber(path)

    try:
        import PyPDF2
    except ImportError:
        try:
            from pypdf import PdfReader as PypdfReader
            return _extract_pdf_pypdf(path, PypdfReader)
        except ImportError:
            raise ImportError(
                "Install a PDF library: pip install pdfplumber or pip install PyPDF2"
            )
    return _extract_pdf_pypdf2(path)


def _extract_from_pdf_ocr(path: Path) -> str:
    """
    OCR fallback for scanned/image-based PDFs.

    Step 3: Use pdf2image to convert each PDF page to images.
    Step 4: Use pytesseract.image_to_string() to extract text from each image.
    Step 5: Combine OCR text from all pages and return.

    If OCR fails (missing dependencies or runtime error), raises ValueError.
    """
    try:
        from pdf2image import convert_from_path
        import pytesseract
    except ImportError as e:
        raise ValueError(
            "Could not extract text from resume. For scanned PDFs, install: "
            "pip install pdf2image pytesseract. You also need Tesseract OCR and poppler installed on your system."
        ) from e

    try:
        # Step 3: Convert each PDF page to an image (requires poppler-utils on system)
        images = convert_from_path(path)
    except Exception as e:
        raise ValueError("Could not extract text from resume") from e

    if not images:
        raise ValueError("Could not extract text from resume")

    # Step 4 & 5: OCR each page and combine the text
    parts = []
    for img in images:
        try:
            page_text = pytesseract.image_to_string(img)
            if page_text and page_text.strip():
                parts.append(page_text.strip())
        except Exception as e:
            # e.g. Tesseract not installed or not on PATH
            raise ValueError("Could not extract text from resume") from e

    combined = "\n\n".join(parts).strip()
    if not combined:
        raise ValueError("Could not extract text from resume")
    return combined


def _extract_pdf_pdfplumber(path: Path) -> str:
    """Extract text using pdfplumber."""
    parts = []
    with pdfplumber.open(str(path.resolve())) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text and text.strip():
                parts.append(text.strip())
    return "\n\n".join(parts).strip() or ""


def _extract_pdf_pypdf2(path: Path) -> str:
    """Extract text using PyPDF2."""
    import PyPDF2
    parts = []
    with open(str(path.resolve()), "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text = page.extract_text()
            if text and text.strip():
                parts.append(text.strip())
    return "\n\n".join(parts).strip() or ""


def _extract_pdf_pypdf(path: Path, PdfReader) -> str:
    """Extract text using pypdf (PdfReader)."""
    parts = []
    reader = PdfReader(str(path.resolve()))
    for page in reader.pages:
        text = page.extract_text()
        if text and text.strip():
            parts.append(text.strip())
    return "\n\n".join(parts).strip() or ""


def _extract_from_text_path(path: Path) -> str:
    """Read plain text file (UTF-8, with latin-1 fallback)."""
    with open(path, "rb") as f:
        raw = f.read()
    try:
        return raw.decode("utf-8").strip()
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace").strip()


def extract_text_from_file(uploaded_file) -> str:
    """
    Extract text from an uploaded file object (e.g. request.FILES['resume_file']).
    Supports PDF (including OCR fallback for scanned PDFs) and .txt.
    """
    name = getattr(uploaded_file, "name", "") or ""
    if name.lower().endswith(".pdf"):
        content = uploaded_file.read()
        uploaded_file.seek(0)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            return extract_resume_text(tmp_path)
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    content = uploaded_file.read()
    try:
        return content.decode("utf-8").strip()
    except UnicodeDecodeError:
        return content.decode("latin-1", errors="replace").strip()
