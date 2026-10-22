---
name: sonnet-build
description: Build something with the strong-plan, cheap-build split — a top model writes a short spec, a cheaper model builds, the top model checks before Chef sees it.
---

# Plan strong, build cheap

**Goal:** excellent work at the lowest cost. Follows `routing.md`.

## Rules
- Top model (Opus/Fable or equivalent): plan, architecture, final check. Never routine wiring.
- Builder model (Sonnet/Haiku or equivalent): the building.
- Chef sees only checked work.

## Steps
1. **Spec** (top model): write `SPEC.md` — goal, must-haves, don't-touch list, how to test, done-when. Keep it to one screen.
2. **Build** (builder): read SPEC.md, build, self-test (run it; for UI, take screenshots and check for console errors).
3. **Check** (top model): compare to SPEC.md, look at screenshots, run tests. Send fixes back to the same builder instead of starting over.
4. **Deliver:** one line on what it is + the file or link. Ship with `bca-ship`.
