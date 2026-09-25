from fastapi import APIRouter
 
from app.services.embedding_service import FINETUNED_MODEL_PATH
from app.services.skill_extractor import load_skills
 
 
router = APIRouter()
 
 
@router.get("/health")
def health():
    """
    Vérifie l'état réel des dépendances critiques de l'app,
    pas juste "le serveur répond".
    """
 
    # Le modèle fine-tuné existe-t-il sur disque ? Si non,
    # l'app tourne quand même (fallback), mais en mode dégradé
    # (qualité de matching moindre) — utile à savoir en
    # monitoring/déploiement.
    if FINETUNED_MODEL_PATH.exists():
        model_status = "fine-tuned"
    else:
        model_status = "base fallback"
 
    # skills.json se charge-t-il correctement ?
    try:
        skills = load_skills()
        skills_status = "ok"
        skills_count = len(skills)
    except Exception as error:
        skills_status = f"error: {error}"
        skills_count = 0
 
    is_healthy = (
        model_status == "fine-tuned"
        and skills_status == "ok"
        and skills_count > 0
    )
 
    return {
        "status": "ok" if is_healthy else "degraded",
        "embedding_model": model_status,
        "skills_status": skills_status,
        "skills_loaded": skills_count,
    }
 