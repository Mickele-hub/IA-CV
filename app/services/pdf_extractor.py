import fitz


def extract_text_from_pdf(pdf_file) -> str:
    """
    Extrait le texte contenu dans un fichier PDF.

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
        text += page.get_text("text", sort=True)

    document.close()

    return text