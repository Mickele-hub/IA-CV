from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from app.services.analyzer import analyze_cv


router = APIRouter()


@router.post("/analyze")
async def analyze(
    cv: UploadFile = File(...),
    job_description: str = Form(...)
):
    """
    Analyse un CV PDF par rapport à une offre d'emploi.
    """

    if cv.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Le fichier doit être un PDF."
        )

    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="La description du poste est obligatoire."
        )

    try:
        result = analyze_cv(
            cv.file,
            job_description
        )

        return result

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur pendant l'analyse : {str(error)}"
        )