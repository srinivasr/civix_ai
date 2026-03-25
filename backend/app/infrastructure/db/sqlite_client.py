"""SQLite database engine and session management via SQLModel."""

from pathlib import Path
from sqlmodel import SQLModel, Session, create_engine

DB_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite:///{DB_DIR / 'app.db'}"

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


def init_db():
    """Create all SQLModel tables (idempotent)."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency that yields a SQLModel Session."""
    with Session(engine) as session:
        yield session
