import requests
from app.core.config import settings


class OllamaClient:
    """HTTP client for Ollama's /api/generate endpoint."""

    def __init__(self):
        self.base_url = settings.OLLAMA_URL
        self.model = "llama3:latest"

    def generate_cypher(self, schema: str, question: str) -> str:
        """Prompt the LLM with graph schema + user question → read-only Cypher."""
        prompt = f"""You are a Neo4j Cypher expert. Given the graph database schema below,
write a single READ-ONLY Cypher query to answer the user's question.

SCHEMA:
{schema}

RULES:
1. SCHEMA STRICTNESS: Use ONLY labels, relationship types, and properties provided in the schema. Do NOT hallucinate or invent properties.
2. STRING MATCHING (CRITICAL): For string properties, NEVER use exact dictionary matches (e.g. {{gender: 'Male'}}). ALWAYS use a case-insensitive WHERE clause. For robustness, prefer CONTAINS for partial matching where appropriate: `WHERE toLower(v.name) CONTAINS 'sharma'`.
3. NUMERICAL MATCHING: DO NOT use string functions (`toLower()`) or string quotes (`'50'`) for numerical properties (like `age`, `booth_id`). Compare them natively: `WHERE v.age > 50`.
4. RETURN GRAPH ENTITIES: Always RETURN the actual nodes or relationships (e.g., `RETURN v, c`), NOT just their properties (e.g., avoid `RETURN v.name`). This is required for the application's graph visualization.
5. READ-ONLY: NEVER use DELETE, CREATE, MERGE, SET, REMOVE, DROP, or DETACH. Only use MATCH, OPTIONAL MATCH, WITH, and RETURN.
6. FALLBACK: If the question cannot be answered with the given schema, return exactly: MATCH (n) RETURN n LIMIT 0
7. FORMATTING: Return ONLY the valid Cypher query, no conversational explanations, and no markdown fences.

EXAMPLES:
Question: "list all the male voters"
Cypher: MATCH (v:Voter) WHERE toLower(v.gender) = 'male' RETURN v

Question: "list all the voters above the age of 50"
Cypher: MATCH (v:Voter) WHERE v.age > 50 RETURN v

Question: "show me open complaints about water"
Cypher: MATCH (v:Voter)-[:REPORTED]->(c:Complaint) WHERE toLower(c.status) = 'open' AND toLower(c.issue_type) CONTAINS 'water' RETURN v, c

QUESTION: {question}

CYPHER:"""

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0},
            },
            timeout=120,
        )
        response.raise_for_status()
        cypher = response.json().get("response", "").strip()

        # Strip markdown fences if the model wraps the output
        if cypher.startswith("```"):
            lines = cypher.split("\n")
            lines = [line for line in lines if not line.startswith("```")]
            cypher = "\n".join(lines).strip()

        return cypher

    def summarize_results(self, question: str, cypher: str, results: list) -> str:
        """Prompt the LLM with question + Cypher + results → natural-language answer."""
        prompt = f"""You are a helpful civic data analyst. Given a user's question,
the Cypher query that was executed, and the query results, provide a clear,
concise natural-language summary.

QUESTION: {question}

CYPHER QUERY:
{cypher}

QUERY RESULTS:
{results}

Provide a helpful, human-readable answer. Be concise and direct. Do not include
the Cypher query in your answer. If the results are empty, say so clearly.

ANSWER:"""

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0},
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()


ollama_client = OllamaClient()
