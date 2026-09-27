from app.services.skill_extractor import extract_skills


def test_extract_skills_detects_technical_and_soft_skills():
    text = (
        "Développeuse Python avec de bonnes compétences en "
        "communication et en travail d'équipe."
    )

    skills = extract_skills(text)

    assert "Python" in skills
    assert "Communication" in skills
    assert "Travail d'équipe" in skills


def test_extract_skills_handles_curly_apostrophe():
    # Le CV utilise une apostrophe typographique (’),
    # skills.json utilise une apostrophe simple (').
    text = "J’ai un fort sens de l’initiative."

    skills = extract_skills(text)

    assert "Sens de l'initiative" in skills


def test_extract_skills_no_match_returns_empty_list():
    text = "Ceci est un texte sans aucune compétence connue."

    assert extract_skills(text) == []


def test_extract_skills_empty_text_returns_empty_list():
    assert extract_skills("") == []
