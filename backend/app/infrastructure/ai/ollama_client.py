#to communicate with
import ollama
import json
from app.core.config import settings

class OllamaClient:
    def __init__(self):
        self.client = ollama.AsyncClient(host=settings.OLLAMA_HOST)
        self.model = "llama3."

    async def generate_response(self, prompt: str, is_json: bool = False):
        try:
            response = await self.client.generate(
                model=self.model,
                prompt=prompt,
                format="json" if is_json else "",
                options={"temperature": 0}  # Keep it logic-heavy, not creative
            )
            return response.response
        except Exception as e:
            print(f"Ollama Error: {e}")
            return None