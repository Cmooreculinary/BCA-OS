"""VaultSpace write layer — MongoDB-backed. Conrad writes here; never to NotebookLM."""
import os
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

_client: AsyncIOMotorClient | None = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(os.environ["MONGO_URI"])
    return _client[os.environ.get("MONGO_DB", "expo_os")]


async def vault_write(source: str, content: str, tags: list[str] | None = None) -> str:
    """Write a result to vaultspace collection. Returns inserted document id."""
    doc = {
        "source": source,
        "content": content,
        "tags": tags or [],
        "ts": datetime.now(timezone.utc),
    }
    result = await _db()["vaultspace"].insert_one(doc)
    return str(result.inserted_id)


async def vault_read_recent(limit: int = 10) -> list[dict]:
    """Return the most recent vaultspace entries (for context injection)."""
    cursor = _db()["vaultspace"].find({}, {"_id": 0}).sort("ts", -1).limit(limit)
    return await cursor.to_list(length=limit)
