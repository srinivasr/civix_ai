from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
from datetime import datetime
from pathlib import Path
import os
from app.domain.services.graph_builder import process_complaints

router = APIRouter()

UPLOADS_DIR = Path("data/uploads")
COMPLAINTS_CSV = UPLOADS_DIR / "complaints.csv"

class ComplaintRequest(BaseModel):
    epic: str
    subject: str
    issue_type: str
    description: str

@router.post("/")
async def lodge_complaint(request: ComplaintRequest):
    try:
        # 1. Read existing CSV to determine new ID (or use timestamp-based)
        if not COMPLAINTS_CSV.exists():
            # Create with headers if doesn't exist
            UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
            df = pd.DataFrame(columns=["complaint_id", "epic", "subject", "issue_type", "description", "timestamp", "status"])
            df.to_csv(COMPLAINTS_CSV, index=False)
        
        existing_df = pd.read_csv(COMPLAINTS_CSV)
        next_id = 1001
        if not existing_df.empty and "complaint_id" in existing_df.columns:
            next_id = int(existing_df["complaint_id"].max()) + 1
            
        timestamp = datetime.now().isoformat()
        
        # 2. Append to CSV
        new_row = {
            "complaint_id": next_id,
            "epic": request.epic,
            "subject": request.subject,
            "issue_type": request.issue_type,
            "description": request.description,
            "timestamp": timestamp,
            "status": "Open"
        }
        
        # Check if subject/description columns exist, if not, re-save with them
        if "subject" not in existing_df.columns:
            existing_df["subject"] = ""
            existing_df["description"] = ""
            
        new_df = pd.concat([existing_df, pd.DataFrame([new_row])], ignore_index=True)
        new_df.to_csv(COMPLAINTS_CSV, index=False)
        
        # 3. Process into Neo4j
        # process_complaints expects a DataFrame
        process_complaints(pd.DataFrame([new_row]))
        
        return {"status": "success", "complaint_id": next_id}
        
    except Exception as e:
        print(f"Error lodging complaint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
