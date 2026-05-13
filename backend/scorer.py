from backend.nlp_engine import analyse

def get_grade(score: float) -> dict:
    """Convert a 0–100 score into a letter grade + label."""
    if score >= 80:
        return {"grade": "A", "label": "Excellent Match",  "color": "green"}
    elif score >= 60:
        return {"grade": "B", "label": "Good Match",      "color": "blue"}
    elif score >= 40:
        return {"grade": "C", "label": "Partial Match",    "color": "yellow"}
    elif score >= 20:
        return {"grade": "D", "label": "Weak Match",      "color": "orange"}
    else:
        return {"grade": "F", "label": "Poor Match",      "color": "red"}


def get_recommendation(score: float, missing_skills: list) -> str:
    top_missing = missing_skills[:5]

    if score >= 80:
        return (
            "Strong match! Apply confidently. Tailor your cover letter "
            "to highlight your most relevant projects."
        )
    elif score >= 60:
        gaps = ", ".join(top_missing) if top_missing else "a few areas"
        return (
            f"Good match. Consider adding these skills to your resume: {gaps}. "
            "One relevant project could push you to an A."
        )
    elif score >= 40:
        gaps = ", ".join(top_missing) if top_missing else "several areas"
        return (
            f"Partial match. Key gaps: {gaps}. "
            "Build 1–2 small projects using these technologies to improve your score."
        )
    else:
        return (
            "Low match for this specific role. Consider applying to similar "
            "roles that better match your current skill set, or upskill first."
        )


def screen(resume_text: str, jd_text: str) -> dict:
    analysis = analyse(resume_text, jd_text)

    grade_info = get_grade(analysis["final_score"])
    suggestion = get_recommendation(
        analysis["final_score"],
        analysis["missing_skills"]
    )

    return {
        "final_score":    analysis["final_score"],
        "semantic_score": analysis["semantic_score"],
        "keyword_score":  analysis["keyword_score"],
        "grade":          grade_info["grade"],
        "label":          grade_info["label"],
        "color":          grade_info["color"],
        "matched_skills": analysis["matched_skills"],
        "missing_skills": analysis["missing_skills"],
        "recommendation": suggestion
    }