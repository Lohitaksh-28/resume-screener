from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile, os, shutil

from backend.parser import parse_resume
from backend.scorer import screen

# Create the FastAPI app
app = FastAPI(
    title="Resume Screener API",
    description="AI-powered resume vs job description matcher",
    version="1.0.0"
)

# Allow the React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def health_check():
    return {
        "status": "running",
        "message": "Resume Screener API is live"
    }
@app.post("/screen")
async def screen_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    # Validate file type
    if not resume.filename.endswith((".pdf", ".docx")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported"
        )

    # Save uploaded file to a temp location
    suffix = ".pdf" if resume.filename.endswith(".pdf") else ".docx"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(resume.file, tmp)
        tmp_path = tmp.name

    try:
        # Parse the resume
        parsed = parse_resume(tmp_path)
        resume_text = parsed["full_text"]

        if not resume_text.strip():
            raise HTTPException(
                status_code=422,
                detail="Could not extract text from the resume. Try a different file."
            )

        # Run AI scoring
        result = screen(resume_text, job_description)
        result["sections"] = parsed["sections"]
        return result

    finally:
        # Always delete the temp file
        os.unlink(tmp_path)
        