from fastapi import APIRouter, HTTPException
from app.infrastructure.db.neo4j_client import neo4j_client

router = APIRouter()

@router.get("/{booth_id}")
def get_booth_drives(booth_id: str):
    try:
        query = """
        MATCH (b:Booth {booth_id: $booth_id})-[:HAS_DRIVE]->(d:Drive)
        RETURN 
            d.title AS title,
            d.description AS description,
            d.type AS type,
            d.date AS date,
            d.created_at AS created_at
        ORDER BY d.date DESC
        """
        return neo4j_client.run_query(query, {"booth_id": booth_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
