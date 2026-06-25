"""VaultSpace write layer — MongoDB-backed. Conrad writes here; never to NotebookLM."""
import os
from datetime import datetime, timezone
from typing import Any

_client: Any | None = None


def _db():
    global _client
    if _client is None:
        from motor.motor_asyncio import AsyncIOMotorClient

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


async def intake_store(record: dict, audit_record: dict) -> None:
    """Store an intake item and its append-only routing audit record."""
    db = _db()
    await db["intake_items"].insert_one(record.copy())
    await db["audit_log"].insert_one(audit_record.copy())


async def intake_read_recent(limit: int = 10) -> list[dict]:
    """Return recent Conrad intake records without Mongo ObjectIds."""
    cursor = _db()["intake_items"].find({}, {"_id": 0}).sort("timestamp", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def intake_read(intake_id: str) -> dict | None:
    """Return one Conrad intake record by id."""
    return await _db()["intake_items"].find_one({"intake_id": intake_id}, {"_id": 0})
