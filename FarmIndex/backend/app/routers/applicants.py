from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas import ApplicantListItem, ApplicantDetail
import app.storage as storage

router = APIRouter()


@router.get("/applicants", response_model=List[ApplicantListItem])
def get_applicants(
    search: Optional[str] = Query(default=None),
    region: Optional[str] = Query(default=None),
    recommendation: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    if storage.scored_df is None:
        return []

    df = storage.scored_df.copy()

    if search:
        df = df[df["name"].astype(str).str.contains(search, case=False, na=False)]

    if region:
        df = df[df["region"].astype(str) == region]

    if recommendation:
        df = df[df["recommendation"].astype(str) == recommendation]

    df = df.sort_values(by="score", ascending=False)
    df = df.iloc[offset: offset + limit]

    result = []
    for _, row in df.iterrows():
        result.append(
            ApplicantListItem(
                id=int(row["id"]),
                name=str(row["name"]),
                region=str(row["region"]),
                score=float(row["score"]),
                recommendation=str(row["recommendation"]),
                risk=str(row["risk"]),
            )
        )
    return result


@router.get("/applicants/{applicant_id}", response_model=ApplicantDetail)
def get_applicant_detail(applicant_id: int):
    if storage.scored_df is None:
        raise HTTPException(status_code=400, detail="Скоринг еще не запускался")

    matched = storage.scored_df[storage.scored_df["id"] == applicant_id]
    if matched.empty:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    row = matched.iloc[0]

    direction = str(row.get("Направление водства", "")).strip() or None

    return ApplicantDetail(
        id=int(row["id"]),
        name=str(row["name"]),
        region=str(row["region"]),
        farm_type=direction,
        score=float(row["score"]),
        recommendation=str(row["recommendation"]),
        risk=str(row["risk"]),
        positive_factors=list(row["positive_factors"]),
        negative_factors=list(row["negative_factors"]),
        risk_flags=list(row["risk_flags"]),
    )