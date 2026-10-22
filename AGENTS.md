# BCA agents — start here

Every agent (Claude, ChatGPT/Astra, Codex, Cursor, Grok, VANGUARD) uses the same skills.

**Before a task, check `skills/` for a matching skill and follow it.**

| Skill | Use when |
|---|---|
| `skills/app-go-live` | Taking an app live (Clerk, DNS, GitHub settings, Fly, Cloudflare) |
| `skills/cloudflare-dns-records` | Adding DNS records to a Cloudflare domain |
| `skills/bca-ship` | Getting a change merged; fixing a failed deploy |
| `skills/agent-handoff` | Handing a task to another agent |
| `skills/sonnet-build` | Building anything: plan strong, build cheap, check |

Architecture decisions route through Conrad/EXPO (see CLAUDE.md). Always: Chef OKs before anything goes live. Never put passwords or keys in chat or repos. Give Chef short, numbered steps, one at a time.

Skills use the open SKILL.md format. Edit them here only, so every agent stays in sync.
