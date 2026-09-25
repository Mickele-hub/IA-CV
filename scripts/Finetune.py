"""
Fine-tune le modèle d'embedding en mélangeant :
- les paires françaises construites à la main
  (data/training/embedding_pairs.jsonl), sur-échantillonnées
  pour peser face au volume anglais
- un sous-ensemble du dataset anglais public, pour garder du
  volume sans diluer complètement l'apport du français
 
Corrige le problème du premier entraînement (100% anglais, 4
epochs), qui avait dégradé les performances du modèle en
français (catastrophic forgetting).
 
Utilisation (depuis la racine du projet) :
    python scripts/finetune_v2.py
"""
 
import json
import sys
from pathlib import Path
 
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
 
from datasets import Dataset, load_dataset
from sentence_transformers import (
    SentenceTransformer,
    SentenceTransformerTrainer,
    SentenceTransformerTrainingArguments,
    losses,
)
 
 
FR_PAIRS_PATH = Path("data/training/raw_pairs.json")
OUTPUT_PATH = "models/embedding_model_v2"
 
LABEL_MAP = {"No Fit": 0.0, "Potential Fit": 0.5, "Good Fit": 1.0}
 
# Combien de fois répéter chaque paire française, pour qu'elle
# pèse davantage face au volume anglais. À ajuster : plus ce
# nombre est haut, plus le modèle se spécialise sur tes propres
# exemples (risque de sur-apprentissage si trop haut vu le peu
# de paires françaises).
FR_OVERSAMPLE_FACTOR = 8
 
# Nombre de lignes anglaises à garder (sur les ~6241 disponibles).
# Réduit par rapport à l'entraînement précédent (qui utilisait
# tout le dataset) pour laisser plus de poids relatif au français.
EN_SAMPLE_SIZE = 1000
 
 
def load_fr_pairs() -> list[dict]:
    if not FR_PAIRS_PATH.exists():
        print(
            f"⚠️  {FR_PAIRS_PATH} introuvable. Lance d'abord "
            "scripts/build_dataset.py pour créer des paires."
        )
        sys.exit(1)
 
    with open(FR_PAIRS_PATH, encoding="utf-8") as file:
        rows = json.load(file)
 
    missing_label = [row for row in rows if "label" not in row]
 
    if missing_label:
        print(
            f"⚠️  {len(missing_label)} paire(s) sans label trouvée(s) "
            f"dans {FR_PAIRS_PATH} (créées avec une ancienne version "
            "du script ?). Elles seront ignorées."
        )
        rows = [row for row in rows if "label" in row]
 
    return rows
 
 
def main() -> None:
    fr_rows = load_fr_pairs()
    print(f"{len(fr_rows)} paire(s) française(s) chargée(s).")
 
    fr_rows_boosted = fr_rows * FR_OVERSAMPLE_FACTOR
    print(
        f"→ {len(fr_rows_boosted)} paire(s) après "
        f"sur-échantillonnage (x{FR_OVERSAMPLE_FACTOR})."
    )
 
    print("Téléchargement / chargement du dataset anglais...")
    en_ds = load_dataset("cnamuangtoun/resume-job-description-fit")["train"]
    en_ds = en_ds.shuffle(seed=42).select(
        range(min(EN_SAMPLE_SIZE, len(en_ds)))
    )
    print(f"→ {len(en_ds)} ligne(s) anglaise(s) retenue(s).")
 
    sentence1 = (
        [row["cv_text"] for row in fr_rows_boosted]
        + list(en_ds["resume_text"])
    )
    sentence2 = (
        [row["job_text"] for row in fr_rows_boosted]
        + list(en_ds["job_description_text"])
    )
    score = (
        [LABEL_MAP[row["label"]] for row in fr_rows_boosted]
        + [LABEL_MAP[label] for label in en_ds["label"]]
    )
 
    train_dataset = Dataset.from_dict({
        "sentence1": sentence1,
        "sentence2": sentence2,
        "score": score,
    })
 
    print(f"Dataset d'entraînement total : {len(train_dataset)} lignes.")
 
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    train_loss = losses.CosineSimilarityLoss(model)
 
    args = SentenceTransformerTrainingArguments(
        output_dir=OUTPUT_PATH,
        num_train_epochs=2,
        per_device_train_batch_size=16,
        warmup_steps=50,
    )
 
    trainer = SentenceTransformerTrainer(
        model=model,
        args=args,
        train_dataset=train_dataset,
        loss=train_loss,
    )
 
    trainer.train()
    model.save(OUTPUT_PATH)
 
    print(f"\n✅ Modèle sauvegardé dans {OUTPUT_PATH}")
    print(
        "Étape suivante : pointe temporairement embedding_service.py "
        "vers ce dossier et relance scripts/evaluate_scores.py pour "
        "comparer au modèle de base avant de le mettre en production."
    )
 
 
if __name__ == "__main__":
    main()
 