"""
Évalue le match_score du modèle fine-tuné sur une série de
paires CV/offre pré-labellisées (bon match / mauvais match),
pour recalibrer les seuils de generate_recommendations().
 
À placer dans scripts/evaluate_scores.py et lancer depuis la
racine du projet :
 
    python scripts/evaluate_scores.py
"""
 
import sys
from pathlib import Path
 
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
 
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.text_cleaner import clean_text
from app.services.matcher import calculate_match_score
 
 
# --------------------------------------------------------
# Renseigne ici tes cas de test : (description, cv, job, attendu)
# "attendu" est juste indicatif pour toi (pas utilisé par le
# calcul), ça sert à comparer visuellement au résultat obtenu.
#
# cv peut être soit un chemin vers un PDF, soit du texte brut
# directement (les deux sont gérés ci-dessous).
# --------------------------------------------------------
 
TEST_CASES = [
    {
        "description": "Harper Russo (web dev) vs offre web dev — bon match",
        "cv": "Black and White Simple CV Resume.pdf",
        "job": (
            "We are looking for a web developer with experience in "
            "front-end coding, database administration and website "
            "design. Strong problem-solving and communication skills "
            "required."
        ),
        "expected": "bon match",
        "lang": "en",
    },
    {
        "description": "Harper Russo (web dev) vs offre marketing — mauvais match",
        "cv": "Black and White Simple CV Resume.pdf",
        "job": (
            "We are looking for a marketing manager to develop and "
            "execute marketing strategies, manage a team, and monitor "
            "brand consistency across channels."
        ),
        "expected": "mauvais match",
        "lang": "en",
    },
    {
        "description": "Richard Sanchez (marketing manager) vs offre marketing — bon match",
        "cv": "Blue and Gray Simple Professional CV Resume.pdf",
        "job": (
            "We are looking for a marketing manager to develop and "
            "execute comprehensive marketing strategies, lead a team, "
            "manage budget and monitor brand consistency across "
            "channels."
        ),
        "expected": "bon match",
        "lang": "en",
    },
    {
        "description": "Richard Sanchez (marketing manager) vs offre product design — mauvais match",
        "cv": "Blue and Gray Simple Professional CV Resume.pdf",
        "job": (
            "We are looking for a product designer with strong skills "
            "in design process, creativity and project management."
        ),
        "expected": "mauvais match",
        "lang": "en",
    },
    {
        "description": "Richard Sanchez (product designer) vs offre product design — bon match",
        "cv": "Black Modern Professional Resume.pdf",
        "job": (
            "We are looking for a product designer with strong skills "
            "in design process, creativity and project management."
        ),
        "expected": "bon match",
        "lang": "en",
    },
    {
        "description": "Richard Sanchez (product designer) vs offre marketing — mauvais match",
        "cv": "Black Modern Professional Resume.pdf",
        "job": (
            "We are looking for a marketing manager to develop and "
            "execute comprehensive marketing strategies, lead a team, "
            "manage budget and monitor brand consistency across "
            "channels."
        ),
        "expected": "mauvais match",
        "lang": "en",
    },
]
 
def load_cv_text(cv_value: str) -> str:
    """
    Si cv_value pointe vers un fichier PDF existant, extrait
    son texte. Sinon, traite cv_value comme du texte brut.
    """
 
    path = Path(cv_value)
 
    if path.exists() and path.suffix.lower() == ".pdf":
        with open(path, "rb") as file:
            raw_text = extract_text_from_pdf(file)
        return clean_text(raw_text)
 
    return clean_text(cv_value)
 
 
def main() -> None:
    results = []
 
    for case in TEST_CASES:
        cv_text = load_cv_text(case["cv"])
        job_text = clean_text(case["job"])
 
        score = calculate_match_score(cv_text, job_text)
 
        results.append({
            "description": case["description"],
            "expected": case["expected"],
            "score": score,
        })
 
    print("\n=== Résultats ===\n")
 
    for row in sorted(results, key=lambda r: r["score"], reverse=True):
        print(
            f"{row['score']:>3} | {row['expected']:<15} | "
            f"{row['description']}"
        )
 
    scores_bons = [
        r["score"] for r in results if r["expected"] == "bon match"
    ]
    scores_mauvais = [
        r["score"] for r in results if r["expected"] == "mauvais match"
    ]
 
    if scores_bons and scores_mauvais:
        print("\n=== Résumé ===")
        print(
            f"Bons matchs   : min={min(scores_bons)}, "
            f"max={max(scores_bons)}, "
            f"moyenne={sum(scores_bons) / len(scores_bons):.1f}"
        )
        print(
            f"Mauvais matchs: min={min(scores_mauvais)}, "
            f"max={max(scores_mauvais)}, "
            f"moyenne={sum(scores_mauvais) / len(scores_mauvais):.1f}"
        )
        print(
            "\n➡️  Choisis un seuil 'bonne correspondance' situé "
            "entre le max des mauvais matchs et le min des bons "
            "matchs (avec de la marge des deux côtés)."
        )
 
 
if __name__ == "__main__":
    main()