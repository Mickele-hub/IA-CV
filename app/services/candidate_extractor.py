import re


def extract_email(text: str) -> str | None:
    """
    Extrait la première adresse email trouvée.
    """

    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

    match = re.search(pattern, text)

    if match:
        return match.group(0)

    return None


def extract_phone(text: str) -> str | None:
    """
    Extrait un numéro de téléphone en évitant les années
    et les périodes comme '2024 - 2023'.
    """

    patterns = [
        # Numéros internationaux :
        # +261 34 12 345 67
        # +33 6 12 34 56 78
        r"\+\d{1,3}[\s.-]?(?:\d[\s.-]?){7,12}",

        # Numéros avec préfixe local :
        # 034 12 345 67
        # 032 12 345 67
        r"\b0\d{2}[\s.-]?(?:\d[\s.-]?){6,9}\b",

        # Format générique type 123-456-7890 ou 123.456.7890
        r"\b\d{3}[\s.-]\d{3}[\s.-]\d{4}\b"
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text)

        for match in matches:

            # Nettoyage
            phone = re.sub(r"\s+", " ", match).strip()

            # Compter uniquement les chiffres
            digits = re.sub(r"\D", "", phone)

            # Un vrai téléphone doit généralement avoir
            # au moins 9 chiffres.
            if len(digits) >= 9:

                # Éviter les années/périodes
                if re.fullmatch(r"\d{4}\s*[-–]\s*\d{4}", phone):
                    continue

                return phone

    return None


def extract_name(text: str) -> str | None:
    """
    Tente d'extraire le nom du candidat.

    Cette fonction cherche d'abord les lignes contenant
    des indicateurs comme 'Nom', 'Name', etc.

    Si aucun indicateur n'est trouvé, elle utilise une
    heuristique sur les premières lignes du CV.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # --------------------------------------------------
    # 1. Recherche explicite
    # --------------------------------------------------

    name_patterns = [
        r"^(?:nom|name|full name)\s*[:\-]\s*(.+)$",
        r"^(?:nom complet)\s*[:\-]\s*(.+)$"
    ]

    for line in lines[:30]:

        for pattern in name_patterns:

            match = re.search(
                pattern,
                line,
                re.IGNORECASE
            )

            if match:
                name = match.group(1).strip()

                if is_valid_name(name):
                    return name

    # --------------------------------------------------
    # 2. Heuristique sur les premières lignes
    # --------------------------------------------------

    ignored_keywords = [
        "curriculum",
        "curriculum vitae",
        "resume",
        "cv",
        "profil",
        "profile",
        "compétence",
        "competence",
        "compétences",
        "competences",
        "formation",
        "education",
        "expérience",
        "experience",
        "développement",
        "developpement",
        "développement mobile",
        "developpement mobile",
        "développement web",
        "developpement web",
        "contact",
        "objectif",
        "skills",
        "languages",
        "langues",
        "projets",
        "projects"
    ]

    candidates = []

    window = lines[:20]
    i = 0

    while i < len(window):

        line = window[i]

        # Ignorer les lignes contenant des emails
        if "@" in line:
            i += 1
            continue

        # Ignorer les lignes contenant des chiffres
        if re.search(r"\d", line):
            i += 1
            continue

        # Ignorer les lignes trop longues
        if len(line) > 50:
            i += 1
            continue

        normalized = line.lower().strip()

        # Ignorer les titres connus
        if normalized in ignored_keywords:
            i += 1
            continue

        # Ignorer les lignes contenant des mots-clés
        if any(
            keyword in normalized
            for keyword in ignored_keywords
        ):
            i += 1
            continue

        words = line.split()

        # Cas normal : la ligne contient déjà 2 à 4 mots
        if 2 <= len(words) <= 4:

            if is_valid_name(line):
                candidates.append(line)
                break

        # Cas d'un nom éclaté sur deux lignes distinctes
        # (ex: "Andréa" sur une ligne, "Sanchez" sur la
        # suivante, à cause de la mise en page du CV)
        elif len(words) == 1 and i + 1 < len(window):

            next_line = window[i + 1]
            merged = f"{line} {next_line}"

            if is_valid_name(merged):
                candidates.append(merged)
                break

        i += 1

    if candidates:
        return candidates[0]

    return None


def is_valid_name(name: str) -> bool:
    """
    Vérifie si une chaîne peut raisonnablement représenter
    un nom de personne.
    """

    if not name:
        return False

    if len(name) < 3 or len(name) > 60:
        return False

    # Aucun chiffre
    if re.search(r"\d", name):
        return False

    # Aucun email
    if "@" in name:
        return False

    words = name.split()

    if not 2 <= len(words) <= 4:
        return False

    # Liste de mots qui ne sont normalement pas des noms
    forbidden = {
        "développement",
        "developpement",
        "mobile",
        "web",
        "software",
        "developer",
        "développeur",
        "développeuse",
        "engineer",
        "engineering",
        "curriculum",
        "vitae",
        "profil",
        "profile",
        "formation",
        "education",
        "expérience",
        "experience",
        "compétences",
        "competences",
        "skills",
        "contact",
        "projets",
        "projects"
    }

    for word in words:

        if word.lower().strip(".,:;-") in forbidden:
            return False

    return True


def extract_candidate_info(text: str) -> dict:
    """
    Extrait les informations principales du candidat.
    """

    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text)
    }