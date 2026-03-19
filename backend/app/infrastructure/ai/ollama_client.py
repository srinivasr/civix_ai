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
- Return ONLY the Cypher query, no explanations, no markdown fences.
- Use ONLY labels, relationship types, and property keys from the schema above.
- NEVER use DELETE, CREATE, MERGE, SET, REMOVE, DROP, or DETACH.
- Always use MATCH and RETURN.
- IMPORTANT: For string properties (like gender, issue, name), NEVER use direct dictionary matches (e.g. {{gender: 'Male'}} or {{gender: toLower('male')}}). ALWAYS use a WHERE clause with `toLower()` (e.g. `WHERE toLower(v.gender) = 'male'`).
- If the question cannot be answered with the schema, return: MATCH (n) RETURN n LIMIT 0

EXAMPLES:
Question: "list all the male voters"
Cypher: MATCH (v:Voter) WHERE toLower(v.gender) = 'male' RETURN v

Question: "show me open complaints"
Cypher: MATCH (c:Complaint) WHERE toLower(c.status) = 'open' RETURN c

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
