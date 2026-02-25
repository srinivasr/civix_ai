#This is the heart of the "Knowledge Graph" loop. It handles the three stages: Translate (to Cypher), Execute (in Neo4j), and Summarize (to Human).
import json
from app.infrastructure.ai.ollama_client import OllamaClient
from app.infrastructure.db.neo4j_adapter import Neo4jAdapter

class LLMGraphService:
    def __init__(self):
        self.ai = OllamaClient()
        self.db = Neo4jAdapter()

    async def extract_and_save_entities(self, raw_note: str):
        """
        The 'Living Graph' Engine: Converts raw text into Neo4j nodes and edges.
        """
        extract_prompt = f"""
        Extract entities and relationships from this note for an electoral database.
        Return ONLY valid JSON.
        
        Labels: Voter, Booth, Sentiment
        Relationships: ASSIGNED_TO, INFLUENCES, WORKS_AT
        
        Format: 
        {{ 
          "nodes": [{{ "label": "Voter", "properties": {{ "name": "string", "voter_id": "string" }} }}], 
          "rels": [{{ "start_node": "name1", "end_node": "name2", "type": "INFLUENCES" }}] 
        }}
        
        Note: {raw_note}
        """

        # 1. Get the extraction from Ollama
        extraction_raw = await self.ai.generate_response(extract_prompt, is_json=True)
        if not extraction_raw:
            return "Failed to extract data from note."
        
        data = json.loads(extraction_raw)

        # 2. Persist Nodes to Neo4j
        # We use MERGE so we don't create duplicate voters every time a note is updated
        for node in data.get("nodes", []):
            label = node.get("label")
            props = node.get("properties", {})
            
            # Ruthless Check: Ensure we have a unique identifier
            if "name" not in props: continue 
            
            query = f"MERGE (n:{label} {{name: $name}}) SET n += $props"
            await self.db.execute_write(query, {"name": props["name"], "props": props})

        # 3. Persist Relationships
        for rel in data.get("rels", []):
            query = f"""
            MATCH (a {{name: $start}}), (b {{name: $end}})
            MERGE (a)-[r:{rel['type']}]->(b)
            """
            await self.db.execute_write(query, {"start": rel['start_node'], "end": rel['end_node']})

        return "Graph updated successfully and nodes merged."