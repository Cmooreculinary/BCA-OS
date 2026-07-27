# Conrad Memory Log
<!-- Conrad appends durable lessons here with today's date. Read at session start. -->

## 2026-06-18
- Learning loop verified: this entry was appended during Packet B validation. Format: `## YYYY-MM-DD` header, bullet per lesson.
- Fable 5 access suspended under ~June 12 export-control directive — use Opus 4.8 as Teacher until restored.
- GLM-5.2 is the free heavy-coding engine (hosted, not self-hosted) — never feed it Stripe keys or customer data.

## 2026-06-24
- BCA OS is the founder-controlled parent system; Conrad is the central brain and universal intake router beneath it. Claude and other models are tools Conrad may use, not parent brains.

## 2026-07-27
- Cherry-picked 11 skills from Garry Tan's gstack (MIT, upstream v1.60.1.0) into `.claude/skills/`: office-hours, plan-ceo-review, plan-eng-review, spec, review, ship, investigate, retro, learn, cso, careful. Provenance and upgrade recipe in `.claude/skills/README.md`.
- These are standing staff, not on-request tools. The auto-engage table in CLAUDE.md is law: I invoke the matching skill myself when its trigger fires, announce which and why, and back off only if the founder says so.
- Left out on purpose: browse/qa/design-* (31MB browser runtime + Bun binaries + real Chrome), all ios-*, and benchmark/canary/setup-deploy/supabase/codex/gbrain. Revisit browse only if a real browser-QA need appears.
- gstack's `bin/` helpers (config, telemetry, decision log, brain sync) are NOT vendored — needs Bun. Every call site is guarded, so skills degrade to defaults. Installing the full bundle at `~/.claude/skills/gstack` would light them up with no edits.
