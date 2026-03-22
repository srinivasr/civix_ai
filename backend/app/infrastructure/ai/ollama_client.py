import requests
from app.core.config import settings


class OllamaClient:
    """HTTP client for Ollama's /api/generate endpoint."""

    def __init__(self):
        self.base_url = settings.OLLAMA_URL
        self.model = "tomasonjo/llama3-text2cypher-demo:8b_4bit"

    def generate_cypher(self, schema: str, question: str) -> str:
        """Prompt the LLM with graph schema + user question → read-only Cypher."""
        prompt = f"""[OBJECTIVE]
Convert natural language into high-performance, READ-ONLY Neo4j Cypher.

[CONTEXT]
You are a Senior Neo4j Architect. You interpret user questions against a provided <schema> to produce executable code.

<schema>
{schema}
</schema>

[THOUGHT_PROCESS_STRICT]
Before outputting Cypher, you must internally:
1. IDENTIFY: Which nodes and relationships in the <schema> match the user's intent?
2. CASE-INSENSITIVE: Always apply `toLower()` to string comparisons (e.g., `WHERE toLower(v.name) CONTAINS 'sharma'`).
3. STRUCTURE: Ensure the RETURN statement includes full entities (nodes/relationships) for UI rendering (e.g. `RETURN n`). 
4. GRAPH VISUALIZATION: To show a graph in the UI, you MUST return the nodes and the connections. For example, instead of `RETURN v.name, h.house_no`, use `RETURN v, r, h`. NEVER return just properties or strings if a graph is expected.
5. VALIDATE: Check for any mutating keywords (CREATE, MERGE, SET, DELETE). If found, remove them.
6. FAMILY RELATIONSHIPS: "Family" is stored as string properties (`relation_name`, `relation_type`) on the Voter node. Do NOT invent a `[:FATHER]` edge.
7. IDs AND TYPES: `booth_id` is always a string formatted as e.g. "MH_123_001". Do not treat it as an integer.
8. FALLBACK: If the schema is insufficient, your only allowed output is the fallback query (`MATCH (n) RETURN n LIMIT 0`).

[CONSTRAINTS]
- NO markdown formatting (no ```cypher).
- NO explanations or preamble outside the XML tags.

[OUTPUT_FORMAT]
You MUST output your response exactly in this XML format:
<logic>
Write a short 1-sentence explanation of your approach.
</logic>
<query>
Write the executable Cypher query here.
</query>

[EXAMPLES]
Question: "Show me all the male voters"
<logic>
I will find Voter nodes where the lowercase gender property equals 'male'.
</logic>
<query>
MATCH (v:Voter) WHERE toLower(v.gender) = 'male' RETURN v
</query>

Question: "Show all the relationships"
<logic>
I will match all nodes connected by any relationship and return the full nodes and connections.
</logic>
<query>
MATCH (n)-[r]->(m) RETURN n, r, m
</query>

Question: "Who lives in house number 5?"
<logic>
I will find the House node with house_no '5' and the Voter nodes connected to it via LIVES_IN.
</logic>
<query>
MATCH (v:Voter)-[r:LIVES_IN]->(h:House) WHERE h.house_no = '5' RETURN v, r, h
</query>

QUESTION: "{question}"

OUTPUT:"""

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
        raw_text = response.json().get("response", "").strip()

        return self._clean_cypher(raw_text)

    def _clean_cypher(self, text: str) -> str:
        """
        Extracts the query from the Antigravity XML structure.
        """
        import re
        # Find content between <query> tags
        query_match = re.search(r'<query>(.*?)</query>', text, re.DOTALL)
        if query_match:
            query = query_match.group(1).strip()
        else:
            # Fallback if the LLM failed the tags but gave the query
            query = text.replace("```cypher", "").replace("```", "").strip()

        # Final safety check: No semi-colons, no mutations
        query = query.split(';')[0].strip()
        forbidden = ["CREATE", "MERGE", "DELETE", "SET", "REMOVE", "DROP", "DETACH"]
        if any(cmd in query.upper() for cmd in forbidden):
            return "MATCH (n) RETURN n LIMIT 0"

        return query

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