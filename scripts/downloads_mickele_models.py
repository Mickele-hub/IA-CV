"""
Download the trained CV-AI embedding models from Hugging Face.

Usage:
    python scripts/download_models.py
"""

from pathlib import Path
from huggingface_hub import snapshot_download


# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Local models directory
MODELS_DIR = BASE_DIR / "models"


# ============================================================
# Hugging Face repositories
# ============================================================
#
# Replace these values with your actual Hugging Face
# repository IDs.
#
# Example:
# "Mickele-hub/cv-ai-embedding-model"
#

MODELS = {
    "embedding_model": "Mickele-hub/cv-ai-embedding-model",
    "embedding_model_test": "Mickele-hub/cv-ai-embedding-model-test",
}


def download_model(model_name: str, repository_id: str) -> None:
    """
    Download one model from Hugging Face.
    """

    destination = MODELS_DIR / model_name

    print()
    print("=" * 60)
    print(f"Downloading: {model_name}")
    print(f"Repository: {repository_id}")
    print(f"Destination: {destination}")
    print("=" * 60)

    destination.mkdir(parents=True, exist_ok=True)

    # Download model files
    snapshot_download(
        repo_id=repository_id,
        local_dir=str(destination),
    )

    print(f"✓ {model_name} downloaded successfully.")


def main() -> None:
    """
    Download all required models.
    """

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    for model_name, repository_id in MODELS.items():

        try:
            download_model(
                model_name=model_name,
                repository_id=repository_id,
            )

        except Exception as error:
            print()
            print(f"✗ Failed to download {model_name}")
            print(f"Error: {error}")
            return

    print()
    print("=" * 60)
    print("✓ All CV-AI models are ready.")
    print("=" * 60)


if __name__ == "__main__":
    main()

