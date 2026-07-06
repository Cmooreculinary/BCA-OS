# BCA Universal User Shell — Phased Implementation Plan
**Module:** BCA Universal User Shell
**Status:** Planning — no code until Founder approves Spec (Phase 0 gate)
**Last updated:** 2026-06-18
**Prerequisite:** BCA_Universal_User_Shell_Spec.md approved by Founder + Teacher checkpoint

---

## Phase 0 — Spec Acceptance (Gate: Founder + Teacher)
**Duration:** Current session
**Owner:** Founder approval required before anything proceeds

- [ ] Founder reviews `BCA_Universal_User_Shell_Spec.md`
- [ ] Founder approves or redlines named concepts, user flow, API contracts
- [ ] Founder approves or adjusts pricing tier structure (amounts TBD)
- [ ] Founder approves Conrad greeting copy and image usage on Landing Shell
- [ ] Teacher checkpoint (Opus 4.8): architecture review of spec
  - Confirm agent-at-edges pattern is preserved
  - Confirm no hot-path agent calls
  - Confirm VaultSpace/Galaxy invariants intact
  - Confirm Stripe guardrails in place
- [ ] Founder decides: extend MCP bridge (port 8001) OR new shell_api service (port 8002)
  - Recommendation: new shell_api service (see spec §5)

**Exit criterion:** Founder signs off. Teacher blesses. No open redlines.

---

## Phase 1 — Data Layer
**Duration:** ~2 days
**Owner:** Claude Code
**Depends on:** Phase 0 complete

### Deliverables
- [ ] SQLite storage initialization script (idempotent, safe to re-run)
  - `shell_sessions`, `user_permissions`, `token_wallet`, `token_transactions`,
    `smartvault_activity`, `support_tickets`, `tour_configs`, `launch_incentives`,
    `user_incentive_claims`
- [ ] Index definitions for each collection (see spec §6)
- [ ] Seed script: default `tour_configs` for Foodtruck Apollo (placeholder steps)
- [ ] Seed script: initial `launch_incentives` records (onboarding grant + 1 founder
  credit code — amounts to be filled in after Founder approval)
- [ ] `BCA_VaultSpace_NotebookLM_Architecture.md` — append `smartvault_activity`
  collection to §2 schema section

### Guardrails
- No application code yet — data layer only
- Seed scripts must be safe to re-run (upsert, not insert)
- No real token amounts until Founder approves §2.11 values

---

## Phase 2 — Shell API Skeleton
**Duration:** ~3 days
**Owner:** Claude Code (routes + Pydantic models) / Codex (model generation assist)
**Depends on:** Phase 1 complete

### Deliverables
- [ ] New FastAPI service: `shell_api/` directory
  - `shell_api/main.py` — app factory, health endpoint
  - `shell_api/models.py` — Pydantic request/response models (all 14 endpoints)
  - `shell_api/routes/session.py` — `POST /shell/session/start`, `POST /shell/session/end`
  - `shell_api/routes/permissions.py` — `POST /shell/permissions/grant`
  - `shell_api/routes/wallet.py` — `GET /wallet/balance`, `GET /wallet/history`,
    `POST /wallet/grant`, `POST /wallet/debit`
  - `shell_api/routes/tour.py` — `GET /shell/tour/{app_id}`, `POST /shell/tour/complete`
  - `shell_api/routes/incentives.py` — `POST /launch/claim-incentive`,
    `POST /launch/onboarding-grant` (internal)
  - `shell_api/routes/pricing.py` — `GET /shell/pricing`
  - `shell_api/routes/stripe_webhook.py` — `POST /stripe/webhook`
  - `shell_api/db.py` — SQLite connection (reuse sqlite storage pattern from mcp_bridge)
  - `shell_api/requirements.txt`
- [ ] VaultSpace activity logger utility (`shell_api/activity.py`)
  - `async def log_activity(event_type, session_id, user_id, app_context, payload)`
  - Always async, never awaited on the hot path (fire-and-forget with error catch)
- [ ] n8n workflow JSON: `n8n/support_escalation.workflow.json`
  - Trigger: webhook from `POST /support/escalate`
  - Action: send notification (email/Slack TBD) to Founder/support queue
- [ ] Basic integration tests for session and wallet routes

### Guardrails
- Hot-path endpoints (session/start, permissions/grant, wallet/balance) must return
  without any agent calls or Galaxy queries
- `log_activity` is fire-and-forget — never block a response waiting for it
- Stripe webhook handler must validate Stripe-Signature before touching the DB

---

## Phase 3 — Conrad Integration
**Duration:** ~3 days
**Owner:** Claude Code
**Depends on:** Phase 2 complete

### Deliverables
- [ ] `shell_api/routes/support.py` — `POST /support/message`, `POST /support/escalate`,
  `GET /support/history/{session_id}`
- [ ] `POST /support/message` calls MCP bridge (`POST /galaxy/query`) for source-grounded
  FAQ answers; result written to `smartvault_activity` async
- [ ] `POST /support/escalate` creates support ticket + calls n8n escalation workflow
- [ ] New Galaxy created (offline population): `bca-shell-v1`
  - Sources: this spec, BCA_VaultSpace_NotebookLM_Architecture.md, CLAUDE.md
  - Teacher checkpoint (Opus 4.8) on citation quality before marking active
- [ ] `claude_mcp_config.json` updated: new tool stub for shell support desk if needed
- [ ] Conrad greeting text finalized and stored in DB (Founder-approved copy)

### Guardrails
- Conrad is called only for `POST /support/message` — no other shell endpoint
  calls Conrad
- Galaxy population is offline and manual — never automated at runtime
- Support desk response is async — client must handle pending state gracefully

---

## Phase 4 — Tour System
**Duration:** ~2 days
**Owner:** Claude Code (backend) / Gemini (tour content generation assist)
**Depends on:** Phase 2 complete (can run parallel to Phase 3)

### Deliverables
- [ ] `GET /shell/tour/{app_id}` fully wired to `tour_configs` collection
- [ ] `POST /shell/tour/complete` wired: logs to `smartvault_activity`, calls
  `wallet/grant` if token reward configured (amount TBD — Founder approval needed)
- [ ] Tour configs seeded for Foodtruck Apollo (minimum 5 steps)
  - Step content: Gemini assists with narration copy from app documentation
- [ ] Graceful degradation: if target_selector matches no element, step is skipped
  silently (no error thrown, no tour crash)
- [ ] Tour config versioning: version field incremented on updates, shell client
  caches by version

### Guardrails
- Tour step narration is static copy in SQLite — Conrad is NOT called per step
  (would be too slow). Conrad is available from HUD separately.
- Token reward amount requires Founder approval before wiring

---

## Phase 5 — Token Economy and Pricing
**Duration:** ~3 days
**Owner:** Claude Code
**Depends on:** Phase 2 complete, Founder approval of pricing amounts
**Gate:** Founder must approve Standard/Pro amounts and token allowances before this
  phase begins. Stripe product/price IDs must be created in Stripe dashboard
  by Founder (Claude Code never touches live billing keys).

### Deliverables
- [ ] `POST /stripe/webhook` fully wired: handles `customer.subscription.created`,
  `customer.subscription.updated`, `customer.subscription.deleted`
  - Updates `token_wallet.tier` and `monthly_allowance` on subscription change
  - Logs to `smartvault_activity`
- [ ] `POST /wallet/grant` and `POST /wallet/debit` fully wired with SQLite
  transactions and idempotency key enforcement
- [ ] `POST /launch/claim-incentive` fully wired with atomic claim increment
  and `user_incentive_claims` idempotency ledger
- [ ] `POST /launch/onboarding-grant` internal endpoint wired (called by session/start
  on first verified login)
- [ ] `GET /shell/pricing` returns real tier data from config collection (Founder
  approves amounts before seeding)
- [ ] n8n workflow JSON: `n8n/onboarding_token_grant.workflow.json`
  - Trigger: first login event from `smartvault_activity`
  - Action: call `POST /launch/onboarding-grant` → log result
- [ ] Load test: wallet grant/debit under concurrent requests (race condition
  verification for SQLite transaction path)

### Guardrails
- No Stripe product/price IDs committed to code — pulled from env vars only
- Stripe-Signature validation is mandatory before any webhook processing
- Token amounts are Founder-approved config, not hardcoded

---

## Phase 6 — Launch Prep
**Duration:** ~2 days
**Owner:** Claude Code (scripts) / Founder (data approval)
**Depends on:** Phases 3, 4, 5 complete

### Deliverables
- [ ] Launch giveaway seed data loaded (Founder approves amounts first):
  - Automatic onboarding grant record
  - First batch of founder credit codes (count and amounts TBD)
  - Referral bonus incentive record
- [ ] n8n workflow JSON: `n8n/referral_bonus.workflow.json`
  - Trigger: new user sign-up with referral source in session
  - Action: grant tokens to referrer + referee
- [ ] SmartVault Galaxy population cycle: export `smartvault_activity` summary
  (PII stripped) + shell spec docs → `bca-shell-v1` Galaxy (offline, manual)
- [ ] `memory.md` append: document Shell module go-live lessons
- [ ] `BCA_VaultSpace_NotebookLM_Architecture.md` updated: add Shell API as new
  service in §4 (MCP Bridge section) and note `bca-shell-v1` Galaxy
- [ ] Smoke test checklist run end-to-end (see task board for test items)

### Guardrails
- No production deployment without Founder explicit approval
- No live Stripe keys in any script or commit
- All seed data is idempotent (upsert patterns)

---

## Phase 7 — Frontend (LOCKED — Founder Must Unlock)
**Status:** LOCKED. No frontend code is written until Founder explicitly approves.
**Owner:** TBD (frontend dev or design-approved implementation)
**Depends on:** All phases above complete, Founder explicit sign-off

When unlocked, the frontend component map in `BCA_Universal_User_Shell_Spec.md §4`
is the handoff document. API contracts in §5 are the interface contract.

---

## Phase Dependencies Summary

```
Phase 0 (Gate) ──┬──> Phase 1 ──> Phase 2 ──┬──> Phase 3
                 │                           ├──> Phase 4
                 │                           └──> Phase 5 (needs Founder $$$ approval)
                 │
                 └──> [Founder pricing approval] ──> Phase 5

Phases 3 + 4 + 5 all complete ──> Phase 6 ──> Phase 7 (LOCKED)
```

---

## Decision Log

| Decision | Options Considered | Choice | Rationale |
|---|---|---|---|
| Shell API service scope | Extend MCP bridge vs new service | New `shell_api/` service (pending Founder confirm) | Keeps MCP bridge focused on Conrad ↔ memory. Shell is a distinct concern. |
| Conrad in tour narration | Conrad per-step vs static copy | Static copy in SQLite | Per-step Conrad calls would make tour latency unacceptable. Conrad available from HUD separately. |
| Hot-path agent calls | Conrad in session/start | Rejected | Violates agents-at-edges rule. Session start must be < 200ms. |
| Frontend scope | Build now vs lock until approved | Locked (Phase 7) | Spec says "do not build frontend unless explicitly approved." |
