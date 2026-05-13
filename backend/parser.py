# Standard library
import re
import io

# PDF parsing
import fitz                              # PyMuPDF
from pdfminer.high_level import extract_text

# Word document support
from docx import Document
def clean_text(raw: str) -> str:
    # Remove non-ASCII characters (weird symbols from PDFs)
    text = re.sub(r'[^\x00-\x7F]+', ' ', raw)

    # Collapse multiple spaces into one
    text = re.sub(r' +', ' ', text)

    # Collapse 3+ blank lines into 2 (preserve section gaps)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Strip each line and remove empty ones
    lines = [line.strip() for line in text.splitlines()]
    lines = [l for l in lines if l]

    return "\n".join(lines)
def parse_with_pymupdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    full_text = []

    for page in doc:
        # "text" mode sorts characters by reading order
        text = page.get_text("text")
        full_text.append(text)

    doc.close()
    return clean_text("\n".join(full_text))
def parse_with_ocr(pdf_path: str) -> str:
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return parse_with_pymupdf(pdf_path)  # fallback if OCR not installed

    doc = fitz.open(pdf_path)
    full_text = []

    for page in doc:
        text = page.get_text("text").strip()

        if len(text) < 50:  # likely a scanned image page
            mat = fitz.Matrix(2, 2)         # 2x zoom for better OCR accuracy
            pix = page.get_pixmap(matrix=mat)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            text = pytesseract.image_to_string(img)

        full_text.append(text)

    doc.close()
    return clean_text("\n".join(full_text))
def parse_docx(docx_path: str) -> str:
    doc = Document(docx_path)
    full_text = []

    for para in doc.paragraphs:
        if para.text.strip():
            full_text.append(para.text.strip())

    return clean_text("\n".join(full_text))
def extract_sections(text: str) -> dict:
    section_headers = {
        "summary":    r"(summary|objective|profile|about)",
        "education":  r"(education|qualifications|academics)",
        "experience": r"(experience|work history|employment)",
        "skills":     r"(skills|technical skills|competencies)",
        "projects":   r"(projects|personal projects|portfolio)",
    }

    sections = {}
    current_section = "other"
    buffer = []

    for line in text.splitlines():
        matched = False
        for sec, pattern in section_headers.items():
            if re.search(pattern, line.lower()):
                if buffer:
                     sections[current_section] = "\n".join(buffer)
                current_section = sec
                buffer = []
                matched = True
                break
        if not matched:
            buffer.append(line)

    if buffer:
        sections[current_section] = "\n".join(buffer)

    return sections
def parse_resume(file_path: str) -> dict:
    # Detect file type
    if file_path.endswith(".docx"):
        raw_text = parse_docx(file_path)
    else:
        raw_text = parse_with_ocr(file_path)  # handles both digital + scanned PDFs

    # Extract named sections
    sections = extract_sections(raw_text)

    return {
        "full_text": raw_text,
        "sections": sections
    }
# Quick test — run directly to verify it works
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = parse_resume(sys.argv[1])
        print("=== FULL TEXT (first 500 chars) ===")
        print(result["full_text"][:500])
        print("\n=== SECTIONS FOUND ===")
        for sec, content in result["sections"].items():
            print(f"[{sec.upper()}]: {content[:100]}...")
    else:
        print("Usage: python parser.py your_resume.pdf")
        