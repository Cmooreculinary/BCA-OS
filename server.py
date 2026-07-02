"""
BCA OS web service — the Render-deployable HTTP surface for BCA OS.

Exposes the OS services (status, policy/launch gates, expedite, vault)
as a JSON API, and hosts CONRAD/EXPO — the founder-facing host brain —
behind a chat endpoint with a built-in web UI at "/".

Run locally:
    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=sk-ant-...
    uvicorn server:app --reload

On Render the service is provisioned from render.yaml.
"""
from __future__ import annotations

import json
import threading
import uuid
from typing import Any

import anthropic
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from bca_os import BCA_APPS, Sensitivity, TaskClass, boot_os

OS = boot_os()

app = FastAPI(
    title="BCA OS",
    version="1.0.0",
    description="Operating system layer for Blue Collar Apps Co. — routing, "
    "launch-gate policy, Teacher Pattern dispatch, and the CONRAD/EXPO host brain.",
)

_TASK = {t.value: t for t in TaskClass}
_SENS = {s.value: s for s in Sensitivity}

# ---------------------------------------------------------------------------
# Request/response models
# ---------------------------------------------------------------------------

class ExpediteRequest(BaseModel):
    intent: str
    task_class: str = "execution_std"
    sensitivity: str = "internal"
    domain_hint: str | None = None


class GatesRequest(BaseModel):
    gates_met: list[str] = Field(default_factory=list)


class VaultWriteRequest(BaseModel):
    key: str
    value: Any


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


# ---------------------------------------------------------------------------
# Health + OS service endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "bca-os",
        "api_key_configured": OS.api_key_configured(),
    }


@app.get("/api/status")
def status() -> dict:
    return OS.status()


@app.get("/api/policy/{brain}")
def policy(brain: str) -> dict:
    result = OS.check_policy(brain)
    if not result.get("ok", True) and "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.post("/api/policy/{brain}/gates")
def set_gates(brain: str, req: GatesRequest) -> dict:
    if brain not in BCA_APPS:
        raise HTTPException(status_code=404, detail=f"Unknown brain/app: {brain}")
    allowed = set(BCA_APPS[brain]["launch_gates"])
    unknown = [g for g in req.gates_met if g not in allowed]
    if unknown:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown gates for {brain}: {unknown}. Valid: {sorted(allowed)}",
        )
    OS.remember(f"gates_met_{brain}", req.gates_met)
    return OS.check_policy(brain)


@app.post("/api/expedite")
def expedite(req: ExpediteRequest) -> dict:
    tc = _TASK.get(req.task_class, TaskClass.EXECUTION_STD)
    sens = _SENS.get(req.sensitivity, Sensitivity.INTERNAL)
    decision = OS.route(req.intent, req.domain_hint, tc)
    if decision.policy_status.startswith("BLOCKED"):
        return {
            "routed": decision.as_dict(),
            "executed": False,
            "reason": f"Launch gate not met: {decision.policy_status}",
        }
    system = (
        "You are a BCA domain brain executing a single ticket. "
        "Trench Design: build from the operator's reality. Be exact."
    )
    try:
        out = OS.dispatch(decision, system, req.intent, sensitivity=sens)
        return {"routed": decision.as_dict(), "executed": True, "result": out}
    except RuntimeError as e:  # missing API key
        raise HTTPException(status_code=503, detail=str(e))
    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=f"Claude API error: {e}")


@app.get("/api/vault/{key}")
def vault_get(key: str) -> dict:
    return {"key": key, "value": OS.recall(key)}


@app.post("/api/vault")
def vault_set(req: VaultWriteRequest) -> dict:
    OS.remember(req.key, req.value)
    return {"saved": req.key}


# ---------------------------------------------------------------------------
# CONRAD/EXPO — host brain over HTTP (manual tool-use loop)
# ---------------------------------------------------------------------------

CONRAD_SYSTEM = """You are CONRAD/EXPO — the first brain of Blue Collar Apps Co.,
running on the BCA OS. You are the expediter and host of the BCA ecosystem.

FOUNDER: Christopher "Chef" Moore — CIA-trained, 40+ years hospitality, solo
founder augmented by an AI agent fleet. You are the top of that fleet.

PHILOSOPHY — TRENCH DESIGN: every product is built bottom-up from real
hospitality experience. "There has to be a better way."

YOUR JOB:
- HOST: be the founder-facing presence. Compressed, direct, action-oriented.
  Voice-dictated shorthand is normal. "BUILD ME" = execute and ship a finished
  artifact. "info" = give detailed next-step guidance.
- EXPEDITE: you do not cook every dish. Classify intent, then call expedite
  to route work to the right domain brain at the correct Teacher Pattern tier.
- Lead every reply with the most cost-efficient model appropriate to the task.
  Teacher Pattern: Haiku->Sonnet for execution; Opus for architecture,
  strategy, review. Never optimize cost before a quality baseline exists.

DISCIPLINE:
- Secrets: never expose full keys; never route secrets or customer data to
  free-tier/external adapters. The OS enforces this — respect its refusals.
- Gates are launch blockers, not afterthoughts: CapKids->COPPA,
  AllergenShield->liability+insurance, any SMS->A2P 10DLC+TCPA. Call
  check_policy before greenlighting a launch.

SESSION OPENER: if it's the first exchange of a session, call status and
give a live BCA App Catalog report before the work.

Use remember / recall for durable facts, and providence to log
capability-alignment moments. The pass stays clean."""

CONRAD_TOOLS: list[dict] = [
    {
        "name": "status",
        "description": "Live BCA App Catalog + OS status. Call this at the start "
        "of a session before other work.",
        "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "expedite",
        "description": "Route an intent to the right domain brain, check its launch "
        "gates, and execute it at the correct Teacher Pattern tier. Call this to "
        "delegate execution work instead of doing it yourself.",
        "input_schema": {
            "type": "object",
            "properties": {
                "intent": {"type": "string", "description": "The work to route/execute"},
                "task_class": {
                    "type": "string",
                    "enum": ["execution_light", "execution_std", "architecture", "review"],
                    "description": "Teacher Pattern tier",
                },
                "sensitivity": {
                    "type": "string",
                    "enum": ["public", "internal", "secret", "customer"],
                    "description": "Data sensitivity of the intent",
                },
                "domain_hint": {
                    "type": "string",
                    "description": "Optional domain override, e.g. youth-nutrition, "
                    "hospitality-ops, food-safety, hospitality-comms",
                },
            },
            "required": ["intent", "task_class"],
        },
    },
    {
        "name": "check_policy",
        "description": "Check launch gates for one brain (capkids, roundtable, "
        "allergenshield, trenchsms). Call before greenlighting any launch.",
        "input_schema": {
            "type": "object",
            "properties": {"brain": {"type": "string"}},
            "required": ["brain"],
        },
    },
    {
        "name": "remember",
        "description": "Persist a durable fact to the Vault under a key.",
        "input_schema": {
            "type": "object",
            "properties": {"key": {"type": "string"}, "value": {"type": "string"}},
            "required": ["key", "value"],
        },
    },
    {
        "name": "recall",
        "description": "Read a fact back from the Vault by key.",
        "input_schema": {
            "type": "object",
            "properties": {"key": {"type": "string"}},
            "required": ["key"],
        },
    },
    {
        "name": "providence",
        "description": "Log a moment where a capability arrived in alignment with "
        "a BCA need.",
        "input_schema": {
            "type": "object",
            "properties": {"note": {"type": "string"}},
            "required": ["note"],
        },
    },
]


def _run_tool(name: str, args: dict) -> dict:
    if name == "status":
        return OS.status()
    if name == "expedite":
        tc = _TASK.get(args.get("task_class", ""), TaskClass.EXECUTION_STD)
        sens = _SENS.get(args.get("sensitivity", "internal"), Sensitivity.INTERNAL)
        decision = OS.route(args["intent"], args.get("domain_hint"), tc)
        if decision.policy_status.startswith("BLOCKED"):
            return {
                "routed": decision.as_dict(),
                "executed": False,
                "reason": f"Launch gate not met: {decision.policy_status}",
            }
        system = (
            "You are a BCA domain brain executing a single ticket. "
            "Trench Design: build from the operator's reality. Be exact."
        )
        try:
            out = OS.dispatch(decision, system, args["intent"], sensitivity=sens)
            return {"routed": decision.as_dict(), "executed": True, "result": out}
        except Exception as e:
            return {"routed": decision.as_dict(), "executed": False, "error": str(e)}
    if name == "check_policy":
        return {"brain": args["brain"], "policy": OS.check_policy(args["brain"])}
    if name == "remember":
        OS.remember(args["key"], {"note": args["value"]})
        return {"saved": args["key"]}
    if name == "recall":
        return {"key": args["key"], "value": OS.recall(args["key"])}
    if name == "providence":
        OS.note_providence(args["note"])
        return {"logged": True}
    return {"error": f"Unknown tool: {name}"}


# In-memory chat sessions: session_id -> message history (SDK content blocks).
# Render instances are ephemeral; durable facts belong in the Vault.
_SESSIONS: dict[str, list[dict]] = {}
_SESSIONS_LOCK = threading.Lock()
_MAX_TURNS_KEPT = 40
_MAX_TOOL_ITERATIONS = 10

CONRAD_MODEL = "claude-opus-4-8"


@app.post("/api/chat")
def chat(req: ChatRequest) -> dict:
    if not OS.api_key_configured():
        raise HTTPException(
            status_code=503,
            detail="ANTHROPIC_API_KEY is not configured. On Render: dashboard → "
            "your service → Environment → add ANTHROPIC_API_KEY.",
        )

    session_id = req.session_id or str(uuid.uuid4())
    with _SESSIONS_LOCK:
        messages = list(_SESSIONS.get(session_id, []))

    messages.append({"role": "user", "content": req.message})
    tool_trace: list[dict] = []

    try:
        for _ in range(_MAX_TOOL_ITERATIONS):
            response = OS.client.messages.create(
                model=CONRAD_MODEL,
                max_tokens=16000,
                thinking={"type": "adaptive"},
                system=CONRAD_SYSTEM,
                tools=CONRAD_TOOLS,
                messages=messages,
            )
            messages.append({"role": "assistant", "content": response.content})
            if response.stop_reason != "tool_use":
                break
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = _run_tool(block.name, dict(block.input))
                    tool_trace.append({"tool": block.name, "input": dict(block.input)})
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, default=str),
                        }
                    )
            messages.append({"role": "user", "content": tool_results})
    except anthropic.AuthenticationError:
        raise HTTPException(status_code=503, detail="Invalid ANTHROPIC_API_KEY.")
    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=f"Claude API error: {e}")

    reply = "".join(
        block.text
        for block in response.content
        if getattr(block, "type", None) == "text"
    )

    with _SESSIONS_LOCK:
        _SESSIONS[session_id] = messages[-_MAX_TURNS_KEPT:]

    return {"session_id": session_id, "reply": reply, "tools_used": tool_trace}


# ---------------------------------------------------------------------------
# Web UI
# ---------------------------------------------------------------------------

INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BCA OS — CONRAD/EXPO</title>
<style>
  :root {
    --bg: #101418; --panel: #1a2129; --line: #2a3441;
    --text: #e6edf3; --dim: #8b98a5; --accent: #e8833a; --ok: #4cc38a; --bad: #e5534b;
  }
  * { box-sizing: border-box; margin: 0; }
  body { background: var(--bg); color: var(--text);
         font: 15px/1.5 Georgia, 'Times New Roman', serif;
         height: 100vh; display: flex; flex-direction: column; }
  header { padding: 14px 20px; border-bottom: 1px solid var(--line);
           display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap; }
  header h1 { font-size: 18px; font-weight: 600; letter-spacing: .04em; }
  header h1 em { color: var(--accent); font-style: normal; }
  header .sub { color: var(--dim); font-size: 13px; }
  #keywarn { color: var(--bad); font-size: 13px; display: none; }
  main { flex: 1; display: flex; min-height: 0; }
  #chatcol { flex: 1; display: flex; flex-direction: column; min-width: 0; }
  #log { flex: 1; overflow-y: auto; padding: 20px; }
  .msg { max-width: 760px; margin: 0 auto 16px; }
  .msg .who { font-size: 12px; letter-spacing: .08em; text-transform: uppercase;
              color: var(--dim); margin-bottom: 4px; }
  .msg.user .who { color: var(--accent); }
  .msg .body { white-space: pre-wrap; }
  .msg .tools { margin-top: 6px; font-size: 12px; color: var(--dim);
                font-family: ui-monospace, monospace; }
  #composer { border-top: 1px solid var(--line); padding: 14px 20px; }
  #composer form { max-width: 760px; margin: 0 auto; display: flex; gap: 10px; }
  #composer input { flex: 1; background: var(--panel); color: var(--text);
                    border: 1px solid var(--line); border-radius: 8px;
                    padding: 10px 14px; font: inherit; }
  #composer input:focus { outline: none; border-color: var(--accent); }
  #composer button { background: var(--accent); color: #14100b; border: none;
                     border-radius: 8px; padding: 10px 18px; font: inherit;
                     font-weight: 700; cursor: pointer; }
  #composer button:disabled { opacity: .5; cursor: wait; }
  aside { width: 300px; border-left: 1px solid var(--line); padding: 18px;
          overflow-y: auto; background: var(--panel); }
  aside h2 { font-size: 12px; letter-spacing: .1em; text-transform: uppercase;
             color: var(--dim); margin-bottom: 12px; }
  .app { border: 1px solid var(--line); border-radius: 8px; padding: 10px 12px;
         margin-bottom: 10px; background: var(--bg); }
  .app .name { font-weight: 700; }
  .app .status { float: right; font-size: 11px; padding: 1px 8px;
                 border-radius: 10px; border: 1px solid var(--line); color: var(--dim); }
  .app .status.beta { color: var(--ok); border-color: var(--ok); }
  .app .desc { font-size: 13px; color: var(--dim); margin-top: 4px; }
  .app .gates { margin-top: 6px; font-size: 12px; }
  .gate { display: inline-block; margin: 2px 4px 0 0; padding: 1px 7px;
          border-radius: 9px; border: 1px solid var(--bad); color: var(--bad); }
  .gate.met { border-color: var(--ok); color: var(--ok); }
  @media (max-width: 860px) { aside { display: none; } }
</style>
</head>
<body>
<header>
  <h1>BCA OS · <em>CONRAD/EXPO</em></h1>
  <span class="sub">Blue Collar Apps Co. — the pass stays clean</span>
  <span id="keywarn">ANTHROPIC_API_KEY not configured — chat is offline</span>
</header>
<main>
  <div id="chatcol">
    <div id="log"></div>
    <div id="composer">
      <form id="f">
        <input id="inp" autocomplete="off"
               placeholder="Chef: what are we cooking today?" />
        <button id="send" type="submit">Fire</button>
      </form>
    </div>
  </div>
  <aside>
    <h2>BCA App Catalog</h2>
    <div id="apps"><span style="color:var(--dim)">Loading…</span></div>
  </aside>
</main>
<script>
const log = document.getElementById('log');
const form = document.getElementById('f');
const inp = document.getElementById('inp');
const send = document.getElementById('send');
let sessionId = null;

function addMsg(who, cls, text, tools) {
  const div = document.createElement('div');
  div.className = 'msg ' + cls;
  const whoEl = document.createElement('div');
  whoEl.className = 'who'; whoEl.textContent = who;
  const body = document.createElement('div');
  body.className = 'body'; body.textContent = text;
  div.append(whoEl, body);
  if (tools && tools.length) {
    const t = document.createElement('div');
    t.className = 'tools';
    t.textContent = 'tools: ' + tools.map(x => x.tool).join(' → ');
    div.append(t);
  }
  log.append(div);
  log.scrollTop = log.scrollHeight;
  return body;
}

async function loadStatus() {
  try {
    const r = await fetch('/api/status');
    const s = await r.json();
    if (!s.api_key_configured) document.getElementById('keywarn').style.display = 'inline';
    const el = document.getElementById('apps');
    el.innerHTML = '';
    for (const [id, a] of Object.entries(s.apps)) {
      const d = document.createElement('div');
      d.className = 'app';
      d.innerHTML = '<span class="status ' + a.status.replace(/[^a-z-]/g,'') + '">'
        + a.status + '</span><div class="name"></div><div class="desc"></div>'
        + '<div class="gates"></div>';
      d.querySelector('.name').textContent = a.name;
      d.querySelector('.desc').textContent = a.description;
      const gwrap = d.querySelector('.gates');
      fetch('/api/policy/' + id).then(r => r.json()).then(p => {
        for (const g of p.gates_required) {
          const s2 = document.createElement('span');
          s2.className = 'gate' + (p.gates_met.includes(g) ? ' met' : '');
          s2.textContent = g;
          gwrap.append(s2);
        }
      }).catch(() => {});
      el.append(d);
    }
  } catch (e) {
    document.getElementById('apps').textContent = 'status unavailable';
  }
}

form.addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const text = inp.value.trim();
  if (!text) return;
  inp.value = '';
  addMsg('Chef', 'user', text);
  send.disabled = true;
  const pending = addMsg('Conrad', 'bot', '…');
  try {
    const r = await fetch('/api/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: text, session_id: sessionId}),
    });
    const data = await r.json();
    if (!r.ok) {
      pending.textContent = '⚠ ' + (data.detail || 'request failed');
    } else {
      sessionId = data.session_id;
      pending.textContent = data.reply || '(no text reply)';
      if (data.tools_used && data.tools_used.length) {
        const t = document.createElement('div');
        t.className = 'tools';
        t.textContent = 'tools: ' + data.tools_used.map(x => x.tool).join(' → ');
        pending.parentElement.append(t);
      }
      loadStatus();
    }
  } catch (e) {
    pending.textContent = '⚠ network error: ' + e;
  } finally {
    send.disabled = false;
    inp.focus();
  }
});

loadStatus();
inp.focus();
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return INDEX_HTML
