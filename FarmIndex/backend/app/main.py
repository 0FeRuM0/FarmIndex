from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.upload import router as upload_router
from app.routers.scoring import router as scoring_router
from app.routers.applicants import router as applicants_router
from app.routers.shortlist import router as shortlist_router

app = FastAPI(title="Agro Subsidy Scoring API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(scoring_router)
app.include_router(applicants_router)
app.include_router(shortlist_router)


@app.get("/")
def root():
    return {"message": "Agro Subsidy Scoring API is running"}