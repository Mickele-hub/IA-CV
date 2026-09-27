import fitz


def _find_column_boundary(words, page_width):
    """
    Détecte dynamiquement la frontière entre 2 colonnes en
    cherchant le plus grand espace vide horizontal (gouttière)
    entre les positions de départ des mots.
    """

    xs = sorted(set(round(w[0]) for w in words))

    candidates = [
        x for x in xs
        if page_width * 0.15 <= x <= page_width * 0.6
    ]

    if len(candidates) < 2:
        return page_width / 2

    best_gap = 0
    boundary = page_width / 2

    for i in range(1, len(candidates)):
        gap = candidates[i] - candidates[i - 1]
        if gap > best_gap:
            best_gap = gap
            boundary = (candidates[i] + candidates[i - 1]) / 2

    return boundary


def _group_words_into_lines(words):
    """
    Regroupe une liste de mots (avec position) en lignes de texte,
    en utilisant les numéros de bloc/ligne fournis nativement par
    PyMuPDF plutôt qu'une tolérance verticale approximative (qui
    peut casser selon l'interligne propre à chaque mise en page).
    """

    # Chaque mot : (x0, y0, x1, y1, "mot", block_no, line_no, word_no)
    words = sorted(words, key=lambda w: (w[5], w[6], w[0]))

    lines = {}

    for word in words:
        key = (word[5], word[6])
        lines.setdefault(key, []).append(word)

    text_lines = []

    for key in sorted(lines.keys()):
        line_words = sorted(lines[key], key=lambda w: w[0])
        text_lines.append(" ".join(w[4] for w in line_words))

    return "\n".join(text_lines)


def extract_text_from_pdf(pdf_file) -> str:
    """
    Extrait le texte contenu dans un fichier PDF.

    Détecte automatiquement une éventuelle mise en page à
    2 colonnes et traite chaque colonne séparément, pour
    éviter que le texte des deux colonnes ne se mélange.

    Args:
        pdf_file: chemin vers le fichier PDF ou objet fichier.

    Returns:
        Texte extrait du PDF.
    """

    if hasattr(pdf_file, "read"):
        pdf_bytes = pdf_file.read()
        document = fitz.open(stream=pdf_bytes, filetype="pdf")
    else:
        document = fitz.open(pdf_file)

    text = ""

    for page in document:
        page_width = page.rect.width

        words = page.get_text("words")

        if not words:
            continue

        boundary = _find_column_boundary(words, page_width)

        left_words = [w for w in words if w[0] < boundary]
        right_words = [w for w in words if w[0] >= boundary]

        text += _group_words_into_lines(right_words) + "\n"
        text += _group_words_into_lines(left_words) + "\n"

    document.close()

    return text