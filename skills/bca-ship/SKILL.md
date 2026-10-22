---
name: bca-ship
description: Get a code change from branch to merged in a BCA repo — PR, checks, review, Chef merges — and fix a failed deploy run.
---

# Ship a change

**Goal:** the change is on `main`, all checks green, and nothing broke.

## Rules
- Never merge yourself. Chef taps merge.
- Never push to `main` directly. No secrets in code or PR text.
- One change per PR, with a short plain-language description.

## Steps
1. Branch from the latest `main`. Make the change. Run the repo's tests locally.
2. Open the PR: what changed, why, how it was tested.
3. Wait for checks and the automated review. Fix every real finding; say why if one is wrong.
4. Tell Chef: "PR #N is green and ready — tap merge." Check back later if he's away.
5. After merge, watch the deploy run.

## A deploy failed
1. Open the failed run → the failed job → the first failed step.
2. Read the error. Usually a missing setting, a wrong path, or a broken dependency.
3. Fix the cause (settings via `app-go-live` step 3; code via a new PR). Re-run and confirm green.
