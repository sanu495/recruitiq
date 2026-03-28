import pdfplumber

def extract_text_from_pdf(filepath: str) -> str:
    """Extract plain text from a PDF resume file."""
    try:
        text= ""
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text +=page_text + "\n"
        return text.strip()
    
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""
