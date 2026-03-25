import sys
import os
sys.path.append("/home/lev/repos/AAkar/backend")

from backend.app.infrastructure.db.neo4j_client import neo4j_client
import pandas as pd

res = neo4j_client.run_query("MATCH (i:Issue) RETURN i.complaint_id AS cid ORDER BY cid")
db_cids = [r['cid'] for r in res] if res else []
print("Neo4j complaint IDs:", db_cids)

df = pd.read_csv("backend/data/uploads/complaints.csv")
csv_cids = df['complaint_id'].tolist()
print("CSV complaint IDs:", csv_cids)

missing = set(csv_cids) - set(db_cids)
print("Missing in Neo4j:", missing)

if missing:
    cid = list(missing)[0]
    row = df[df['complaint_id'] == cid].iloc[0]
    epic = str(row['EPIC']).strip()
    print(f"Missing complaint {cid} has EPIC {epic}. Checking Person node...")
    pres = neo4j_client.run_query("MATCH (p:Person {epic_id: $epic}) RETURN p.epic_id AS epic", {"epic": epic})
    print(f"Person query result: {pres}")
    
    pres = neo4j_client.run_query("MATCH (p:Person {epic_id: $epic}) RETURN p limit 1", {"epic": epic})
    print(f"Does person exist at all? {pres}")

