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

## Notes / next steps

- **Get Notified** is a front-end stub: it stores emails in local state and shows a success
  state. See the `TODO(backend)` in `src/components/GetNotified.tsx` for where to wire a real
  waitlist (API endpoint or Stripe).
- The Python files (`bca_os.py`, `conrad_expo.py`) are the separate BCA OS backend and are not
  part of this web app.
