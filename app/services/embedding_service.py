from pathlib import Path
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parents[2]
FINETUNED_MODEL_PATH = BASE_DIR / "models" / "embedding_model"

# Modèle multilingue de secours, utilisé tant que le modèle
# fine-tuné (models/embedding_model) n'existe pas
FALLBACK_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

_model = None


def get_model():
    """
    Charge le modèle uniquement lorsqu'il est nécessaire.

    Utilise le modèle fine-tuné local s'il existe
    (models/embedding_model), sinon retombe sur le modèle
    multilingue de base.
    """

    global _model

    if _model is None:

        if FINETUNED_MODEL_PATH.exists():
            _model = SentenceTransformer(str(FINETUNED_MODEL_PATH))
        else:
            print(
                f"⚠️  {FINETUNED_MODEL_PATH} introuvable, "
                f"utilisation du modèle de base '{FALLBACK_MODEL_NAME}'."
            )
            _model = SentenceTransformer(FALLBACK_MODEL_NAME)

    return _model


def generate_embedding(text: str):
    """
    Transforme un texte en vecteur.
    """

    model = get_model()

    return model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True
    )