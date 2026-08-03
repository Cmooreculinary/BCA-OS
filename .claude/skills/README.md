# Vendored skills — gstack subset

Cherry-picked from [garrytan/gstack](https://github.com/garrytan/gstack) (MIT, see
`GSTACK-LICENSE`) at upstream `v1.60.1.0`, commit `a3259400a366593e0c909dd9ac3e59752efd2488`.

## What's here

| Skill | Role it plays for BCA OS |
|---|---|
| `office-hours` | YC-style founder session — pressure-tests the product, not the code |
| `plan-ceo-review` | CEO/founder review of a feature plan before anything gets built |
| `plan-eng-review` | Eng-manager review — locks architecture before implementation |
| `spec` | Turns vague intent into an executable spec in five phases |
| `review` | Pre-landing diff/PR review with specialist passes |
| `ship` | Merge base, run tests, bump version, changelog, commit, push, PR |
| `investigate` | Systematic root-cause debugging instead of guess-and-patch |
| `retro` | Weekly retrospective over what actually shipped |
| `learn` | Captures durable project learnings — feeds Conrad's `memory.md` loop |
| `cso` | Chief Security Officer mode — OWASP + STRIDE audit |
| `careful` | Slow-down guard for high-blast-radius changes |

## What was deliberately left out

- **`browse` / `connect-chrome` / `qa` / `design-*`** — 31 MB of browser runtime plus
  compiled Bun binaries and a real Chrome. Not worth it here.
- **iOS skills** (`ios-*`) — no iOS surface in BCA OS.
- **`benchmark`, `canary`, `setup-deploy`, `supabase`, `codex`, `*-gbrain`** — infra and
  vendor paths BCA OS doesn't use.

## Runtime note

Upstream skills open with a preamble that shells out to `~/.claude/skills/gstack/bin/*`
(config, telemetry, decision log, brain sync). Those helpers are **not** vendored — the
full bundle needs Bun and pulls in the parts above. Every call site is guarded
(`2>/dev/null || <default>` or `[ -x ... ]`), so the skills fall back to defaults and the
methodology — which is plain Markdown — runs unchanged. Telemetry stays off because the
binary is absent.

If the full bundle is ever installed at `~/.claude/skills/gstack`, those helpers light up
automatically with no edits here.

## Upgrading

SKILL.md files are vendored verbatim, so upgrading is a re-copy:

```bash
git clone --depth 1 https://github.com/garrytan/gstack.git /tmp/gstack
for s in office-hours plan-ceo-review plan-eng-review spec review ship \
         investigate retro learn cso careful; do
  rm -rf .claude/skills/$s && cp -R /tmp/gstack/$s .claude/skills/$s
done
```

Then update the version and commit pinned at the top of this file.
