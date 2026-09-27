FROM python:3.11-slim

WORKDIR /code

# Dépendances système minimales (PyMuPDF/scikit-learn en ont besoin pour compiler certaines roues)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Hugging Face Spaces exige de ne pas exécuter le conteneur en root
RUN useradd -m -u 1000 appuser
ENV HOME=/home/appuser \
    HF_HOME=/home/appuser/.cache/huggingface \
    PATH=/home/appuser/.local/bin:$PATH

COPY --chown=appuser:appuser . .
RUN chmod +x start.sh

USER appuser

# Seul le port 7860 est exposé publiquement par Hugging Face Spaces
EXPOSE 7860

CMD ["./start.sh"]
