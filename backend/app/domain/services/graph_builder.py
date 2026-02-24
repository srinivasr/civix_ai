from app.infrastructure.db.neo4j_client import neo4j_client

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
        neo4j_client.run_query(query, {
            "voter_id": int(row["voter_id"]),
            "name": row["name"],
            "house_no": row["house_no"],
            "booth_id": int(row["booth_id"])
        })
        count += 1

    return {"voters_processed": count}


def process_complaints(df):
    count = 0
    for _, row in df.iterrows():
        query = """
        MATCH (v:Voter {voter_id: $voter_id})
        MERGE (c:Complaint {complaint_id: $complaint_id})
        SET c.issue_type = $issue_type,
            c.timestamp = $timestamp,
            c.status = $status
        MERGE (v)-[:REPORTED]->(c)
        """
        neo4j_client.run_query(query, {
            "complaint_id": int(row["complaint_id"]),
            "voter_id": int(row["voter_id"]),
            "issue_type": row["issue_type"],
            "timestamp": row["timestamp"],
            "status": row["status"]
        })
        count += 1

    return {"complaints_processed": count}