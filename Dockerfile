# syntax=docker/dockerfile:1
 
FROM python:3.11-slim
 
WORKDIR /app
 
# Dépendances système nécessaires à PyMuPDF (fitz) et torch
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
 
# Installer les dépendances Python d'abord (mise en cache Docker :
# ne se réinstalle que si requirements.txt change, pas à chaque
# modification de app/)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
# Copier le code de l'application
COPY app/ ./app/
COPY data/ ./data/
 
# Le modèle fine-tuné (models/embedding_model) est volumineux
# (~470 Mo) et peut changer indépendamment du code — on le monte
# en volume au lancement (voir docker-compose.yml) plutôt que de
# le copier dans l'image. Si tu préfères une image 100%
# autonome (sans dépendre d'un volume externe), décommente :
# COPY models/ ./models/
 
EXPOSE 8000
 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
 