# Blue Collar Apps Co. — Marketing Site + Tool Finder

A single-page React + TypeScript + Tailwind marketing site for **Blue Collar Apps Co. (BCA)**,
a hospitality & foodservice software ecosystem. Includes a Gemini-powered **Tool Finder** that
recommends BCA products based on a description of the user's operation — grounded strictly in the
product catalog.

> Design language: **Trench Design** — dark, high-contrast, industrial-premium. Fire Orange as the
> cutting edge. Bebas Neue / DM Sans / IBM Plex Mono.

## Stack

- React 19 + TypeScript
- Vite 6
- Tailwind CSS 3
- `@google/genai` (Gemini `gemini-2.5-flash`) for the Tool Finder
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
npm install
cp .env.local.example .env.local   # add your Gemini key
npm run dev
```

Then open the printed local URL.

### API key

The Tool Finder needs a Gemini API key.

- **Google AI Studio** injects it automatically — nothing to configure.
- **Locally**, set `GEMINI_API_KEY` in `.env.local`. `vite.config.ts` maps it to
  `process.env.API_KEY`, which `src/services/geminiService.ts` reads.

If the key is missing, the rest of the site works fully; only the Tool Finder shows a clear,
graceful message.

## Build

```bash
npm run build      # type-checks (tsc --noEmit) then builds to dist/
npm run preview    # serve the production build
```

## Deploy

The app is a static build (`dist/`) plus one Gemini call, so any static host works.
The Tool Finder needs `GEMINI_API_KEY` available **at build time** (Vite inlines it) —
read the Security section below before deploying a public key.

| Host | Steps | Notes |
|------|-------|-------|
| **Google AI Studio** | Open the project in AI Studio. | Key injected automatically; Tool Finder works, nothing to configure. |
| **Vercel** | Import the repo. Set `GEMINI_API_KEY` env var. Deploy. | Vite is auto-detected. Real public URL. |
| **Netlify** | Import the repo. Build `npm run build`, publish `dist`. Set `GEMINI_API_KEY`. | Same shape as Vercel. |
| **GitHub Pages** | Settings → Pages → Source: **GitHub Actions**. Add repo secret `GEMINI_API_KEY`. Run the **Deploy to GitHub Pages** workflow (Actions tab → Run workflow). | Uses `.github/workflows/deploy-pages.yml`. Sets `VITE_BASE=/<repo>/` so assets resolve on the project site. |

The Pages workflow is **manual-trigger only** (`workflow_dispatch`) — it never runs on
a normal push. `vite.config.ts` reads `VITE_BASE` (default `/`) so the same build works
at a domain root (Vercel/Netlify/AI Studio) or under `/<repo>/` (Pages).

## Structure

```
src/
  components/        UI sections (Hero, TrenchEdge, Catalog, ToolFinder, Mission, …)
  data/              catalog.ts (single source of truth) + nav.ts
  services/          geminiService.ts — grounded Tool Finder
  hooks/             useActiveSection.ts (sticky-nav highlighting)
  types.ts           shared domain types
```

### Source of truth

`src/data/catalog.ts` drives **both** the Product Catalog grid and the Tool Finder's grounding
context. Edit the catalog there and both stay in sync — the AI can only recommend products that
exist in that array.

## Security — API key handling

Vite's `define` inlines `GEMINI_API_KEY` into the client bundle at build time, so
**any key present in a deployed build is publicly extractable** from the browser
JavaScript. This is inherent to the AI Studio single-page model, where the key is
injected client-side.

For local dev and AI Studio previews this is fine. Before a **public production
deploy**, do one of:

- **Recommended:** proxy the Tool Finder request through a server-side function
  (edge/serverless) so the key stays server-side. `recommendTools()` in
  `src/services/geminiService.ts` is the single call site to repoint at that
  endpoint.
- **At minimum:** use a **restricted, quota-capped** AI Studio key that is
  **rotated regularly**, so a leaked key has limited blast radius.

## Notes / next steps

- **Get Notified** is a front-end stub: it stores emails in local state and shows a success
  state. See the `TODO(backend)` in `src/components/GetNotified.tsx` for where to wire a real
  waitlist (API endpoint or Stripe).
- The Python files (`bca_os.py`, `conrad_expo.py`) are the separate BCA OS backend and are not
  part of this web app.
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
