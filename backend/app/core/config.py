from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    NEO4J_URI: str
    NEO4J_USERNAME: str
    NEO4J_PASSWORD: str
    OLLAMA_URL: str = "http://localhost:11434"

    class Config:
        env_file = Path(__file__).resolve().parent.parent.parent / ".env"


settings = Settings()
