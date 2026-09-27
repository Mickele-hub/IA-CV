from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_analyze_rejects_non_pdf_file():
    fake_file = ("cv.txt", b"ceci n'est pas un pdf", "text/plain")

    response = client.post(
        "/analyze",
        files={"cv": fake_file},
        data={"job_description": "Développeur Python"},
    )

    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


def test_analyze_rejects_empty_job_description(sample_cv_path):
    with open(sample_cv_path, "rb") as pdf_file:
        response = client.post(
            "/analyze",
            files={"cv": ("cv.pdf", pdf_file, "application/pdf")},
            data={"job_description": "   "},
        )

    assert response.status_code == 400
    assert "obligatoire" in response.json()["detail"]


def test_analyze_returns_expected_fields(
    monkeypatch,
    sample_cv_path,
    sample_job_description,
):
    # On mocke le score sémantique pour ne pas dépendre du
    # téléchargement du modèle sentence-transformers pendant
    # les tests : ce comportement est déjà couvert par
    # test_matcher.py.
    monkeypatch.setattr(
        "app.services.analyzer.calculate_match_score",
        lambda cv_text, job_text: 75,
    )

    with open(sample_cv_path, "rb") as pdf_file:
        response = client.post(
            "/analyze",
            files={"cv": ("cv.pdf", pdf_file, "application/pdf")},
            data={"job_description": sample_job_description},
        )

    assert response.status_code == 200

    body = response.json()

    assert "skills" in body
    assert "job_skills" in body
    assert "matched_skills" in body
    assert "missing_skills" in body
    assert "match_score" in body
    assert "recommendations" in body

    # Python et React sont dans le CV ET dans l'offre
    assert "Python" in body["matched_skills"]
    assert "React" in body["matched_skills"]

    assert body["match_score"] == 75
    assert isinstance(body["recommendations"], list)
    assert len(body["recommendations"]) > 0
