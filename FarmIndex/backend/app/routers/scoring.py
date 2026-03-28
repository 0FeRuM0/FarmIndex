from fastapi import APIRouter, HTTPException
from app.schemas import ScoringRunResponse
from app.services.scoring_service import run_scoring
import app.storage as storage

router = APIRouter()


@router.post("/scoring/run", response_model=ScoringRunResponse)
def run_scoring_endpoint():
    if storage.dataset_df is None:
        raise HTTPException(status_code=400, detail="Сначала загрузите датасет")

    storage.scored_df = run_scoring(storage.dataset_df)

    return ScoringRunResponse(
        status="success",
        processed=len(storage.scored_df),
        message="Скоринг успешно выполнен"
    )