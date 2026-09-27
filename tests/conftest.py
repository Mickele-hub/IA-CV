from pathlib import Path

import pytest


TESTS_DIR = Path(__file__).resolve().parent
SAMPLE_CV_PATH = TESTS_DIR / "sample_cv.pdf"


@pytest.fixture
def sample_cv_path() -> Path:
    """
    Chemin vers un CV PDF factice utilisé dans plusieurs tests.

    Contenu du CV (voir sample_cv.pdf) :
    - Nom : Andrea Sanchez
    - Email : andrea.sanchez@example.com
    - Téléphone : +33 6 12 34 56 78
    - Compétences : Python, JavaScript, React, Docker, PostgreSQL
    """
    return SAMPLE_CV_PATH


@pytest.fixture
def sample_job_description() -> str:
    """
    Offre d'emploi factice, avec des compétences qui
    chevauchent partiellement celles du CV de test :
    Python et React sont dans le CV, Django et AWS non.
    """
    return (
        "Nous recherchons un développeur Python avec une "
        "expérience en React, Django et AWS."
    )
