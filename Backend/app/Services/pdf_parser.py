import pdfplumber
import os


def extract_text_from_pdf(filepath: str) -> str:
    """
    Extract clean plain text from a PDF resume.
    Handles multi-page PDFs automatically.
    """
    if not os.path.exists(filepath):
        print(f"PDF not found: {filepath}")
        return ""

    try:
        text = ""
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        cleaned = clean_text(text)
        return cleaned

    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text — remove extra spaces, blank lines.
    """
    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.strip()
        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def get_resume_summary(filepath: str) -> dict:
    """
    Returns a quick summary of the resume PDF.
    Useful for validation before sending to Groq.
    """
    text = extract_text_from_pdf(filepath)

    return {
        "extracted": bool(text),
        "word_count": len(text.split()) if text else 0,
        "char_count": len(text) if text else 0,
        "preview": text[:300] if text else "Could not extract text",
    }