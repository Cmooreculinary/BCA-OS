# Conrad Blueprint Explorer

Interactive, read-only V1 architecture map for Blue Collar Apps OS.

## Product boundary

- Blue Collar Apps OS is the parent founder operating system.
- Conrad / EXPO is the company brain, expediter, router, guide, and source-of-truth coordinator.
- Blueprint Explorer is the governed architecture map Conrad reads and updates.
- Conrad Control Center is a later operational cockpit built on the explorer.

The prototype does not invent pricing, launch claims, roadmap commitments, product boundaries, or private architecture. Unknown information remains marked unknown or unverified.

## Current capabilities

- Same-level systems aligned in level columns
- Expand and collapse architecture branches
- Full-text search across nodes and metadata
- Status filters
- Detailed node panel
- Parent, child, dependency, and downstream relationship views
- JSON architecture export
- Responsive desktop and mobile interface
- Trench Design visual system

## Run locally

```bash
npm install
npm run dev
```

Open the local URL printed by Vite.

## Production build

```bash
npm run build
npm run preview
```

## Deployment

The explorer deploys beside BCA-OS from the same repository and root Render Blueprint. It remains a separate static service so the React/Vite frontend does not alter the Python runtime of the existing BCA-OS service.

- **Repository:** `Cmooreculinary/BCA-OS`
- **Target branch:** `feature/conrad-blueprint-explorer`
- **Application directory:** `blueprint-explorer`
- **Render service:** `bca-os-blueprint-explorer`
- **Render runtime:** static
- **Render root directory:** `blueprint-explorer`
- **Build command:** `npm ci && npm run build`
- **Publish directory:** `dist`
- **SPA route:** all paths rewrite to `/index.html`
- **Environment variables:** none required for V1
- **Expected Render URL:** `https://bca-os-blueprint-explorer.onrender.com` after the Blueprint creates the service; the final URL must be confirmed in Render.

Vercel remains technically compatible, but Render is the selected deployment target for this branch.

## Architecture data

All V1 architecture content is stored in `src/data.js`. The structure is intentionally separated from the interface so it can later migrate to a governed API and MongoDB without rebuilding the visual layer.

## Governance

- Architecture-level decisions route through Conrad / EXPO.
- CapKids remains COPPA-gated.
- AllergenShield remains liability-gated and must never guarantee allergen safety.
- Secrets belong in environment variables or an approved secret manager, never source control.
- Every future automated update requires a source, timestamp, and confidence state.
