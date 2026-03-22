from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.infrastructure.db.neo4j_client import neo4j_client

router = APIRouter()


@router.get("/overview")
def get_admin_overview():
    try:
        # Aggregate all stats from booth metrics for consistency
        overview_query = """
        MATCH (b:Booth)
        WITH count(b) AS total_booths
        OPTIONAL MATCH (c:Complaint)
        RETURN
            total_booths,
            count(c) AS total_complaints,
            sum(CASE WHEN c.status = 'Open' THEN 1 ELSE 0 END) AS total_open,
            sum(CASE WHEN c.status = 'Resolved' THEN 1 ELSE 0 END) AS total_resolved
        """
        result = neo4j_client.run_query(overview_query)
        row = result[0] if result else {}

        total_booths = row.get("total_booths") or 0
        total_complaints = row.get("total_complaints") or 0
        total_open = row.get("total_open") or 0
        total_resolved = row.get("total_resolved") or 0

        avg_open_ratio = 0
        if total_complaints > 0:
            avg_open_ratio = total_open / total_complaints

        return {
            "total_booths": total_booths,
            "total_complaints": total_complaints,
            "total_open_complaints": total_open,
            "total_resolved_complaints": total_resolved,
            "avg_open_ratio": round(avg_open_ratio, 2),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch overview: {str(e)}"
        )


@router.get("/booths")
def get_booths():
    query = """
    MATCH (b:Booth)
    RETURN 
        b.booth_id AS booth_id,
        coalesce(b.complaint_count, 0) AS complaint_count,
        coalesce(b.open_count, 0) AS open_count,
        coalesce(b.resolved_count, 0) AS resolved_count,
        coalesce(b.risk_level, "Low") AS risk_level,
        coalesce(b.recommendation, "No action required") AS recommendation
    ORDER BY b.booth_id
    """
    return neo4j_client.run_query(query)


@router.get("/recommendations")
def get_recommendations():
    query = """
    MATCH (b:Booth)
    WHERE b.recommendation IS NOT NULL AND b.recommendation <> "No action required"
    RETURN
        b.booth_id AS booth_id,
        b.recommendation AS recommendation,
        coalesce(b.risk_level, "Low") AS risk_level
    ORDER BY b.booth_id
    """
    return neo4j_client.run_query(query)


@router.get("/messages")
def get_messages():
    from app.domain.services.message_generator import generate_booth_messages

    return generate_booth_messages()


@router.get("/analytics/network")
def get_analytics_network():
    from app.domain.services.graph_analytics import get_network_analytics

    try:
        return get_network_analytics()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate network analytics: {str(e)}"
        )


class DriveCreate(BaseModel):
    title: str
    description: str
    type: str  # 'Drive' or 'Function'
    date: str
    booth_id: str


@router.post("/drives")
def create_official_drive(drive: DriveCreate):
    try:
        # Create Drive node and link to Booth
        query = """
        MATCH (b:Booth {booth_id: $booth_id})
        CREATE (d:Drive {
            title: $title,
            description: $description,
            type: $type,
            date: $date,
            created_at: $created_at
        })
        CREATE (b)-[:HAS_DRIVE]->(d)
        RETURN d
        """
        params = {
            "booth_id": drive.booth_id,
            "title": drive.title,
            "description": drive.description,
            "type": drive.type,
            "date": drive.date,
            "created_at": datetime.now().isoformat()
        }
        result = neo4j_client.run_query(query, params)
        if not result:
            raise HTTPException(status_code=404, detail="Booth not found")
        return {"status": "success", "message": "Drive created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/drives")
def get_all_drives():
    try:
        query = """
        MATCH (b:Booth)-[:HAS_DRIVE]->(d:Drive)
        RETURN 
            d.title AS title,
            d.description AS description,
            d.type AS type,
            d.date AS date,
            b.booth_id AS booth_id,
            d.created_at AS created_at
        ORDER BY d.created_at DESC
        """
        return neo4j_client.run_query(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
