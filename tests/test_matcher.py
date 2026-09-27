import numpy as np
import pytest

from app.services.matcher import (
    calculate_match_score,
    calculate_similarity,
    compare_skills,
)


def fake_embedding(text: str):
    """
    Remplace le vrai modèle sentence-transformers par un
    faux embedding déterministe, pour tester la logique de
    matcher.py sans charger un modèle ML (lourd et lent) à
    chaque exécution des tests. Deux textes identiques
    donnent le même vecteur ; des textes différents donnent
    des vecteurs différents.
    """
    vector = np.zeros(8)

    for index, char in enumerate(text[:8]):
        vector[index] = ord(char)

    norm = np.linalg.norm(vector)

    return vector / norm if norm > 0 else vector


def test_calculate_similarity_identical_texts(monkeypatch):
    monkeypatch.setattr(
        "app.services.matcher.generate_embedding",
        fake_embedding,
    )

    similarity = calculate_similarity("Python developer", "Python developer")

    assert similarity == pytest.approx(1.0)


def test_calculate_similarity_empty_text_returns_zero():
    assert calculate_similarity("", "Python developer") == 0.0
    assert calculate_similarity("Python developer", "") == 0.0
    assert calculate_similarity("", "") == 0.0


def test_calculate_match_score_is_between_0_and_100(monkeypatch):
    monkeypatch.setattr(
        "app.services.matcher.generate_embedding",
        fake_embedding,
    )

    score = calculate_match_score("Python developer", "Java developer")

    assert isinstance(score, int)
    assert 0 <= score <= 100


def test_calculate_match_score_identical_texts_is_100(monkeypatch):
    monkeypatch.setattr(
        "app.services.matcher.generate_embedding",
        fake_embedding,
    )

    score = calculate_match_score("Python React Docker", "Python React Docker")

    assert score == 100


def test_compare_skills_splits_matched_and_missing():
    cv_skills = ["Python", "React", "Docker"]
    job_skills = ["Python", "Django", "React", "AWS"]

    matched, missing = compare_skills(cv_skills, job_skills)

    assert matched == ["Python", "React"]
    assert missing == ["Django", "AWS"]


def test_compare_skills_is_case_insensitive():
    cv_skills = ["python", "REACT"]
    job_skills = ["Python", "React"]

    matched, missing = compare_skills(cv_skills, job_skills)

    assert matched == ["Python", "React"]
    assert missing == []


def test_compare_skills_no_overlap():
    cv_skills = ["Python"]
    job_skills = ["Java", "Kotlin"]

    matched, missing = compare_skills(cv_skills, job_skills)

    assert matched == []
    assert missing == ["Java", "Kotlin"]

