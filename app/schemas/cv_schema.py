from pydantic import BaseModel


class AnalysisResponse(BaseModel):
    skills: list[str]
    job_skills: list[str]
    matched_skills: list[str]
    missing_skills: list[str]
    match_score: int
    recommendations: list[str]