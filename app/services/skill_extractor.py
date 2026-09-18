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


def extract_skills(text: str) -> list[str]:
    """
    Recherche les compétences connues dans un texte.
    """

    if not text:
        return []

    found_skills = []

    text_lower = text.lower()

    for skill in load_skills():

        pattern = r"\b" + re.escape(skill.lower()) + r"\b"

        if re.search(pattern, text_lower):
            found_skills.append(skill)

    return sorted(found_skills)