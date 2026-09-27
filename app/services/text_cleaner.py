import re


def collapse_repeated_token(token: str) -> str:
    """
    Corrige les artefacts de rendu où un mot est dupliqué
    plusieurs fois consécutivement sans séparateur
    (ex: 'AndréaAndréaAndréa' -> 'Andréa'), causés par un
    effet de gras synthétique (texte redessiné 2-3 fois)
    dans certains templates PDF.
    """

    length = len(token)

    # On ignore les tokens trop courts pour éviter de
    # collapser des répétitions légitimes (ex: "ll", "oo")
    if length < 6:
        return token

    for period in range(3, length // 2 + 1):

        if length % period != 0:
            continue

        repeat_count = length // period

        if repeat_count < 2:
            continue

        candidate = token[:period]

        if candidate * repeat_count == token:
            return candidate

    return token


def clean_repeated_words(text: str) -> str:
    """
    Applique collapse_repeated_token à chaque mot du texte,
    ligne par ligne, en préservant les retours à la ligne.
    """

    return "\n".join(
        " ".join(
            collapse_repeated_token(word)
            for word in line.split(" ")
        )
        for line in text.splitlines()
    )


def clean_text(text: str) -> str:
    """
    Nettoie le texte extrait du CV.
    """

    if not text:
        return ""

    # Corriger les mots dupliqués (artefact de rendu PDF),
    # avant tout autre nettoyage, tant que les mots sont
    # encore collés tels qu'extraits
    text = clean_repeated_words(text)

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
