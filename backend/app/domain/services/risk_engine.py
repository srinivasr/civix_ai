from app.infrastructure.db.neo4j_client import neo4j_client

def update_risk_scores():
    query = """
    MATCH (b:Booth)
    WITH b,
         CASE WHEN b.complaint_count > 0 THEN toFloat(b.open_count) / toFloat(b.complaint_count) ELSE 0.0 END AS open_ratio
    SET b.risk_level = 
        CASE 
            WHEN open_ratio > 0.7 THEN "High"
            WHEN open_ratio > 0.4 THEN "Medium"
            ELSE "Low"
        END
    """
    neo4j_client.run_query(query)
    return {"status": "risk scores updated"}
