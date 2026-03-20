from app.infrastructure.db.neo4j_client import neo4j_client


def check():
    res = neo4j_client.run_query("MATCH (v:Voter) RETURN count(v) AS count")
    print("Voters in DB:", res[0]["count"])
    res2 = neo4j_client.run_query("MATCH (c:Complaint) RETURN count(c) AS count")
    print("Complaints in DB:", res2[0]["count"])


if __name__ == "__main__":
    check()
