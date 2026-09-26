from app.services.pdf_extractor import extract_text_from_pdf
from app.services.text_cleaner import clean_text
from app.services.skill_extractor import extract_skills
from app.services.candidate_extractor import extract_candidate_info
from app.services.matcher import (
    calculate_match_score,
    compare_skills
)


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
        match_score,
        job_skills
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
    match_score: int,
    job_skills: list[str]
) -> list[str]:

    recommendations = []

    if not job_skills:
        recommendations.append(
            "Aucune compétence connue n'a été reconnue dans "
            "l'offre d'emploi. Le référentiel actuel ne couvre "
            "peut-être pas ce secteur, et le score de "
            "compatibilité peut donc être moins fiable ici."
        )

    if missing_skills:
        recommendations.append(
            "Mettre davantage en avant les compétences "
            "correspondant aux exigences de l'offre."
        )

    if matched_skills:
        recommendations.append(
            "Valoriser les expériences concrètes associées "
            "aux compétences recherchées."
        )

    if match_score < 50:
        recommendations.append(
            "Le CV présente une correspondance limitée avec "
            "l'offre. Vérifier les compétences et expériences "
            "pertinentes à mettre en évidence."
        )

    elif match_score < 75:
        recommendations.append(
            "Le CV présente une correspondance partielle. "
            "Renforcer les éléments directement liés au poste."
        )

    else:
        recommendations.append(
            "Le CV présente une bonne correspondance sémantique "
            "avec l'offre."
        )

    return recommendations

