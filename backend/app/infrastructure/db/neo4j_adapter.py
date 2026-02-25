from neo4j import AsyncGraphDatabase
from app.core.config import settings

class Neo4jAdapter:
    def __init__(self):
        self.driver = AsyncGraphDatabase.driver(
            settings.process.env.NEO4J_URI, 
            auth=(settings.process.env.NEO4J_USERNAME, settings.process.env.NEO4J_PASSWORD)
        )

    async def close(self):
        await self.driver.close()

    async def execute_write(self, query, parameters=None):
        async with self.driver.session() as session:
            return await session.execute_write(lambda tx: tx.run(query, parameters).data())

    async def execute_read(self, query, parameters=None):
        async with self.driver.session() as session:
            return await session.execute_read(lambda tx: tx.run(query, parameters).data())