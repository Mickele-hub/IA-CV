"""
Fixtures partagées par tous les tests. pytest découvre ce
fichier automatiquement s'il est placé dans tests/.
"""
 
from pathlib import Path
 
import pytest
 
 
FIXTURES_DIR = Path(__file__).parent / "fixtures"
 
 
@pytest.fixture
def harper_russo_pdf_path() -> Path:
    """
    Chemin vers le CV de test 'Harper Russo' (profil web
    developer). Doit être présent dans tests/fixtures/.
    """
 
    path = FIXTURES_DIR / "Black and White Simple CV Resume.pdf"
 
    if not path.exists():
        pytest.skip(
            f"Fixture manquante : {path}. Copie le CV dans "
            "tests/fixtures/ pour activer ce test."
        )
 
    return path
 
 
@pytest.fixture
def richard_sanchez_marketing_pdf_path() -> Path:
    """
    Chemin vers le CV de test 'Richard Sanchez' (profil
    marketing manager). Doit être présent dans tests/fixtures/.
    """
 
    path = FIXTURES_DIR / "Blue and Gray Simple Professional CV Resume.pdf"
 
    if not path.exists():
        pytest.skip(
            f"Fixture manquante : {path}. Copie le CV dans "
            "tests/fixtures/ pour activer ce test."
        )
 
    return path
