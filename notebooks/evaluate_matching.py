"""
Évaluation du pipeline de matching CV/offre de SmartCV AI.

Objectif
--------
Vérifier si le score de matching produit par le pipeline (calculate_match_score)
est cohérent avec un jugement humain, en utilisant un dataset externe de CV
réels (anonymisés) associés à des classements produits par deux annotateurs
humains indépendants (recruteurs).

Dataset utilisé
----------------
"Vacancy-resume matching dataset, with human ground truth rankings"
Natalia Vanetik, Genady Kogan — https://github.com/NataliaVanetik/vacancy-resume-matching-dataset
Licence GPLv3. À citer si réutilisé :
Vanetik, N.; Kogan, G. Job Vacancy Ranking with Sentence Embeddings,
Keywords, and Named Entities. Information 2023, 14, 468.

Méthode
-------
Pour chacun des 30 premiers CV du dataset, on calcule le score de matching
du pipeline SmartCV AI contre les 5 offres d'emploi de référence, on en
déduit un classement (1 = meilleure offre selon le pipeline), et on compare
ce classement à celui des deux annotateurs humains avec la corrélation de
rang de Spearman (plus proche de 1 = meilleur accord).

On calcule aussi l'accord ENTRE les deux annotateurs humains, qui sert de
référence : un bon score du pipeline devrait s'en approcher, il est
irréaliste d'espérer le dépasser (les humains ne sont pas parfaitement
d'accord entre eux non plus).

Utilisation
-----------
1. Cloner le dataset à côté du projet (pas dans le repo Git, il est sous
   licence GPLv3 et contient des CV, même anonymisés) :

   git clone https://github.com/NataliaVanetik/vacancy-resume-matching-dataset.git ../vacancy-resume-matching-dataset

2. Lancer ce script depuis la racine du projet (là où se trouve app/) :

   python notebooks/evaluate_matching.py
"""

import csv
import json
import statistics
import sys
from pathlib import Path

import docx
from scipy.stats import spearmanr

# Ajoute la racine du projet (dossier parent de notebooks/) au chemin Python,
# pour que "from app.services.matcher import ..." fonctionne quel que soit
# l'endroit d'où ce script est lancé.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.matcher import calculate_match_score, calculate_combined_score
from app.services.skill_extractor import extract_skills


DATASET_DIR = Path(__file__).resolve().parent.parent.parent / "vacancy-resume-matching-dataset"

# Classements de référence produits par 2 annotateurs humains (recruteurs),
# pour les CV 1 à 30, contre les 5 offres du fichier 5_vacancies.csv.
# 1 = meilleure offre pour ce CV selon l'annotateur, 5 = la moins adaptée.
ANNOTATOR_1 = [[2,1,4,3,5],[1,2,3,4,5],[1,2,3,4,5],[3,1,2,4,5],[1,5,4,2,3],
       [3,2,1,4,5],[3,2,1,5,4],[2,4,3,1,5],[1,5,2,1,4],[3,2,1,4,5],
       [1,2,3,4,5],[1,2,3,4,5],[1,3,2,4,5],[1,2,3,4,5],[3,1,2,4,5],
       [3,1,2,4,5],[3,1,2,4,5],[1,2,5,3,4],[3,2,1,4,5],[3,2,1,4,5],
       [2,3,1,4,5],[1,2,3,5,4],[2,1,3,5,4],[1,2,3,5,4],[1,2,3,4,5],
       [2,1,3,4,5],[2,3,4,5,1],[2,4,3,2,5],[5,1,2,4,3],[2,1,4,3,5]]

ANNOTATOR_2 = [[4,3,1,5,2],[2,4,3,1,5],[5,4,2,3,1],[1,3,2,4,5],[5,1,2,4,3],
        [1,3,2,4,5],[4,2,3,1,5],[2,4,3,1,5],[3,4,2,1,5],[4,1,2,5,3],
        [2,4,3,5,1],[4,3,2,1,5],[4,2,3,1,5],[3,4,2,1,5],[2,4,3,1,5],
        [3,2,4,1,5],[4,2,3,1,5],[4,2,5,3,1],[4,2,3,1,5],[1,5,2,4,3],
        [1,3,4,5,2],[4,1,3,2,5],[1,3,4,2,5],[1,4,3,5,2],[1,4,2,5,3],
        [1,5,2,4,3],[4,3,1,2,5],[1,4,2,3,5],[5,1,2,4,3],[1,2,3,4,5]]


def read_docx(path):
    document = docx.Document(path)
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def load_jobs():
    jobs = []
    with open(DATASET_DIR / "5_vacancies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            jobs.append(row["job_description"])
    return jobs


def run_evaluation():
    jobs = load_jobs()
    results = []

    for cv_index in range(1, 31):
        cv_path = DATASET_DIR / "CV" / f"{cv_index}.docx"
        cv_text = read_docx(cv_path)

        if not cv_text.strip():
            print(f"CV {cv_index} vide, ignoré")
            continue

        cv_skills = extract_skills(cv_text)

        scores = [calculate_match_score(cv_text, job_text) for job_text in jobs]

        combined_scores = [
            calculate_combined_score(
                cv_text, job_text,
                cv_skills, extract_skills(job_text)
            )
            for job_text in jobs
        ]

        # Score -> classement (1 = meilleur score)
        order = sorted(range(5), key=lambda i: -scores[i])
        model_rank = [0] * 5
        for rank, job_i in enumerate(order, start=1):
            model_rank[job_i] = rank

        combined_order = sorted(range(5), key=lambda i: -combined_scores[i])
        combined_rank = [0] * 5
        for rank, job_i in enumerate(combined_order, start=1):
            combined_rank[job_i] = rank

        human_1 = ANNOTATOR_1[cv_index - 1]
        human_2 = ANNOTATOR_2[cv_index - 1]

        corr_1, _ = spearmanr(model_rank, human_1)
        corr_2, _ = spearmanr(model_rank, human_2)
        combined_corr_1, _ = spearmanr(combined_rank, human_1)
        combined_corr_2, _ = spearmanr(combined_rank, human_2)
        inter_annotator, _ = spearmanr(human_1, human_2)

        results.append({
            "cv": cv_index,
            "scores": scores,
            "model_rank": model_rank,
            "combined_scores": combined_scores,
            "combined_rank": combined_rank,
            "human_1": human_1,
            "human_2": human_2,
            "corr_model_vs_annotator1": corr_1,
            "corr_model_vs_annotator2": corr_2,
            "combined_corr_vs_annotator1": combined_corr_1,
            "combined_corr_vs_annotator2": combined_corr_2,
            "inter_annotator_agreement": inter_annotator,
        })

        print(
            f"CV {cv_index:2d} | semantique={[round(s) for s in scores]} rho={corr_1:.2f}/{corr_2:.2f} "
            f"| combine={[round(s) for s in combined_scores]} rho={combined_corr_1:.2f}/{combined_corr_2:.2f}"
        )

    output_path = Path(__file__).resolve().parent / "eval_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    mean_corr1 = statistics.mean(r["corr_model_vs_annotator1"] for r in results)
    mean_corr2 = statistics.mean(r["corr_model_vs_annotator2"] for r in results)
    mean_combined_corr1 = statistics.mean(r["combined_corr_vs_annotator1"] for r in results)
    mean_combined_corr2 = statistics.mean(r["combined_corr_vs_annotator2"] for r in results)
    mean_inter = statistics.mean(r["inter_annotator_agreement"] for r in results)

    print()
    print("=== RÉSULTATS AGRÉGÉS ===")
    print(f"CV évalués                                            : {len(results)}")
    print(f"[Sémantique seul]  corrélation vs Annotateur 1        : {mean_corr1:.3f}")
    print(f"[Sémantique seul]  corrélation vs Annotateur 2        : {mean_corr2:.3f}")
    print(f"[Score combiné]    corrélation vs Annotateur 1        : {mean_combined_corr1:.3f}")
    print(f"[Score combiné]    corrélation vs Annotateur 2        : {mean_combined_corr2:.3f}")
    print(f"Accord inter-annotateurs (référence)                  : {mean_inter:.3f}")
    print()
    print(f"Résultats détaillés sauvegardés dans : {output_path}")


if __name__ == "__main__":
    run_evaluation()
