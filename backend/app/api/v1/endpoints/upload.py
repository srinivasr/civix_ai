import io
import tempfile
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
import pandas as pd

from app.domain.services.graph_builder import process_voters, process_complaints

router = APIRouter()

UPLOADS_DIR = Path(__file__).resolve().parents[4] / "data" / "uploads"


@router.post("/")
async def upload_csv(file: UploadFile = File(...), file_type: str = "voters"):
    """Upload a CSV file and process it into the graph."""
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        if file_type == "voters":
            result = process_voters(df)
        elif file_type == "complaints":
            result = process_complaints(df)
        else:
            raise HTTPException(status_code=400, detail="Invalid file_type")

        return {"status": "success", "details": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a voter PDF → convert to CSV via OCR → process into graph."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400, detail="Only PDF files are accepted."
        )

    try:
        # Save uploaded PDF to a temp file
        contents = await file.read()
        with tempfile.NamedTemporaryFile(
            suffix=".pdf", delete=False, mode="wb"
        ) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        # Run the PDF → DataFrame pipeline
        from app.domain.services.pdf_converter import process_pdf

        df = process_pdf(tmp_path)

        # Clean up temp file
        import os
        os.unlink(tmp_path)

        if df.empty:
            return {
                "status": "success",
                "records_extracted": 0,
                "message": "No voter records could be extracted from this PDF.",
            }

        # Save as voters.csv (triggers auto-update watcher too)
        csv_path = UPLOADS_DIR / "voters.csv"
        df.to_csv(csv_path, index=False)

        # Process into graph immediately
        result = process_voters(df)

        return {
            "status": "success",
            "records_extracted": len(df),
            "processing_result": result,
            "message": (
                f"Successfully extracted {len(df)} voter records "
                f"from PDF and loaded into the database."
            ),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF processing failed: {str(e)}",
        )
