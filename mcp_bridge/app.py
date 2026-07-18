from __future__ import annotations

"""Authenticated production entrypoint for the Conrad / BCA-OS founder service."""

import hashlib
import hmac
import os
from pathlib import Path

from fastapi import HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from . import server
from .system_prompt import build_conrad_system_prompt

app = server.app
server._CONRAD_SYSTEM = build_conrad_system_prompt()

COOKIE_NAME = "bca_os_founder_session"
COOKIE_MAX_AGE = 8 * 60 * 60
PUBLIC_PATHS = {"/health", "/unlock", "/favicon.ico"}


def _remove_route(path: str) -> None:
    app.router.routes[:] = [
        route for route in app.router.routes if getattr(route, "path", None) != path
    ]


_remove_route("/")
_remove_route("/health")


def _configured_token() -> str | None:
    token = os.environ.get("CONRAD_ACCESS_TOKEN", "").strip()
    return token or None


def _session_value(token: str) -> str:
    return hmac.new(token.encode("utf-8"), b"bca-os-founder-session", hashlib.sha256).hexdigest()


def _authorized(request: Request) -> bool:
    configured = _configured_token()
    if not configured:
        return False

    authorization = request.headers.get("Authorization", "")
    if authorization.startswith("Bearer "):
        supplied = authorization[7:].strip()
        if hmac.compare_digest(supplied, configured):
            return True

    cookie = request.cookies.get(COOKIE_NAME, "")
    return bool(cookie) and hmac.compare_digest(cookie, _session_value(configured))


def _secure_cookie() -> bool:
    return os.environ.get("RENDER", "").lower() in {"1", "true", "yes"}


@app.middleware("http")
async def founder_access_gate(request: Request, call_next):
    path = request.url.path
    if path != "/" and path not in PUBLIC_PATHS and not _authorized(request):
        if not _configured_token():
            return JSONResponse(
                status_code=503,
                content={"detail": "CONRAD_ACCESS_TOKEN is not configured"},
            )
        return JSONResponse(status_code=401, content={"detail": "Founder authorization required"})

    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:",
    )
    if path != "/health":
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
    return response


class UnlockRequest(BaseModel):
    token: str


_UNLOCK_UI = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Conrad / BCA OS — Founder Access</title>
<style>
:root{--obsidian:#0D0D0D;--surface:#141414;--surface2:#1E1E1E;--orange:#EC5B13;--text:#F3F3F3;--muted:#999}
*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;background:var(--obsidian);color:var(--text);font-family:Arial,sans-serif;padding:24px}.panel{width:min(440px,100%);background:var(--surface);border:1px solid #2A2A2A;padding:32px}.eyebrow{font-family:monospace;color:var(--orange);font-size:12px;letter-spacing:.12em;text-transform:uppercase;margin-bottom:12px}h1{font-size:34px;line-height:1;margin:0 0 12px;text-transform:uppercase;letter-spacing:.03em}.copy{color:var(--muted);line-height:1.5;margin-bottom:24px}label{display:block;font-size:12px;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px}input{width:100%;background:#090909;color:var(--text);border:1px solid #333;padding:13px 14px;font-family:monospace;font-size:14px;outline:none}input:focus{border-color:var(--orange);box-shadow:0 0 0 2px rgba(236,91,19,.25)}button{width:100%;margin-top:14px;background:var(--orange);color:#090909;border:0;padding:13px 16px;font-weight:800;text-transform:uppercase;letter-spacing:.08em;cursor:pointer}button:disabled{opacity:.55;cursor:wait}#message{min-height:20px;color:#ff8b62;font-family:monospace;font-size:12px;margin-top:12px}</style>
</head>
<body>
<main class="panel">
<div class="eyebrow">Blue Collar Apps OS</div>
<h1>Founder Access</h1>
<p class="copy">Conrad, intake routing, and VaultSpace are restricted founder systems.</p>
<form id="unlock-form">
<label for="token">Access token</label>
<input id="token" type="password" autocomplete="current-password" required autofocus/>
<button id="submit" type="submit">Open Conrad</button>
<div id="message" role="alert"></div>
</form>
</main>
<script>
const form=document.getElementById('unlock-form');
form.addEventListener('submit',async(event)=>{
 event.preventDefault();
 const button=document.getElementById('submit');
 const message=document.getElementById('message');
 button.disabled=true;message.textContent='Verifying…';
 try{
  const response=await fetch('/unlock',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:document.getElementById('token').value})});
  if(!response.ok){const data=await response.json().catch(()=>({}));throw new Error(data.detail||'Access denied');}
  window.location.replace('/');
 }catch(error){message.textContent=error.message;button.disabled=false;}
});
</script>
</body>
</html>"""


_SETUP_UI = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BCA OS Setup Required</title></head><body style="background:#0D0D0D;color:#eee;font-family:monospace;padding:40px"><h1 style="color:#EC5B13">BCA OS IS LOCKED</h1><p>Set the Render secret <strong>CONRAD_ACCESS_TOKEN</strong>, then redeploy.</p></body></html>"""


@app.get("/", response_class=HTMLResponse)
async def founder_ui(request: Request):
    if not _configured_token():
        return HTMLResponse(_SETUP_UI, status_code=503)
    if not _authorized(request):
        return HTMLResponse(_UNLOCK_UI, status_code=401)
    return HTMLResponse(server._UI)


@app.post("/unlock")
async def unlock(data: UnlockRequest, response: Response):
    configured = _configured_token()
    if not configured:
        raise HTTPException(status_code=503, detail="CONRAD_ACCESS_TOKEN is not configured")
    if not hmac.compare_digest(data.token.strip(), configured):
        raise HTTPException(status_code=401, detail="Access denied")
    response.set_cookie(
        key=COOKIE_NAME,
        value=_session_value(configured),
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        secure=_secure_cookie(),
        samesite="strict",
        path="/",
    )
    return {"unlocked": True}


@app.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key=COOKIE_NAME,
        path="/",
        secure=_secure_cookie(),
        httponly=True,
        samesite="strict",
    )
    return {"logged_out": True}


@app.get("/health")
async def health():
    sqlite_path = Path(os.environ.get("SQLITE_PATH", ""))
    return {
        "status": "ok",
        "service": "conrad-mcp-bridge",
        "founder_access_configured": bool(_configured_token()),
        "persistent_storage_configured": bool(sqlite_path) and not str(sqlite_path).startswith("/tmp/"),
    }
