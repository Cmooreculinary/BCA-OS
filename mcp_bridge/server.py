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


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


_CONRAD_SYSTEM = """You are Conrad — the central brain beneath BCA OS, named for Conrad Hilton.

You serve Christopher Moore, founder of Blue Collar Apps Co. (BCA). BCA builds software for operators in the field: restaurant managers, venue staff, food truck owners. Philosophy: Trench Design — software built bottom-up from operator experience.

BCA OS hierarchy: BCA OS → Conrad → Companies, Projects, Products, Apps, Agents, Staff, Specialized brains, Founder projects, Founder-private systems.

Active BCA projects:
- Round Table: venue/restaurant management (Iteration 18+)
- Verdict AI: five-chamber AI judgment system (FastAPI)
- Captain Culinary Kids (CapKids): youth culinary education, AWANA pitch
- Smoky Top: luxury home construction platform
- FuseBox 2.0: Forge design system
- BrainForge: private banking/Bloomberg aesthetic (Vercel)
- Maestro + Vaultspace: life management bundle, Smart Inbox pipeline
- Hemispheres: Democrat-Republican fact-checker (HTML/JS)
- Food Truck Launchpad: agent fleet reference architecture (TBD)
- DUSK, Valet Captain, PUBHUB, PLATE ME, Foxhounds: consumer apps (TBD)

Infrastructure: FastAPI + SQLite (deterministic flows), MongoDB (primary DB), Stripe (payments), Vercel (frontend), n8n (orchestration), NotebookLM Galaxies (recall), VaultSpace (write memory).

Delegation law: judgment/planning/identity → you. Instant deterministic flows → FastAPI. Memory write → VaultSpace. Action/orchestration → n8n. Heavy coding → GLM-5.2 (never give it secrets). Architecture review → Opus 4.8.

Your role: answer questions, discuss BCA strategy, think through decisions, serve as the founder's thinking partner. Be direct, concise, and practical — no fluff. You are a force multiplier, not a replacement.

Guardrails: never route live Stripe keys or customer data through third-party cloud LLMs. Hot-path stays deterministic. Agents live at the edges only."""


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
  .chat-wrap{margin-top:24px;max-width:1100px}
  .chat-messages{height:340px;overflow-y:auto;background:#0a0a0a;border:1px solid #1e1e1e;border-radius:4px;padding:12px;margin-bottom:10px}
  .msg{margin-bottom:14px;font-size:13px;line-height:1.6}
  .msg.user{text-align:right}
  .msg.user .bubble{display:inline-block;background:#1a2a1e;border:1px solid #2a5c45;border-radius:6px 6px 0 6px;padding:8px 12px;color:#e8e8e8;max-width:80%;text-align:left;white-space:pre-wrap}
  .msg.assistant .bubble{display:inline-block;background:#111;border:1px solid #222;border-radius:6px 6px 6px 0;padding:8px 12px;color:#c8c8c8;max-width:80%;white-space:pre-wrap}
  .msg.assistant .name{font-size:10px;color:#5ddb9a;margin-bottom:4px;letter-spacing:.1em;text-transform:uppercase}
  .chat-input-row{display:flex;gap:10px;align-items:flex-end}
  .chat-input-row textarea{flex:1;min-height:52px;resize:vertical}
  #chat-send{padding:12px 20px;align-self:flex-end}
  #chat-thinking{font-size:11px;color:#555;margin-top:6px;min-height:16px}
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
<div class="chat-wrap">
  <div class="card">
    <h2>Talk to Conrad</h2>
    <div id="chat-messages" class="chat-messages">
      <div class="msg assistant">
        <div class="name">Conrad</div>
        <div class="bubble">Hello, Christopher. I&#x27;m Conrad &#x2014; the BCA OS brain. Ask me anything about the portfolio, strategy, routing, or what to build next.</div>
      </div>
    </div>
    <div class="chat-input-row">
      <textarea id="chat-input" placeholder="Ask Conrad anything..." rows="2"></textarea>
      <button id="chat-send" class="primary" onclick="sendMessage()">Send</button>
    </div>
    <div id="chat-thinking"></div>
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

document.getElementById('chat-input').addEventListener('keydown', e => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') sendMessage();
});

let chatHistory = [];

function escapeHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function appendMsg(role, text) {
  const el = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = 'msg ' + role;
  if (role === 'assistant') {
    div.innerHTML = '<div class="name">Conrad</div><div class="bubble">' + escapeHtml(text) + '</div>';
  } else {
    div.innerHTML = '<div class="bubble">' + escapeHtml(text) + '</div>';
  }
  el.appendChild(div);
  el.scrollTop = el.scrollHeight;
}

async function sendMessage() {
  const input = document.getElementById('chat-input');
  const msg = input.value.trim();
  if (!msg) return;
  const btn = document.getElementById('chat-send');
  const thinking = document.getElementById('chat-thinking');
  appendMsg('user', msg);
  input.value = '';
  btn.disabled = true;
  thinking.textContent = 'Conrad is thinking...';
  try {
    const res = await fetch(API + '/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: msg, history: chatHistory})
    });
    if (!res.ok) throw new Error(await res.text());
    const r = await res.json();
    chatHistory = r.history;
    appendMsg('assistant', r.reply);
  } catch(e) {
    appendMsg('assistant', 'Error: ' + e.message);
  }
  thinking.textContent = '';
  btn.disabled = false;
}

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


@app.post("/chat")
async def chat(req: ChatRequest):
    """Conrad conversational AI — multi-turn chat backed by Claude Opus 4.8."""
    import asyncio
    import anthropic

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY not configured")

    def _call():
        client = anthropic.Anthropic(api_key=api_key)
        messages = req.history + [{"role": "user", "content": req.message}]
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=4096,
            thinking={"type": "adaptive"},
            system=_CONRAD_SYSTEM,
            messages=messages,
        )
        reply = next((b.text for b in response.content if b.type == "text"), "")
        updated_history = messages + [{"role": "assistant", "content": reply}]
        return {"reply": reply, "history": updated_history}

    try:
        return await asyncio.to_thread(_call)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8001)), reload=False)
