---
title: SmartCV AI
emoji: 📄
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# SmartCV AI

API et interface d'analyse intelligente de CV et de correspondance avec une offre d'emploi.

POUR TESTER L'APP : d'abord créer l'environnement virtuel puis installer les dependances dans requirements.txt
puis :
  1)app : cd .\CV-AI\   .\venv\Scripts\Activate.ps1     uvicorn app.main:app --reload
  2)front : cd .\CV-AI\   .\venv\Scripts\Activate.ps1   python frontend\gradio_app.py
  3)api : http://localhost:8000/docs
