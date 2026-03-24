import re
from app.infrastructure.ai.ollama_client import ollama_client
from app.infrastructure.db.neo4j_client import neo4j_client

# Cypher keywords that indicate a write/destructive operation
BLOCKED_KEYWORDS = re.compile(
    r"\b(DELETE|CREATE|MERGE|SET|REMOVE|DROP|DETACH)\b",
    re.IGNORECASE,
)


def ask_question(question: str) -> dict:
    """Full pipeline: question → schema → Cypher → safety → execute → graph + answer."""

    # 1. Fetch the live schema from Neo4j
    db_schema = neo4j_client.get_schema()

    custom_schema = """
You are a Neo4j Cypher generator.

STRICT RULES:

- The term "voter" refers to ALL Person nodes
- DO NOT filter using p.category = 'voter'
- "voter" is NOT a category — it means Person

- NEVER generate:
  p.category = 'voter'

- ALWAYS interpret:
  "voters" → Person nodes

- Use ONLY:
  Person, Issue, Booth, Area, House, Family

Graph Schema:

Nodes:
- Booth (booth_id, complaint_count, open_count, resolved_count)
- Area (name)
- House (house_no)
- 
- Person (epic_id, name, age, gender, category)
- Issue (complaint_id, type, status, timestamp)

Relationships:
- Booth -[:HAS_AREA]-> Area
- Area -[:HAS_HOUSE]-> House


- Person -[:REPORTED]-> Issue
- Issue -[:BELONGS_TO]-> House
- Issue -[:LOCATED_IN]-> Area
- Issue -[:IN_BOOTH]-> Booth

Rules:
- Use ONLY MATCH and RETURN
- Do NOT use CREATE, DELETE, MERGE, SET
- Return ONLY Cypher query
"""

    schema = custom_schema + "\n\n" + db_schema

    # 2. Generate Cypher
    cypher = ollama_client.generate_cypher(schema, question)

    # 🔥 3. AUTO-CORRECT (CRITICAL FIX)
    cypher = cypher.replace("Voter", "Person")
    cypher = cypher.replace("Complaint", "Issue")

    # 4. Safety check
    if BLOCKED_KEYWORDS.search(cypher):
        return {
            "cypher": cypher,
            "data": [],
            "graph": {"nodes": [], "edges": []},
            "answer": (
                "⚠️ The generated query was blocked because it contains a "
                "write/destructive operation."
            ),
        }

    # 5. Execute query
    try:
        raw_records = neo4j_client.run_read_query_raw(cypher)
    except Exception as e:
        return {
            "cypher": cypher,
            "data": [],
            "graph": {"nodes": [], "edges": []},
            "answer": f"⚠️ Failed to execute the generated Cypher query: {str(e)}",
        }

    # 6. Extract data
    data = [record.data() for record in raw_records]

    try:
        graph = neo4j_client.extract_graph(raw_records)
    except Exception:
        graph = {"nodes": [], "edges": []}

    # 7. Generate answer
    try:
        answer = ollama_client.summarize_results(question, cypher, data)
    except Exception as e:
        answer = f"Query executed but summary failed: {str(e)}"

    return {
        "cypher": cypher,
        "data": data,
        "graph": graph,
        "answer": answer,
    }