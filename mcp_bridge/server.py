from __future__ import annotations

"""
MCP Bridge — FastAPI service exposing Conrad's Galaxy (read) + VaultSpace (write) tools.

Runs on Render as an always-on service. n8n calls /conrad for the closed loop.
"""
import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

try:
    from .galaxy_client import galaxy_query
    from .intake import IntakeRequest, classify_and_route
    from .vaultspace import (
        intake_read,
        intake_read_recent,
        intake_store,
        vault_read_recent,
        vault_write,
    )
except ImportError:  # pragma: no cover - supports `python server.py` from mcp_bridge/
    from galaxy_client import galaxy_query
    from intake import IntakeRequest, classify_and_route
    from vaultspace import intake_read, intake_read_recent, intake_store, vault_read_recent, vault_write

app = FastAPI(title="Conrad MCP Bridge", version="0.2.0")


class ConradRequest(BaseModel):
    task: str
    notebook_id: str | None = None


class VaultWriteRequest(BaseModel):
    source: str
    content: str
    tags: list[str] = []


_UI = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Conrad — BCA OS</title>
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:#0a0a0a;color:#e8e8e8;font-family:'SF Mono',ui-monospace,monospace;min-height:100vh;padding:32px 24px}
  header{border-bottom:1px solid #222;padding-bottom:20px;margin-bottom:32px}
  h1{font-size:22px;font-weight:600;letter-spacing:.05em;color:#fff}
  h1 span{color:#666;font-weight:400}
  .subtitle{color:#555;font-size:12px;margin-top:4px;letter-spacing:.08em;text-transform:uppercase}
  .grid{display:grid;grid-template-columns:1fr 1fr;gap:24px;max-width:1100px}
  @media(max-width:700px){.grid{grid-template-columns:1fr}}
  .card{background:#111;border:1px solid #1e1e1e;border-radius:6px;padding:20px}
  .card h2{font-size:11px;text-transform:uppercase;letter-spacing:.1em;color:#555;margin-bottom:14px}
  textarea{width:100%;background:#0a0a0a;border:1px solid #2a2a2a;border-radius:4px;color:#e8e8e8;font-family:inherit;font-size:13px;padding:10px;resize:vertical;min-height:100px;outline:none}
  textarea:focus{border-color:#444}
  .row{display:flex;gap:10px;margin-top:10px;align-items:center}
  input[type=text]{flex:1;background:#0a0a0a;border:1px solid #2a2a2a;border-radius:4px;color:#e8e8e8;font-family:inherit;font-size:12px;padding:8px 10px;outline:none}
  input[type=text]:focus{border-color:#444}
  input::placeholder{color:#444}
  button{background:#1a1a1a;border:1px solid #333;border-radius:4px;color:#ccc;cursor:pointer;font-family:inherit;font-size:12px;padding:8px 16px;transition:background .15s}
  button:hover{background:#252525;color:#fff}
  button.primary{background:#1c3a2e;border-color:#2a5c45;color:#5ddb9a}
  button.primary:hover{background:#224836}
  #receipt,#recent{margin-top:14px;font-size:12px;line-height:1.7}
  .tag{display:inline-block;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:3px;font-size:11px;padding:1px 7px;margin:2px 2px 2px 0;color:#888}
  .tag.green{border-color:#2a5c45;color:#5ddb9a}
  .tag.yellow{border-color:#5c4e1a;color:#dbb85d}
  .tag.red{border-color:#5c1a1a;color:#db5d5d}
  .row-item{border-bottom:1px solid #1a1a1a;padding:10px 0;font-size:12px}
  .row-item:last-child{border-bottom:none}
  .row-item .meta{color:#555;font-size:11px;margin-top:3px}
  .status-dot{display:inline-block;width:6px;height:6px;border-radius:50%;background:#5ddb9a;margin-right:6px;vertical-align:middle}
  #status-bar{font-size:11px;color:#555;margin-top:6px}
  #error{color:#db5d5d;font-size:12px;margin-top:8px;display:none}
</style>
</head>
<body>
<header>
  <h1>Conrad <span>/ BCA OS</span></h1>
  <div class="subtitle">Founder Interface &mdash; Central Intake &amp; Routing</div>
</header>
<div class="grid">
  <div class="card">
    <h2>Submit to Conrad</h2>
    <textarea id="content" placeholder="Drop anything here — bug report, idea, decision, task, note, credential (will be auto-redacted)..."></textarea>
    <div class="row">
      <input type="text" id="source" placeholder="Source (optional)" value="founder-ui"/>
      <input type="text" id="project" placeholder="Project (optional)"/>
      <button class="primary" onclick="submitIntake()">Route &#8594;</button>
    </div>
    <div id="error"></div>
    <div id="status-bar"></div>
    <div id="receipt"></div>
  </div>
  <div class="card">
    <h2>Recent VaultSpace Entries</h2>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
      <span style="font-size:11px;color:#555">Last 10 items routed</span>
      <button onclick="loadRecent()" style="font-size:11px;padding:4px 10px">Refresh</button>
    </div>
    <div id="recent"><span style="color:#444;font-size:12px">Loading...</span></div>
  </div>
</div>
<script>
const API = '';

function tag(text, color) {
  return `<span class="tag ${color||''}">${text}</span>`;
}

function sensitivityColor(s) {
  if (!s) return '';
  if (s === 'SECRET') return 'red';
  if (s === 'FOUNDER_ONLY') return 'yellow';
  return 'green';
}

async function submitIntake() {
  const content = document.getElementById('content').value.trim();
  if (!content) return;
  const source = document.getElementById('source').value.trim() || 'founder-ui';
  const project = document.getElementById('project').value.trim() || undefined;
  document.getElementById('status-bar').textContent = 'Routing...';
  document.getElementById('receipt').innerHTML = '';
  document.getElementById('error').style.display = 'none';
  try {
    const body = {content, source};
    if (project) body.project = project;
    const res = await fetch(API + '/intake', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error(await res.text());
    const r = await res.json();
    document.getElementById('status-bar').textContent = '';
    document.getElementById('receipt').innerHTML = `
      <div style="margin-top:4px">
        ${tag(r.classification.replace(/_/g,' '))}
        ${tag(r.sensitivity, sensitivityColor(r.sensitivity))}
        ${r.project ? tag(r.project) : ''}
        ${r.approval_required ? tag('approval required','yellow') : ''}
      </div>
      <div style="margin-top:10px;color:#555;font-size:11px">
        <div>&#8594; ${r.primary_destination}</div>
        ${r.secondary_destination ? `<div>&#8594; ${r.secondary_destination}</div>` : ''}
        <div style="margin-top:6px;color:#333">${r.intake_id}</div>
      </div>`;
    loadRecent();
  } catch(e) {
    document.getElementById('status-bar').textContent = '';
    document.getElementById('error').textContent = e.message;
    document.getElementById('error').style.display = 'block';
  }
}

async function loadRecent() {
  const el = document.getElementById('recent');
  try {
    const res = await fetch(API + '/intake/recent?limit=10');
    const data = await res.json();
    const entries = data.entries || [];
    if (!entries.length) { el.innerHTML = '<span style="color:#444">No entries yet.</span>'; return; }
    el.innerHTML = entries.map(e => `
      <div class="row-item">
        <div>${tag(e.classification?.replace(/_/g,' '))||''} ${tag(e.sensitivity||'NORMAL', sensitivityColor(e.sensitivity))}</div>
        <div class="meta">${(e.content||'').slice(0,90)}${(e.content||'').length > 90 ? '...' : ''}</div>
        <div class="meta" style="color:#333;margin-top:2px">${e.intake_id||''} &middot; ${(e.timestamp||'').slice(0,16).replace('T',' ')}</div>
      </div>`).join('');
  } catch(e) {
    el.innerHTML = '<span style="color:#555">Could not load entries.</span>';
  }
}

document.getElementById('content').addEventListener('keydown', e => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') submitIntake();
});

loadRecent();
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def ui():
    return _UI


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
    """Write a result to VaultSpace (SQLite). Returns the inserted document id."""
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


@app.post("/intake")
async def create_intake(req: IntakeRequest):
    """Deterministically classify and route a Conrad intake item."""
    record, audit_record, receipt = classify_and_route(req)
    try:
        await intake_store(record, audit_record)
        return receipt
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.get("/intake/recent")
async def read_recent_intake(limit: int = 10):
    """Return recent Conrad intake records."""
    try:
        entries = await intake_read_recent(limit)
        return {"entries": entries}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.get("/intake/{intake_id}")
async def read_intake_item(intake_id: str):
    """Return one Conrad intake record."""
    try:
        record = await intake_read(intake_id)
        if record is None:
            raise HTTPException(status_code=404, detail="intake item not found")
        return record
    except HTTPException:
        raise
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
