from fastapi import APIRouter, UploadFile, File
from app.schemas import UploadResponse, DatasetPreviewResponse
from app.services.file_parser import parse_uploaded_file
import app.storage as storage

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
def upload_dataset(file: UploadFile = File(...)):
    df = parse_uploaded_file(file)

    if "id" not in df.columns:
        df.insert(0, "id", range(1, len(df) + 1))

    storage.dataset_df = df
    storage.scored_df = None
    storage.shortlist_ids.clear()

    return UploadResponse(
        status="success",
        rows=len(df),
        columns=len(df.columns),
        message="Файл успешно загружен"
    )


@router.get("/dataset/preview", response_model=DatasetPreviewResponse)
def get_dataset_preview():
    if storage.dataset_df is None:
        return DatasetPreviewResponse(columns=[], rows=[])

    preview_df = storage.dataset_df.head(20)
    return DatasetPreviewResponse(
        columns=list(preview_df.columns),
        rows=preview_df.to_dict(orient="records")
    )