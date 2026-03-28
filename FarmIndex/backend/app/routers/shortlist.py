from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas import ShortlistItem, MessageResponse
import app.storage as storage

router = APIRouter()


@router.get("/shortlist", response_model=List[ShortlistItem])
def get_shortlist():
    if storage.scored_df is None:
        return []

    df = storage.scored_df[storage.scored_df["id"].isin(storage.shortlist_ids)].copy()
    df = df.sort_values(by="score", ascending=False)

    result = []
    for _, row in df.iterrows():
        result.append(
            ShortlistItem(
                id=int(row["id"]),
                name=str(row["name"]),
                score=float(row["score"]),
                recommendation=str(row["recommendation"]),
            )
        )
    return result


@router.post("/shortlist/{applicant_id}", response_model=MessageResponse)
def add_to_shortlist(applicant_id: int):
    if storage.scored_df is None:
        raise HTTPException(status_code=400, detail="Скоринг еще не запускался")

    matched = storage.scored_df[storage.scored_df["id"] == applicant_id]
    if matched.empty:
        raise HTTPException(status_code=404, detail="Заявитель не найден")

    storage.shortlist_ids.add(applicant_id)

    return MessageResponse(
        status="success",
        message="Кандидат добавлен в shortlist"
    )


@router.delete("/shortlist/{applicant_id}", response_model=MessageResponse)
def remove_from_shortlist(applicant_id: int):
    storage.shortlist_ids.discard(applicant_id)

    return MessageResponse(
        status="success",
        message="Кандидат удален из shortlist"
    )