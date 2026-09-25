"""
Tests pour app.services.matcher.
 
Plutôt que de figer des valeurs de score exactes (fragile —
un score peut légèrement varier si le modèle est réentraîné),
ces tests vérifient une propriété plus robuste : un bon match
doit toujours scorer nettement plus haut qu'un mauvais match,
pour le même CV.
 
Lancer : pytest tests/test_matcher.py -v
"""
 
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.text_cleaner import clean_text
from app.services.matcher import calculate_match_score, compare_skills
 
 
# Marge minimale exigée entre un bon et un mauvais match. Basé
# sur l'observation empirique (scripts/evaluate_scores.py) :
# bons matchs 36-66, mauvais matchs 15-23 → un écart d'au moins
# 10 points est une exigence prudente, sous la marge réelle
# observée.
MIN_SCORE_GAP = 10
 
 
def _get_cv_text(pdf_path) -> str:
    with open(pdf_path, "rb") as file:
        raw_text = extract_text_from_pdf(file)
    return clean_text(raw_text)
 
 
# --------------------------------------------------------
# calculate_match_score — cas limites
# --------------------------------------------------------
 
def test_calculate_match_score_empty_cv_returns_zero():
    score = calculate_match_score("", "Some job description")
    assert score == 0
 
 
def test_calculate_match_score_empty_job_returns_zero():
    score = calculate_match_score("Some cv text", "")
    assert score == 0
 
 
def test_calculate_match_score_is_between_0_and_100():
    score = calculate_match_score(
        "Experienced Python developer",
        "Looking for a Python developer"
    )
    assert 0 <= score <= 100
 
 
# --------------------------------------------------------
# calculate_match_score — discrimination bon vs mauvais match
# --------------------------------------------------------
 
def test_harper_russo_scores_higher_on_matching_job(harper_russo_pdf_path):
    cv_text = _get_cv_text(harper_russo_pdf_path)
 
    good_job = clean_text(
        "We are looking for a web developer with experience in "
        "front-end coding, database administration and website "
        "design. Strong problem-solving and communication skills "
        "required."
    )
    bad_job = clean_text(
        "We are looking for a marketing manager to develop and "
        "execute marketing strategies, manage a team, and monitor "
        "brand consistency across channels."
    )
 
    good_score = calculate_match_score(cv_text, good_job)
    bad_score = calculate_match_score(cv_text, bad_job)
 
    assert good_score > bad_score + MIN_SCORE_GAP
 
 
def test_richard_sanchez_marketing_scores_higher_on_matching_job(
    richard_sanchez_marketing_pdf_path
):
    cv_text = _get_cv_text(richard_sanchez_marketing_pdf_path)
 
    good_job = clean_text(
        "We are looking for a marketing manager to develop and "
        "execute comprehensive marketing strategies, lead a team, "
        "manage budget and monitor brand consistency across "
        "channels."
    )
    bad_job = clean_text(
        "We are looking for a product designer with strong skills "
        "in design process, creativity and project management."
    )
 
    good_score = calculate_match_score(cv_text, good_job)
    bad_score = calculate_match_score(cv_text, bad_job)
 
    assert good_score > bad_score + MIN_SCORE_GAP
 
 
# --------------------------------------------------------
# compare_skills
# --------------------------------------------------------
 
def test_compare_skills_matches_common_skills():
    cv_skills = ["Python", "Docker", "FastAPI"]
    job_skills = ["Python", "PostgreSQL"]
 
    matched, missing = compare_skills(cv_skills, job_skills)
 
    assert matched == ["Python"]
    assert missing == ["PostgreSQL"]
 
 
def test_compare_skills_case_insensitive():
    cv_skills = ["python"]
    job_skills = ["Python"]
 
    matched, missing = compare_skills(cv_skills, job_skills)
 
    assert matched == ["Python"]
    assert missing == []
 
 
def test_compare_skills_empty_job_skills():
    matched, missing = compare_skills(["Python"], [])
 
    assert matched == []
    assert missing == []
 