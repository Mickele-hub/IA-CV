"""
Tests pour la route POST /analyze.
 
Utilise le TestClient de FastAPI, qui appelle l'application
directement en mémoire — pas besoin qu'uvicorn tourne pour
lancer ces tests.
 
Lancer : pytest tests/test_api.py -v
"""
 
from fastapi.testclient import TestClient
 
from app.main import app
 
 
client = TestClient(app)
 
 
def test_analyze_rejects_non_pdf_content_type():
    response = client.post(
        "/analyze",
        files={"cv": ("cv.txt", b"not a pdf", "text/plain")},
        data={"job_description": "Some job description"},
    )
 
    assert response.status_code == 400
 
 
def test_analyze_rejects_blank_job_description(harper_russo_pdf_path):
    # Une chaîne composée uniquement d'espaces (plutôt qu'une
    # chaîne vraiment vide) pour être sûr que le champ est bien
    # transmis par le client de test — certains clients HTTP
    # omettent un champ de formulaire multipart dont la valeur
    # est une chaîne vide, ce qui déclencherait le 422 générique
    # de FastAPI (champ manquant) au lieu du 400 personnalisé
    # de la route (champ vide) qu'on veut réellement tester ici.
    with open(harper_russo_pdf_path, "rb") as file:
        response = client.post(
            "/analyze",
            files={"cv": ("cv.pdf", file, "application/pdf")},
            data={"job_description": "   "},
        )
 
    assert response.status_code == 400
 
 
def test_analyze_returns_expected_shape(harper_russo_pdf_path):
    with open(harper_russo_pdf_path, "rb") as file:
        response = client.post(
            "/analyze",
            files={"cv": ("cv.pdf", file, "application/pdf")},
            data={
                "job_description": (
                    "We are looking for a web developer with "
                    "experience in front-end coding and website "
                    "design."
                )
            },
        )
 
    assert response.status_code == 200
 
    body = response.json()
 
    assert "candidate" in body
    assert "name" in body["candidate"]
    assert "email" in body["candidate"]
    assert "phone" in body["candidate"]
 
    assert "skills" in body
    assert "job_skills" in body
    assert "matched_skills" in body
    assert "missing_skills" in body
 
    assert "match_score" in body
    assert isinstance(body["match_score"], int)
    assert 0 <= body["match_score"] <= 100
 
    assert "recommendations" in body
    assert isinstance(body["recommendations"], list)
    assert len(body["recommendations"]) > 0
 
 
def test_analyze_extracts_correct_candidate_name(harper_russo_pdf_path):
    with open(harper_russo_pdf_path, "rb") as file:
        response = client.post(
            "/analyze",
            files={"cv": ("cv.pdf", file, "application/pdf")},
            data={"job_description": "Looking for a developer"},
        )
 
    body = response.json()
 
    assert body["candidate"]["name"] == "Harper Russo"
    assert body["candidate"]["email"] == "hello@reallygreatsite.com"
 