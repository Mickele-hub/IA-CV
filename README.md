app : cd .\CV-AI\   .\venv\Scripts\Activate.ps1     uvicorn app.main:app --reload
front : cd .\CV-AI\   .\venv\Scripts\Activate.ps1   python frontend\gradio_app.py
api : http://localhost:8000/docs