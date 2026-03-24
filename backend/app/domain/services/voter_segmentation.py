from app.infrastructure.db.neo4j_client import neo4j_client


def categorize_voters():
    query = """
    MATCH (p:Person)
    OPTIONAL MATCH (p)-[:REPORTED]->(i:Issue)

    WITH p, count(i) AS issue_count

    SET p.category = 
        CASE 
            WHEN issue_count >= 3 THEN "Active"
            WHEN issue_count > 0 THEN "Occasional"
            ELSE "Passive"
        END
    """

    neo4j_client.run_query(query)

    return {"status": "voters categorized"}