#!/bin/bash
set -e

# Lance l'API FastAPI en arrière-plan sur un port interne (8000),
# non exposé publiquement par Hugging Face Spaces.
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Laisse le temps à l'API de démarrer avant que le frontend
# n'essaie de lui envoyer des requêtes.
sleep 5

# Lance le frontend Gradio au premier plan sur le port 7860,
# le seul port exposé publiquement par Hugging Face Spaces.
python frontend/gradio_app.py
