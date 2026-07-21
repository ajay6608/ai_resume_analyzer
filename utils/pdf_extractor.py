"""
pdf_extractor.py
----------------
Handles extracting raw text from an uploaded PDF resume.

Why pdfplumber?
- Simple API, good at preserving text layout/order compared to some alternatives.
- Works well on typical single/double column resumes (text-based PDFs, not scanned images).
"""

import pdfplumber
import io


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extract text from a PDF file object (e.g. from Streamlit's file_uploader).

    Args:
        uploaded_file: a file-like object (BytesIO) containing PDF bytes.

    Returns:
        A single string containing all extracted text from the PDF,
        with pages separated by newlines.

    Raises:
        ValueError: if no extractable text is found (e.g. the PDF is a scanned image).
    """
    text_parts = []

    # pdfplumber can open a file-like object directly
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

    full_text = "\n".join(text_parts).strip()

    if not full_text:
        raise ValueError(
            "No text could be extracted from this PDF. "
            "It might be a scanned image rather than a text-based PDF."
        )

    return full_text


def basic_clean(text: str) -> str:
    """
    Light cleanup: collapse excessive blank lines/spaces so the text we
    send to the AI model is compact (saves tokens, improves consistency).
    """
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]  # drop empty lines
    return "\n".join(lines)
