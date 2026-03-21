import requests
from app.core.config import settings


class OllamaClient:
    """HTTP client for Ollama's /api/generate endpoint."""

    def __init__(self):
        self.base_url = settings.OLLAMA_URL
        self.model = "tomasonjo/llama3-text2cypher-demo:8b_4bit"

    def generate_cypher(self, schema: str, question: str) -> str:
        """Prompt the LLM with graph schema + user question → read-only Cypher."""
        prompt = f"""You are an elite Neo4j Cypher expert. Given the Neo4j graph database schema below, your task is to write a single READ-ONLY Cypher query that accurately and safely answers the user's question.

### DATABASE SCHEMA ###
{schema}

### STRICT RULES FOR CYPHER GENERATION ###
1. ONLY USE EXISTING ENTITIES: Use strictly the node labels, relationship types, and properties found in the schema above. NEVER hallucinate or invent new schema elements (e.g. use 'epic' for voters, not 'voter_id').
2. CASE-INSENSITIVE STRING MATCHING: ALWAYS compare string properties gracefully by lowercasing them. Never use exact dictionaries like `{{gender: 'Male'}}`. ALWAYS use `WHERE toLower(v.name) CONTAINS 'sharma'` or `toLower(v.gender) = 'male'`.
3. NUMERICAL COMPARISONS: Natively compare integers without string functions or quotes. Example: `WHERE v.age > 50`.
4. NO DATA MUTATION (READ-ONLY): You are strictly forbidden from altering the graph. NEVER use CREATE, DELETE, SET, MERGE, REMOVE, DROP, or DETACH. Use only MATCH, WITH, OPTIONAL MATCH, and RETURN.
5. GRAPH VISUALIZATION (RETURN ENTITIES): To render the UI graph correctly, ALWAYS explicitly RETURN the complete path or individual nodes and relationships. DO NOT return primitive properties like `RETURN v.name`. Example: Use `RETURN v, c` instead of `RETURN v.name, c.status`. If matching relationships, return them explicitly: `MATCH (v)-[r]->(b) RETURN v, r, b`.
6. FAMILY RELATIONSHIPS ARE PROPERTIES: Do NOT confuse human "family relationships" with graph edges. If a user asks for "relationships of the voters" or "fathers", check the `relation_name` and `relation_type` properties on the `Voter` node directly. Do NOT write `MATCH (v)-[:FATHER]->(x)`. Use `MATCH (v:Voter) WHERE v.relation_type IS NOT NULL RETURN v`.
7. DO NOT LIMIT RESULTS: NEVER use the `LIMIT` keyword in your query unless the user EXPLICITLY asks for a specific number of results (e.g., "top 5"). Always return the full dataset.
8. FALLBACK RESPONSE: If the question cannot be answered with the given schema, output exactly: `MATCH (n) RETURN n LIMIT 0`.
9. OUTPUT FORMATTING: Output ONLY the raw, executable Cypher query. No explanations, no markdown formatting, no code fences.

### EXAMPLES ###
Question: "List all the male voters"
Cypher: MATCH (v:Voter) WHERE toLower(v.gender) = 'male' RETURN v

Question: "List all the voters above the age of 50"
Cypher: MATCH (v:Voter) WHERE v.age > 50 RETURN v

Question: "Show me open complaints about water"
Cypher: MATCH (v:Voter)-[r:REPORTED]->(c:Complaint) WHERE toLower(c.status) = 'open' AND toLower(c.issue_type) CONTAINS 'water' RETURN v, r, c

Question: "Show me the family relationships of the voters"
Cypher: MATCH (v:Voter) WHERE v.relation_type IS NOT NULL AND v.relation_name IS NOT NULL RETURN v

Question: "Show all the relationships"
Cypher: MATCH (n)-[r]->(m) RETURN n, r, m

QUESTION: "{question}"

CYPHER QUERY:"""

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
