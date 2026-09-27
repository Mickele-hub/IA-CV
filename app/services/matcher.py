import re

from sklearn.metrics.pairwise import cosine_similarity

from app.services.embedding_service import generate_embedding
from app.services.skill_extractor import load_skills


# Mots-clés génériques indiquant qu'une phrase parle probablement
# des compétences/exigences du poste plutôt que d'avantages sociaux,
# de mentions légales ou de présentation d'entreprise.
RELEVANT_KEYWORDS = [
    "experience", "skill", "require", "proficien", "knowledge",
    "responsib", "qualification", "degree", "develop", "years",
    "compétence", "expérience", "exigé", "requis", "maîtris",
    "diplôme", "responsabilité",
]


def _sentence_relevance_score(sentence: str, skills_lower: set) -> int:
    text_lower = sentence.lower()

    score = sum(1 for kw in RELEVANT_KEYWORDS if kw in text_lower)
    score += sum(2 for skill in skills_lower if skill in text_lower)

    return score


def extract_relevant_excerpt(text: str, max_chars: int = 1200) -> str:
    """
    Réduit un texte long à ses phrases les plus pertinentes pour le
    poste (compétences, exigences, responsabilités), avant de
    l'envoyer au modèle sémantique.

    Pourquoi : le modèle d'embedding tronque automatiquement tout
    texte au-delà d'environ 256 tokens (~1500 caractères), en gardant
    toujours le DÉBUT du texte. Or de nombreuses offres d'emploi
    commencent par un long paragraphe marketing/accroche avant
    d'aborder les compétences requises. Dans ce cas, le modèle ne
    "voit" jamais la partie réellement utile du texte. Cette fonction
    sélectionne les phrases les plus denses en mots-clés liés aux
    compétences/exigences, pour que l'information utile soit bien
    présente dans les ~256 premiers tokens envoyés au modèle.
    """

    if not text or len(text) <= max_chars:
        return text

    skills_lower = {skill.lower() for skill in load_skills()}

    sentences = re.split(r"(?<=[.!?])\s+", text)

    scored = [
        (index, sentence, _sentence_relevance_score(sentence, skills_lower))
        for index, sentence in enumerate(sentences)
    ]

    best_first = sorted(scored, key=lambda item: -item[2])

    chosen = {}
    total_length = 0

    for index, sentence, _score in best_first:

        remaining = max_chars - total_length

        if remaining <= 0:
            break

        if len(sentence) <= remaining:
            chosen[index] = sentence
            total_length += len(sentence)
        elif not chosen:
            # Aucune phrase choisie pour l'instant, et la phrase la
            # plus pertinente dépasse à elle seule le budget entier :
            # on la tronque plutôt que de l'ignorer, car elle reste la
            # plus riche en informations utiles (compétences, exigences).
            chosen[index] = sentence[:remaining]
            total_length = max_chars
            break

    if not chosen:
        return text[:max_chars]

    return " ".join(chosen[index] for index in sorted(chosen))


def calculate_similarity(cv_text: str, job_text: str) -> float:
    """
    Calcule la similarité sémantique entre le CV et l'offre.
    """

    if not cv_text or not job_text:
        return 0.0

    cv_embedding = generate_embedding(extract_relevant_excerpt(cv_text))
    job_embedding = generate_embedding(extract_relevant_excerpt(job_text))

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


def calculate_skill_overlap_score(
    cv_skills: list[str],
    job_skills: list[str]
) -> int:
    """
    Calcule un score de 0 à 100 basé sur la proportion des
    compétences requises par l'offre qui sont présentes dans le CV.

    Contrairement au score sémantique (calculate_match_score), qui
    compare le texte dans son ensemble, ce score se base uniquement
    sur les compétences explicitement détectées par
    skill_extractor.extract_skills — moins sensible au bruit
    textuel (texte marketing, mentions légales) qui peut fausser la
    similarité sémantique globale.
    """

    if not job_skills:
        return 0

    matched, _missing = compare_skills(cv_skills, job_skills)

    ratio = len(matched) / len(job_skills)

    return round(ratio * 100)


def calculate_combined_score(
    cv_text: str,
    job_text: str,
    cv_skills: list[str],
    job_skills: list[str],
    semantic_weight: float = 0.5
) -> int:
    """
    Combine le score sémantique et le score de recouvrement de
    compétences en une seule note de 0 à 100.

    semantic_weight contrôle le poids du score sémantique (le reste
    va au score de recouvrement de compétences). Un score combiné
    vise à être plus robuste que le score sémantique seul face à du
    texte bruyant, tout en gardant la capacité du modèle sémantique
    à repérer des synonymes/formulations différentes que
    skill_extractor ne connaît pas.
    """

    semantic_score = calculate_match_score(cv_text, job_text)
    skill_score = calculate_skill_overlap_score(cv_skills, job_skills)

    combined = (
        semantic_weight * semantic_score
        + (1 - semantic_weight) * skill_score
    )

    return round(combined)


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