---
name: agent-handoff
description: Write a short, goal-based handoff prompt for another agent (Astra/ChatGPT, Claude, Codex, Cursor, Grok, VANGUARD) so it can take over a task cold.
---

# Agent handoff

**Goal:** the next agent can do the job without asking Chef anything already known.

## Rules
- Short. Goals and autonomy beat pages of text.
- Facts only, with dates. Mark anything unverified.
- No passwords, keys or tokens. Say where they live, never what they are.

## Format (paste-ready, one code block)
```
ROLE / PROJECT: who owns what
GOAL: one sentence
STATUS (date): what's done, what's broken, links
DO: 3–6 numbered steps
RULES: the 3–5 that matter (Chef OKs before live; keep approved look; ...)
DONE = how Chef will know it worked
REPORT BACK: what to send when finished
```

## Steps
1. Gather the real current state (repo, runs, settings), not old docs.
2. Fill the format. Cut anything the agent can find itself.
3. Hand it to Chef in a code block with one line on who to paste it to.
