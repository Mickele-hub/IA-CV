from sklearn.metrics.pairwise import cosine_similarity

from app.services.embedding_service import generate_embedding


def calculate_similarity(cv_text: str, job_text: str) -> float:
    """
    Calcule la similarité sémantique entre le CV et l'offre.
    """

    if not cv_text or not job_text:
        return 0.0

    cv_embedding = generate_embedding(cv_text)
    job_embedding = generate_embedding(job_text)

    similarity = cosine_similarity(
        [cv_embedding],
        [job_embedding]
    )[0][0]

    return float(similarity)


def calculate_match_score(
    cv_text: str,
    job_text: str
) -> int:
    """
    Convertit la similarité en score de 0 à 100.
    """

    similarity = calculate_similarity(
        cv_text,
        job_text
    )

    score = round(similarity * 100)

    return max(0, min(score, 100))


def compare_skills(
    cv_skills: list[str],
    job_skills: list[str]
) -> tuple[list[str], list[str]]:
    """
    Compare les compétences du CV avec celles de l'offre.
    """

    cv_normalized = {
        skill.lower(): skill
        for skill in cv_skills
    }

    matched = []
    missing = []

    for skill in job_skills:

        if skill.lower() in cv_normalized:
            matched.append(skill)
        else:
            missing.append(skill)

    return matched, missing