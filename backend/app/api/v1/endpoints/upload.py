from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd
from app.domain.services.graph_builder import process_voters, process_complaints

router = APIRouter()

@router.post("/")
async def upload_file(file: UploadFile = File(...), file_type: str = "voters"):
    try:
        contents = await file.read()
        df = pd.read_csv(pd.io.common.BytesIO(contents))

        if file_type == "voters":
            result = process_voters(df)
        elif file_type == "complaints":
            result = process_complaints(df)
        else:
            raise HTTPException(status_code=400, detail="Invalid file_type")

        return {
            "status": "success",
            "details": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))