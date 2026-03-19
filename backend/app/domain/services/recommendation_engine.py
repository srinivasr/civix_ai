from app.infrastructure.db.neo4j_client import neo4j_client

def generate_recommendations():
    # Set recommendation based on most frequent issue_type per Booth
    query = """
    MATCH (b:Booth)<-[:PART_OF]-(h:House)<-[:LIVES_IN]-(v:Voter)-[:REPORTED]->(c:Complaint)-[:BELONGS_TO]->(i:Issue)
    WITH b, i.name AS issue_type, count(c) AS cnt
    ORDER BY cnt DESC
    WITH b, collect({issue: issue_type, count: cnt})[0] AS main_issue
    WITH b, main_issue.issue AS prevalent_issue
    SET b.recommendation = 
        CASE 
            WHEN prevalent_issue = "Water" THEN "Deploy water inspection team"
            WHEN prevalent_issue = "Electricity" THEN "Contact electricity board"
            WHEN prevalent_issue = "Road" THEN "Schedule road repair overview"
            WHEN prevalent_issue = "Sanitation" THEN "Deploy sanitation team"
            WHEN b.open_count > 10 THEN "Deploy general grievance team"
            ELSE "Monitor situation"
        END
    """
    neo4j_client.run_query(query)
    
    # Set default recommendation for booths with no complaints or missing data
    default_query = """
    MATCH (b:Booth)
    WHERE b.recommendation IS NULL OR b.complaint_count = 0
    SET b.recommendation = "No action required"
    """
    neo4j_client.run_query(default_query)
    
    return {"status": "recommendations generated"}
