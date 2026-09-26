import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
SKILLS_FILE = BASE_DIR / "data" / "skills.json"


def load_skills() -> list[str]:
    """
    Charge toutes les compétences depuis skills.json.
    """

    with open(SKILLS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    skills = []

    for category_skills in data.values():
        skills.extend(category_skills)

    return skills


def normalize_apostrophes(text: str) -> str:
    """
    Uniformise les différents types d'apostrophes (typographique
    ’, courbe ‘, etc.) vers une apostrophe simple '.

    Les CV copiés depuis Word/Google Docs utilisent souvent
    l'apostrophe typographique (’), ce qui empêchait de détecter
    des compétences comme "travail d'équipe" écrites avec une
    apostrophe différente de celle stockée dans skills.json.
    """

    return (
        text
        .replace("’", "'")
        .replace("‘", "'")
        .replace("`", "'")
    )


def extract_skills(text: str) -> list[str]:
    """
    Recherche les compétences connues dans un texte.
    """

    if not text:
        return []

    found_skills = []

    text_lower = normalize_apostrophes(text.lower())

    for skill in load_skills():

        skill_normalized = normalize_apostrophes(skill.lower())

        pattern = r"\b" + re.escape(skill_normalized) + r"\b"

        if re.search(pattern, text_lower):
            found_skills.append(skill)

    return sorted(found_skills)