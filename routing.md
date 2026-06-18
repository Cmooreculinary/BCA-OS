# Conrad — Teacher Routing Config
# Law: use the least powerful model that still delivers excellence.
# Escalate only when the rung below fails or the task class demands it.

## Routing Table

| Task Class | Examples | Model | Notes |
|---|---|---|---|
| Mechanical / high-volume | Format conversion, simple transforms, template fills, boolean checks | **Haiku 4.5** | Default first rung. Free or cheapest tier. |
| Execution work | Code edits, repo-wide reads, structured generation, API wiring, config drafts | **Sonnet 4.6** | Mid-tier. Workhorse for most Conrad loops. |
| Strategy & architecture review | Design decisions, packet acceptance, identity/judgment calls, Teacher checkpoints | **Opus 4.8** | Reserved. Not for wiring or iteration. |
| Heavy coding (no secrets) | Complex multi-file builds, long-horizon scaffolding | **GLM-5.2** | Free hosted (OpenRouter). Never feed secrets. |
| Image gen / multimodal / long-context reads | Asset creation, Galaxy population, PDF digestion | **Gemini (free)** | Free tier. No live keys in prompts. |
| Fast draft / rubber-duck | Quick outlines, second opinions, reformats | **ChatGPT (free)** | Free tier. Throwaway; don't build on output. |

## Escalation Rules

1. If Haiku produces an incorrect or incomplete result after one retry → escalate to Sonnet.
2. If Sonnet produces an architectural ambiguity or crosses a design decision → escalate to Opus.
3. Opus is **never** used for wiring, iteration, or routine generation — Teacher only.
4. Fable 5 is suspended (export-control, ~June 12 2026). Do not route to Fable 5 until access restored.

## Cost Law (broke-mode)

Haiku 4.5 → Sonnet 4.6 → (Opus 4.8 at checkpoints only). Free engines first.
Three Teacher checkpoints per build cycle: bless CLAUDE.md, accept MCP bridge, accept closed loop.

## Per-Packet Assignments (EXPO v0.1)

| Packet | Task | Model |
|---|---|---|
| A — Constitution | Review + commit CLAUDE.md | Opus 4.8 (bless) |
| B — Learning loop | Create memory.md, verify append | Haiku 4.5 |
| C — MCP bridge | Build FastAPI + MCP server | Sonnet 4.6 / GLM-5.2 |
| D — n8n loop | Build workflow JSON | GLM-5.2 |
| E — Routing config | This document | Sonnet 4.6 |
