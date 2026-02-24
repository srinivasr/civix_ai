from fastapi import FastAPI
from app.api.v1.endpoints.upload import router as upload_router

app = FastAPI(title="Civix AI Backend")

app.include_router(upload_router, prefix="/api/v1/upload", tags=["Upload"])

@app.get("/")
def health():
    return {"status": "Backend running"}