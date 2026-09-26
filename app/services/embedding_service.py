from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

_model = None


def get_model():
    """
    Charge le modèle uniquement lorsqu'il est nécessaire.
    """

    global _model

    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)

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