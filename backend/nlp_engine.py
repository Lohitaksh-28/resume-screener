from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
# Load once when the file is imported — not inside each function
# all-MiniLM-L6-v2 is fast, small (~80MB), and accurate enough for resumes
model = SentenceTransformer('all-MiniLM-L6-v2')

# spaCy English model for keyword extraction
nlp = spacy.load('en_core_web_sm')
def extract_keywords(text: str) -> list:
    doc = nlp(text)

    keywords = set()

    # Noun chunks: "machine learning", "REST APIs", "data analysis"
    for chunk in doc.noun_chunks:
        clean = chunk.text.lower().strip()
        if 2 < len(clean) < 40:   # filter noise
            keywords.add(clean)

    # Named entities: "Python", "AWS", "TensorFlow"
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT", "GPE", "WORK_OF_ART"]:
            keywords.add(ent.text.lower().strip())

    return list(keywords)
def compute_semantic_score(resume_text: str, jd_text: str) -> float:
    # Convert both texts to embedding vectors
    embeddings = model.encode([resume_text, jd_text])

    # Cosine similarity returns a value between 0 and 1
    score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

    # Return as a 0–100 percentage
    return round(float(score) * 100, 2)
def compute_keyword_score(resume_text: str, jd_text: str) -> dict:
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(jd_text)

    if not jd_keywords:
        return {"score": 0, "matched": [], "missing": []}

    # Find overlap between resume and JD skills
    matched = list(set(resume_keywords) & set(jd_keywords))
    missing = list(set(jd_keywords) - set(resume_keywords))

    score = round(len(matched) / len(jd_keywords) * 100, 2)

    return {
        "score": score,
        "matched": matched[:20],   # top 20 matched skills
        "missing": missing[:20]    # top 20 missing skills
    }
def analyse(resume_text: str, jd_text: str) -> dict:
    # Semantic similarity via BERT (60% weight)
    semantic_score = compute_semantic_score(resume_text, jd_text)

    # Keyword overlap score (40% weight)
    keyword_data = compute_keyword_score(resume_text, jd_text)

    # Weighted final score
    final_score = round(
        0.6 * semantic_score + 0.4 * keyword_data["score"], 1
    )

    return {
        "final_score":    final_score,
        "semantic_score": round(semantic_score, 1),
        "keyword_score":  round(keyword_data["score"], 1),
        "matched_skills": keyword_data["matched"],
        "missing_skills": keyword_data["missing"]
    }
if __name__ == "__main__":
    sample_resume = """
    Gunukula Pandu Ranga Lohitaksh
+91 9010191333 | gprlohitaksh@gmail.com | linkedin.com/in/lohitaksh | github.com/lohitaksh
Education
Vardhaman College of Engineering
Hyderabad, Telangana
Bachelor of Technology in Electronics and Communication Engineering
Aug. 2023 Present
Sri Chaitanya
Hyderabad, Telangana
MPC
Aug. 2021 May 2023
Experience
National Cadet Corps
June 2024 Present
Vardhaman College of Engineering
Hyderabad, Telangana
Underwent rigorous military training including drill, weapon handl

=== SECTIONS FOUND ===
[OTHER]: Gunukula Pandu Ranga Lohitaksh
+91 9010191333 | gprlohitaksh@gmail.com | linkedin.com/in/lohitaksh |...
[EDUCATION]: Vardhaman College of Engineering
Hyderabad, Telangana
Bachelor of Technology in Electronics and Comm...
[EXPERIENCE]: National Cadet Corps
June 2024 Present
Vardhaman College of Engineering
Hyderabad, Telangana
Underwe...
[PROJECTS]: SAR Image Despeckling via Adaptive Recursive CNN | Python, CNN, Colab
Jan 2026 April 2026
Built an e...
[SKILLS]: Languages: Assembly language, MATLAB,Python, C, SQL
Tools: MATLAB, Cadence, Xilinx, Simulink, AutoCAD, Git
    """

    sample_jd = """
    Job Title

VLSI Engineer

Location

[City, State / Remote / Hybrid]

Employment Type

Full-time

About the Role

We are looking for a motivated and detail-oriented VLSI Engineer to join our semiconductor design team. The ideal candidate will work on digital and/or analog VLSI design, verification, implementation, and optimization for high-performance integrated circuits. You will collaborate with cross-functional teams including architecture, RTL, verification, physical design, and validation engineers throughout the chip development lifecycle.

Key Responsibilities
Design and develop VLSI circuits for ASIC/SoC projects
Write and debug RTL code using Verilog/SystemVerilog/VHDL
Perform functional verification, simulation, and timing analysis
Participate in synthesis, STA, DFT, and physical design activities
Develop and execute test benches and verification environments
Analyze power, performance, and area (PPA) optimization
Collaborate with firmware, hardware, and validation teams
Debug silicon issues and support post-silicon validation
Maintain technical documentation and design reports
Ensure design compliance with industry standards and project requirements
Required Qualifications
Bachelor’s or Master’s degree in Electronics, Electrical Engineering, VLSI Design, or related field
Strong understanding of digital electronics and semiconductor fundamentals
Experience with Verilog/SystemVerilog/VHDL
Knowledge of ASIC/FPGA design flow
Familiarity with EDA tools such as Cadence, Synopsys, or Mentor Graphics
Understanding of STA, synthesis, and low-power design concepts
Strong problem-solving and debugging skills
Good communication and teamwork abilities
Preferred Skills
Experience with UVM-based verification
Knowledge of DFT, CDC, and linting tools
Familiarity with scripting languages such as Python, Perl, or TCL
Exposure to physical design and floorplanning
Understanding of AMBA protocols (AXI, AHB, APB)
Experience in FPGA prototyping is a plus
Experience
Freshers / Entry-Level / 1–5 years experience (customize as needed)
Tools & Technologies
Verilog / SystemVerilog / VHDL
Cadence Virtuoso
Synopsys Design Compiler
PrimeTime
ModelSim / QuestaSim / VCS
MATLAB / Python / TCL
What We Offer
Competitive salary and benefits
Opportunity to work on cutting-edge semiconductor technologies
Learning and growth opportunities
Collaborative engineering environment
Flexible work culture
    """

    result = analyse(sample_resume, sample_jd)

    print(f"Final Score    : {result['final_score']}%")
    print(f"Semantic Score : {result['semantic_score']}%")
    print(f"Keyword Score  : {result['keyword_score']}%")
    print(f"Matched Skills : {result['matched_skills']}")
    print(f"Missing Skills : {result['missing_skills']}")
    