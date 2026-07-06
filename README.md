# BCA OS

The operating system layer for **Blue Collar Apps Co.** — routing, memory
(Vault), launch-gate policy enforcement, Teacher Pattern dispatch, and the
BCA app catalog. **CONRAD/EXPO**, the founder-facing host brain, runs on top
of it.

## What's here

| File | Purpose |
|---|---|
| `bca_os.py` | The OS layer: app catalog, domain routing, launch gates, Vault, Claude dispatch |
| `server.py` | FastAPI web service: JSON API + CONRAD/EXPO chat with a built-in web UI |
| `conrad_expo.py` | Interactive terminal host loop (Claude Agent SDK; local use) |
| `render.yaml` | Render Blueprint for one-click deployment |

## Run locally

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
uvicorn server:app --reload
```

Open http://localhost:8000 for the CONRAD/EXPO chat UI. Interactive API docs
are at http://localhost:8000/docs.

The server boots without an API key (status, policy, and vault endpoints all
work); chat and expedite return `503` until the key is set.

## Deploy on Render

1. Push this repository to GitHub.
2. In the [Render dashboard](https://dashboard.render.com), click **New → Blueprint** and select this repo. Render reads `render.yaml`.
3. When prompted, set the `ANTHROPIC_API_KEY` environment variable.
4. Click **Apply**. The service builds with `pip install -r requirements.txt` and starts `uvicorn server:app`. Health checks hit `/health`.

The Vault defaults to `/tmp/bca_vault.json` on Render, which resets on each
deploy. To persist memory across deploys, attach a persistent disk and point
`BCA_VAULT_PATH` at it (see the comment in `render.yaml`).

## API

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check; reports whether the API key is configured |
| `/api/status` | GET | OS status + live BCA app catalog |
| `/api/policy/{brain}` | GET | Launch-gate check for one brain (`capkids`, `roundtable`, `allergenshield`, `trenchsms`) |
| `/api/policy/{brain}/gates` | POST | Mark gates as met: `{"gates_met": ["COPPA", ...]}` |
| `/api/expedite` | POST | Route + execute an intent: `{"intent": "...", "task_class": "execution_std", "sensitivity": "internal"}` |
| `/api/chat` | POST | Talk to CONRAD/EXPO: `{"message": "...", "session_id": null}` |
| `/api/vault/{key}` | GET | Read a Vault entry |
| `/api/vault` | POST | Write a Vault entry: `{"key": "...", "value": ...}` |

Launch gates are enforced on every route: an intent that lands on a brain
with unmet gates is **blocked**, not executed. CapKids requires COPPA,
AllergenShield requires liability insurance + dietitian review, TrenchSMS
requires A2P 10DLC + TCPA compliance.

## Terminal host (optional, local)

`conrad_expo.py` runs the same brain in the terminal via the Claude Agent
SDK, which additionally requires the Claude Code CLI to be installed:

```bash
python conrad_expo.py
```
