import asyncio
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.v1.endpoints.upload import router as upload_router
from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.ask import router as ask_router
from app.domain.services.seed_graph import seed


async def auto_update_csv():
    voters_file = Path("data/uploads/voters.csv")
    last_mtime = 0
    if voters_file.exists():
        last_mtime = os.stat(voters_file).st_mtime

    while True:
        await asyncio.sleep(2)
        if voters_file.exists():
            current_mtime = os.stat(voters_file).st_mtime
            if current_mtime > last_mtime:
                print("💥 Detected change in voters.csv! Auto-updating Neo4j database...")
                last_mtime = current_mtime
                try:
                    seed()
                    print("✅ Auto-update complete!")
                except Exception as e:
                    print(f"❌ Auto-update failed: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Seed initially if needed, and start watcher
    task = asyncio.create_task(auto_update_csv())
    yield
    task.cancel()

app = FastAPI(title="Civix AI Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix="/api/v1/upload", tags=["Upload"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(ask_router, prefix="/api/v1", tags=["Ask"])


@app.get("/")
def health():
    return {"status": "Backend running"}
