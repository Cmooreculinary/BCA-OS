"""
MCP Bridge — FastAPI service exposing Conrad's Galaxy (read) + VaultSpace (write) tools.

Runs on Render as an always-on service. n8n calls /conrad for the closed loop.
"""
import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from galaxy_client import galaxy_query
from vaultspace import vault_write, vault_read_recent

app = FastAPI(title="Conrad MCP Bridge", version="0.1.0")


class ConradRequest(BaseModel):
    task: str
    notebook_id: str | None = None


class VaultWriteRequest(BaseModel):
    source: str
    content: str
    tags: list[str] = []


@app.get("/health")
async def health():
    return {"status": "ok", "service": "conrad-mcp-bridge"}


@app.post("/galaxy/query")
async def query_galaxy(req: ConradRequest):
    """Conrad reads a Galaxy — returns source-grounded answer with citations."""
    try:
        result = await galaxy_query(req.task, req.notebook_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/vault/write")
async def write_vault(req: VaultWriteRequest):
    """Write a result to VaultSpace (MongoDB). Returns the inserted document id."""
    try:
        doc_id = await vault_write(req.source, req.content, req.tags)
        return {"inserted_id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.get("/vault/recent")
async def read_vault(limit: int = 10):
    """Return recent VaultSpace entries for context injection."""
    try:
        entries = await vault_read_recent(limit)
        return {"entries": entries}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/conrad")
async def conrad_loop(req: ConradRequest):
    """
    The full loop in one call — used by n8n's loop runner (Packet D):
      1. Query Galaxy for source-grounded answer.
      2. Write result to VaultSpace.
      3. Return result + vault id for memory.md append.
    """
    try:
        galaxy_result = await galaxy_query(req.task, req.notebook_id)
        vault_id = await vault_write(
            source="conrad-loop",
            content=galaxy_result["answer"],
            tags=["loop", "auto"],
        )
        return {
            "answer": galaxy_result["answer"],
            "citations": galaxy_result["citations"],
            "grounded": galaxy_result["grounded"],
            "vault_id": vault_id,
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8001)), reload=False)
