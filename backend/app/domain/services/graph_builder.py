import uuid
from app.infrastructure.db.neo4j_client import neo4j_client
from app.domain.services.graph_enrichment import update_booth_metrics


def clear_database():
    """Wipe the entire Neo4j database before a clean re-seed."""
    query = "MATCH (n) DETACH DELETE n"
    return neo4j_client.run_query(query)
    


def process_voters(df):
    count = 0

    for _, row in df.iterrows():
        epic_val = str(row["epic"]).strip()
        if not epic_val or epic_val.upper() == "UNKNOWN" or epic_val.lower() == "nan":
            epic_val = f"UNKNOWN_{uuid.uuid4().hex[:8]}"

        house_no = str(row["house_no"]).strip()
        booth_id = str(row["booth_id"]).strip()
        area = str(row["section"]).strip()

        #  FIX: unique house
        house_id = f"{booth_id}_{area}_{house_no}"

        

        query = """
        MERGE (b:Booth {booth_id: $booth_id})

        MERGE (a:Area {name: $area, booth_id: $booth_id})
        MERGE (b)-[:HAS_AREA]->(a)

        MERGE (h:House {house_id: $house_id})
        SET h.house_no = $house_no,
            h.area = $area,
            h.booth_id = $booth_id

        MERGE (a)-[:HAS_HOUSE]->(h)

        MERGE (p:Person {epic_id: $epic})
        SET p.name = $name,
            p.age = $age,
            p.gender = $gender,
            p.relation_name = $relation_name,
            p.relation_type = $relation_type,
            p.assembly = $assembly,
            p.section = $section

        MERGE (h)-[:HAS_MEMBER]->(p)
        """

        neo4j_client.run_query(
            query,
            {
                "epic": epic_val,
                "name": str(row["name"]).strip(),
                "age": int(row["age"]) if str(row["age"]).strip().isdigit() else -1,
                "gender": str(row["gender"]).strip(),
                "relation_name": str(row["relation_name"]).strip(),
                "relation_type": str(row["relation_type"]).strip(),
                "house_no": house_no,
                "assembly": str(row["assembly"]).strip(),
                "section": str(row["section"]).strip(),
                "booth_id": booth_id,
                "area": area,
                "house_id": house_id,
            },
        )

        count += 1

    return {"voters_processed": count}


def process_complaints(df):
    count = 0

    for _, row in df.iterrows():
        query = """
<<<<<<< HEAD
        MERGE (v:Voter {epic: $epic})
=======
        OPTIONAL MATCH (p:Person {epic_id: $epic})
        WITH p
        WHERE p IS NOT NULL
>>>>>>> 50bb645 (Changed the graph structure)

        MERGE (i:Issue {complaint_id: $complaint_id})
        SET i.type = $issue_type,
            i.status = $status,
            i.timestamp = $timestamp

        MERGE (p)-[:REPORTED]->(i)

        WITH i, p
        MATCH (p)<-[:HAS_MEMBER]-(h:House)
        MERGE (i)-[:BELONGS_TO]->(h)

        WITH i, h
        MATCH (h)<-[:HAS_HOUSE]-(a:Area)
        MERGE (i)-[:LOCATED_IN]->(a)

        WITH i, a
        MATCH (a)<-[:HAS_AREA]-(b:Booth)
        MERGE (i)-[:IN_BOOTH]->(b)
        """

        neo4j_client.run_query(
            query,
            {
                "complaint_id": int(row["complaint_id"]),
                "epic": str(row["epic"]).strip(),
                "issue_type": str(row["issue_type"]).strip(),
                "timestamp": str(row["timestamp"]).strip(),
                "status": str(row["status"]).strip(),
            },
        )

        count += 1

    update_booth_metrics()

    from app.domain.services.risk_engine import update_risk_scores
    from app.domain.services.recommendation_engine import generate_recommendations
    from app.domain.services.voter_segmentation import categorize_voters

    update_risk_scores()
    generate_recommendations()
    categorize_voters()

    return {"complaints_processed": count}