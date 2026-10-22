---
name: sonnet-build
description: Build something with the strong-plan, cheap-build split — a top model writes a short spec, a cheaper model builds, the top model checks before Chef sees it.
---

# Plan strong, build cheap

**Goal:** excellent work at the lowest cost.

## Rules
- **Pick every model from `routing.md`.** It is the only model list; it says which rung plans, which builds, and which models are paused. Don't name models anywhere else.
- Top rung: plan, architecture, final check. Never routine wiring.
- Builder rung: the building. Never give a builder secrets.
- Chef sees only checked work.

## Steps
1. **Spec** (top model): write `SPEC.md` — goal, must-haves, don't-touch list, how to test, done-when. Keep it to one screen.
2. **Build** (builder): read SPEC.md, build, self-test (run it; for UI, take screenshots and check for console errors).
3. **Check** (top model): compare to SPEC.md, look at screenshots, run tests. Send fixes back to the same builder instead of starting over.
4. **Deliver:** one line on what it is + the file or link. Ship with `bca-ship`.
