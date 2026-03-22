from app.infrastructure.db.neo4j_client import neo4j_client
from app.domain.services.graph_enrichment import update_booth_metrics


def process_voters(df):
    count = 0
    for _, row in df.iterrows():
        query = """
        MERGE (b:Booth {booth_id: $booth_id})
        MERGE (h:House {house_no: $house_no})
        MERGE (v:Voter {epic: $epic})
        SET v.name = $name, 
            v.age = $age, 
            v.gender = $gender,
            v.relation_name = $relation_name,
            v.relation_type = $relation_type,
            v.assembly = $assembly,
            v.section = $section
        MERGE (v)-[:LIVES_IN]->(h)
        MERGE (h)-[:PART_OF]->(b)
        """
        neo4j_client.run_query(
            query,
            {
                "epic": str(row["epic"]).strip(),
                "name": str(row["name"]).strip(),
                "age": int(row["age"]) if str(row["age"]).strip().isdigit() else -1,
                "gender": str(row["gender"]).strip(),
                "relation_name": str(row["relation_name"]).strip(),
                "relation_type": str(row["relation_type"]).strip(),
                "house_no": str(row["house_no"]).strip(),
                "assembly": str(row["assembly"]).strip(),
                "section": str(row["section"]).strip(),
                "booth_id": int(row["part_no"]) if str(row["part_no"]).strip().isdigit() else -1,
            },
        )
        count += 1

    return {"voters_processed": count}


def process_complaints(df):
    count = 0

    for _, row in df.iterrows():
        query = """
        MATCH (v:Voter {epic: $epic})
        OPTIONAL MATCH (v)-[:LIVES_IN]->(h:House)-[:PART_OF]->(b:Booth)

        MERGE (c:Complaint {complaint_id: $complaint_id})
        SET c.issue_type = $issue_type,
            c.subject = $subject,
            c.description = $description,
            c.timestamp = $timestamp,
            c.status = $status

        MERGE (v)-[:REPORTED]->(c)
        MERGE (i:Issue {name: $issue_type})
        MERGE (c)-[:BELONGS_TO]->(i)
        """

        neo4j_client.run_query(
            query,
            {
                "complaint_id": int(row["complaint_id"]),
                "epic": str(row["epic"]).strip(),
                "subject": str(row.get("subject", "")).strip(),
                "description": str(row.get("description", "")).strip(),
                "issue_type": str(row["issue_type"]).strip(),
                "timestamp": str(row["timestamp"]).strip(),
                "status": str(row["status"]).strip(),
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
