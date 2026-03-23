"""
Complaints API — v1
====================
Endpoints for lodging and resolving voter complaints.
Integrates with the Fast2SMS notification service for real-time SMS updates.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
from datetime import datetime
from pathlib import Path

from app.domain.services.graph_builder import process_complaints
from app.infrastructure.sms_service import send_sms, notify_by_doc_id

router = APIRouter()

UPLOADS_DIR = Path("data/uploads")
COMPLAINTS_CSV = UPLOADS_DIR / "complaints.csv"

# ── Column schema for the complaints CSV ────────────────────────────────────
CSV_COLUMNS = [
    "complaint_id",
    "voter_epic",
    "phone_number",
    "issue_type",
    "issue_classification",
    "subject",
    "description",
    "timestamp",
    "status",
]


# ── Request Models ──────────────────────────────────────────────────────────
class LodgeComplaintRequest(BaseModel):
    voter_epic: str
    phone_number: str
    issue_type: str
    description: str


class LegacyComplaintRequest(BaseModel):
    """Backwards-compatible request shape used by the existing frontend."""
    epic: str
    subject: str
    issue_type: str
    description: str


# ─────────────────────────────────────────────────────────────────────────────
#  POST  /lodge-complaint
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/lodge-complaint")
async def lodge_complaint_sms(request: LodgeComplaintRequest):
    """
    Lodge a new complaint and send a *Complaint Registered* SMS to the voter.
    """
    try:
        _ensure_csv_exists()

        existing_df = pd.read_csv(COMPLAINTS_CSV)
        next_id = _next_complaint_id(existing_df)
        timestamp = datetime.now().isoformat()

        new_row = {
            "complaint_id": next_id,
            "voter_epic": request.voter_epic,
            "phone_number": request.phone_number,
            "issue_type": request.issue_type,
            "issue_classification": request.issue_type,
            "subject": request.issue_type,
            "description": request.description,
            "timestamp": timestamp,
            "status": "Open",
        }

        new_df = pd.concat(
            [existing_df, pd.DataFrame([new_row])], ignore_index=True
        )
        new_df.to_csv(COMPLAINTS_CSV, index=False)

        # Sync into the knowledge‑graph
        try:
            process_complaints(pd.DataFrame([new_row]))
        except Exception as graph_exc:
            # Non-fatal: log but continue
            print(f"⚠ Graph sync failed (non-fatal): {graph_exc}")

        # Fire the acknowledgement SMS
        sms_message = (
            f"CIVIX-AI: Your complaint (Ref: {next_id}) regarding "
            f"'{request.issue_type}' has been REGISTERED successfully. "
            f"We will keep you updated. - Govt Secretariat"
        )
        sms_result = send_sms(request.phone_number, sms_message)

        return {
            "status": "success",
            "complaint_id": next_id,
            "sms_status": sms_result,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error lodging complaint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
#  POST  /  (legacy endpoint — kept for backward compatibility)
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/")
async def lodge_complaint_legacy(request: LegacyComplaintRequest):
    """Original lodge-complaint endpoint preserved for existing clients."""
    try:
        _ensure_csv_exists()

        existing_df = pd.read_csv(COMPLAINTS_CSV)
        next_id = _next_complaint_id(existing_df)
        timestamp = datetime.now().isoformat()

        new_row = {
            "complaint_id": next_id,
            "epic": request.epic,
            "voter_epic": request.epic,
            "subject": request.subject,
            "issue_type": request.issue_type,
            "issue_classification": request.issue_type,
            "description": request.description,
            "timestamp": timestamp,
            "status": "Open",
        }

        # Ensure existing CSV has the new columns
        for col in CSV_COLUMNS:
            if col not in existing_df.columns:
                existing_df[col] = ""

        new_df = pd.concat(
            [existing_df, pd.DataFrame([new_row])], ignore_index=True
        )
        new_df.to_csv(COMPLAINTS_CSV, index=False)

        try:
            process_complaints(pd.DataFrame([new_row]))
        except Exception as graph_exc:
            print(f"⚠ Graph sync failed (non-fatal): {graph_exc}")

        return {"status": "success", "complaint_id": next_id}

    except Exception as e:
        print(f"Error lodging complaint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
#  POST  /resolve/{doc_id}
# ─────────────────────────────────────────────────────────────────────────────
@router.post("/resolve/{doc_id}")
async def resolve_complaint(doc_id: int):
    """
    Mark a complaint as resolved and send a resolution SMS to the voter.
    """
    try:
        if not COMPLAINTS_CSV.exists():
            raise HTTPException(
                status_code=404, detail="Complaints data not found."
            )

        df = pd.read_csv(COMPLAINTS_CSV)
        mask = df["complaint_id"] == doc_id

        if not mask.any():
            raise HTTPException(
                status_code=404,
                detail=f"Complaint with ID {doc_id} not found.",
            )

        # Update status to Resolved
        df.loc[mask, "status"] = "Resolved"
        df.to_csv(COMPLAINTS_CSV, index=False)

        # Send the resolution SMS
        sms_result = notify_by_doc_id(doc_id)

        return {
            "status": "success",
            "complaint_id": doc_id,
            "resolution": "Complaint marked as resolved.",
            "sms_status": sms_result,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error resolving complaint {doc_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _ensure_csv_exists() -> None:
    """Create the complaints CSV with headers if it does not yet exist."""
    if not COMPLAINTS_CSV.exists():
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(columns=CSV_COLUMNS).to_csv(COMPLAINTS_CSV, index=False)


def _next_complaint_id(df: pd.DataFrame) -> int:
    """Return the next sequential complaint ID."""
    if df.empty or "complaint_id" not in df.columns:
        return 1001
    return int(df["complaint_id"].max()) + 1
