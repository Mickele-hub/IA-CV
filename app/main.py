from fastapi import FastAPI

from app.routes.health import router as health_router
from app.routes.analyze import router as analyze_router


app = FastAPI(
    title="SmartCV AI",
    description=(
        "API d'analyse intelligente de CV "
        "et de correspondance avec une offre d'emploi."
    ),
    version="1.0.0"
)


app.include_router(health_router)
app.include_router(analyze_router)


@app.get("/")
def root():
    return {
        "message": "SmartCV AI API",
        "status": "running"
    }