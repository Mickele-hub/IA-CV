import io

import pytest

from app.services.pdf_extractor import extract_text_from_pdf


def test_extract_text_from_pdf_path(sample_cv_path):
    """
    L'extraction depuis un chemin de fichier doit renvoyer
    le texte contenu dans le PDF.
    """
    text = extract_text_from_pdf(str(sample_cv_path))

    assert isinstance(text, str)
    assert len(text) > 0
    assert "Andrea" in text
    assert "andrea.sanchez@example.com" in text


def test_extract_text_from_pdf_file_object(sample_cv_path):
    """
    L'extraction doit aussi fonctionner avec un objet fichier
    (ce que FastAPI fournit via UploadFile.file), pas
    seulement avec un chemin.
    """
    with open(sample_cv_path, "rb") as pdf_file:
        text = extract_text_from_pdf(pdf_file)

    assert "Andrea" in text
    assert "Python" in text


def test_extract_text_from_invalid_pdf_raises():
    """
    Un fichier qui n'est pas un vrai PDF doit lever une
    erreur exploitable plutôt que planter silencieusement
    ou renvoyer un texte vide sans prévenir.
    """
    fake_file = io.BytesIO(b"ceci n'est pas un pdf valide")

    with pytest.raises(Exception):
        extract_text_from_pdf(fake_file)
