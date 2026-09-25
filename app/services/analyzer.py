from app.services.pdf_extractor import extract_text_from_pdf
from app.services.text_cleaner import clean_text
from app.services.skill_extractor import extract_skills
from app.services.candidate_extractor import extract_candidate_info
from app.services.matcher import (
    calculate_match_score,
    compare_skills
)
 
 
# Seuils recalibrés à partir de scripts/evaluate_scores.py sur le
# modèle fine-tuné en anglais : bons matchs observés entre 36 et 66,
# mauvais matchs entre 14 et 23. À réévaluer si tu ajoutes plus de
# cas de test ou si tu réentraînes le modèle.
LOW_MATCH_THRESHOLD = 15
MODERATE_MATCH_THRESHOLD = 30
 
 
def analyze_cv(pdf_file, job_description: str) -> dict:
    """
    Analyse complète d'un CV par rapport à une offre.
    """
 
    # 1. Extraction PDF
    cv_text = extract_text_from_pdf(pdf_file)
 
    # 2. Nettoyage
    cv_text = clean_text(cv_text)
    job_text = clean_text(job_description)
 
    # 3. Extraction des informations du candidat
    candidate = extract_candidate_info(cv_text)
 
    # 4. Extraction des compétences
    cv_skills = extract_skills(cv_text)
    job_skills = extract_skills(job_text)
 
    # 5. Comparaison des compétences
    matched_skills, missing_skills = compare_skills(
        cv_skills,
        job_skills
    )
 
    # 6. Score sémantique
    match_score = calculate_match_score(
        cv_text,
        job_text
    )
 
    # 7. Recommandations
    recommendations = generate_recommendations(
        matched_skills,
        missing_skills,
        match_score
    )
 
    # 8. Résultat final
    return {
        "candidate": candidate,
        "skills": cv_skills,
        "job_skills": job_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_score": match_score,
        "recommendations": recommendations
    }
 
 
def generate_recommendations(
    matched_skills: list[str],
    missing_skills: list[str],
    match_score: int
) -> list[str]:
 
    recommendations = []
 
    if missing_skills:
        recommendations.append(
            "Highlight the skills that match the job "
            "requirements more clearly."
        )
 
    if matched_skills:
        recommendations.append(
            "Emphasize concrete experience related to the "
            "skills the employer is looking for."
        )
 
    if match_score < LOW_MATCH_THRESHOLD:
        recommendations.append(
            "The resume shows limited alignment with the job "
            "posting. Review which skills and experience are "
            "most relevant and make them more visible."
        )
 
    elif match_score < MODERATE_MATCH_THRESHOLD:
        recommendations.append(
            "The resume shows a partial match. Strengthen the "
            "sections directly related to this role."
        )
 
    else:
        recommendations.append(
            "The resume shows a strong semantic match with "
            "the job posting."
        )
 
    return recommendations
 