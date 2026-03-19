from app.infrastructure.db.neo4j_client import neo4j_client


def get_neo4j_dependency():
    """Dependency injection for Neo4j client."""
    return neo4j_client
