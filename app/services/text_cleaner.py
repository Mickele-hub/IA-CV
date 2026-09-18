import re


def clean_text(text: str) -> str:
    """
    Nettoie le texte extrait du CV.
    """

    if not text:
        return ""

    # Remplacer les retours à la ligne multiples
    text = re.sub(r"\n+", "\n", text)

    # Supprimer les espaces multiples
    text = re.sub(r"[ \t]+", " ", text)

    # Supprimer les espaces au début et à la fin
    text = text.strip()

    return text


def normalize_text(text: str) -> str:
    """
    Normalise le texte pour faciliter les comparaisons.
    """

    text = clean_text(text)

    return text.lower()