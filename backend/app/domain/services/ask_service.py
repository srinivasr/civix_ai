import re
from app.infrastructure.ai.ollama_client import ollama_client
from app.infrastructure.db.neo4j_client import neo4j_client

# Cypher keywords that indicate a write/destructive operation
BLOCKED_KEYWORDS = re.compile(
    r"\b(DELETE|CREATE|MERGE|SET|REMOVE|DROP|DETACH)\b",
    re.IGNORECASE,
)


def ask_question(question: str) -> dict:
    """Full pipeline: question → schema → Cypher → safety → execute → graph + answer.

    Returns: { cypher, data, graph, answer }
    """
    # 1. Fetch the live schema from Neo4j
    schema = neo4j_client.get_schema()

    # 2. Generate Cypher from question + schema via Ollama
    cypher = ollama_client.generate_cypher(schema, question)

    # 3. Safety check — block destructive Cypher
    if BLOCKED_KEYWORDS.search(cypher):
        return {
            "cypher": cypher,
            "data": [],
            "graph": {"nodes": [], "edges": []},
            "answer": (
                "⚠️ The generated query was blocked because it contains a "
                "write/destructive operation (DELETE, CREATE, MERGE, SET, "
                "REMOVE, DROP, or DETACH). Only read-only queries are allowed."
            ),
        }

    # 4. Execute the safe Cypher against Neo4j (raw records for graph extraction)
    try:
        raw_records = neo4j_client.run_read_query_raw(cypher)
    except Exception as e:
        return {
            "cypher": cypher,
            "data": [],
            "graph": {"nodes": [], "edges": []},
            "answer": f"⚠️ Failed to execute the generated Cypher query: {str(e)}",
        }

    # 5. Extract tabular data (dicts) and graph data (nodes/edges)
    data = [record.data() for record in raw_records]

    try:
        graph = neo4j_client.extract_graph(raw_records)
    except Exception:
        graph = {"nodes": [], "edges": []}

    # 6. Summarize results into a natural-language answer via Ollama
    try:
        answer = ollama_client.summarize_results(question, cypher, data)
    except Exception as e:
        answer = f"Query executed successfully but failed to generate summary: {str(e)}"

    return {
        "cypher": cypher,
        "data": data,
        "graph": graph,
        "answer": answer,
    }
