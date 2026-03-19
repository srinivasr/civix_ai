from app.infrastructure.db.neo4j_client import neo4j_client
from app.domain.services.graph_enrichment import update_booth_metrics


def process_voters(df):
    count = 0
    for _, row in df.iterrows():
        query = """
        MERGE (b:Booth {booth_id: $booth_id})
        MERGE (h:House {house_no: $house_no})
        MERGE (v:Voter {voter_id: $voter_id})
        SET v.name = $name
        MERGE (v)-[:LIVES_IN]->(h)
        MERGE (h)-[:PART_OF]->(b)
        """
        neo4j_client.run_query(
            query,
            {
                "voter_id": int(row["voter_id"]),
                "name": row["name"],
                "house_no": row["house_no"],
                "booth_id": int(row["booth_id"]),
            },
        )
        count += 1

    return {"voters_processed": count}


def process_complaints(df):
    count = 0

    for _, row in df.iterrows():
        query = """
        MATCH (v:Voter {voter_id: $voter_id})
        OPTIONAL MATCH (v)-[:LIVES_IN]->(h:House)-[:PART_OF]->(b:Booth)

        MERGE (c:Complaint {complaint_id: $complaint_id})
        SET c.issue_type = $issue_type,
            c.timestamp = $timestamp,
            c.status = $status

        MERGE (v)-[:REPORTED]->(c)
        MERGE (i:Issue {name: $issue_type})
        MERGE (c)-[:BELONGS_TO]->(i)
        """

        result = neo4j_client.run_query(
            query,
            {
                "complaint_id": int(row["complaint_id"]),
                "voter_id": int(row["voter_id"]),
                "issue_type": row["issue_type"],
                "timestamp": row["timestamp"],
                "status": row["status"],
            },
        )

        count += 1
    update_booth_metrics()

    # Trigger Intelligence Layer
    from app.domain.services.risk_engine import update_risk_scores
    from app.domain.services.recommendation_engine import generate_recommendations
    from app.domain.services.voter_segmentation import categorize_voters

    update_risk_scores()
    generate_recommendations()
    categorize_voters()

    return {"complaints_processed": count}
