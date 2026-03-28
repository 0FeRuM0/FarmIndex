from pydantic import BaseModel
from typing import List, Optional, Any


class UploadResponse(BaseModel):
    status: str
    rows: int
    columns: int
    message: str


class DatasetPreviewResponse(BaseModel):
    columns: List[str]
    rows: List[dict[str, Any]]


class ScoringRunResponse(BaseModel):
    status: str
    processed: int
    message: str


class ApplicantListItem(BaseModel):
    id: int
    name: str
    region: str
    score: float
    recommendation: str
    risk: str


class ApplicantDetail(BaseModel):
    id: int
    name: str
    region: str
    farm_type: Optional[str] = None
    score: float
    recommendation: str
    risk: str
    positive_factors: List[str]
    negative_factors: List[str]
    risk_flags: List[str]


class ShortlistItem(BaseModel):
    id: int
    name: str
    score: float
    recommendation: str


class MessageResponse(BaseModel):
    status: str
    message: str