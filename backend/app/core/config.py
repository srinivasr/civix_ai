from pydantic import BaseSettings

class Settings(BaseSettings):
    NEO4J_URI: str
    NEO4J_USERNAME: str
    NEO4J_PASSWORD: str

    class Config:
        env_file = ".env"

settings = Settings()