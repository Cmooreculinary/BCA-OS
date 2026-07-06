# BCA Universal User Shell — Task Board
**Module:** BCA Universal User Shell
**Last updated:** 2026-06-18
**Status key:** `[ ]` = not started · `[~]` = in progress · `[x]` = done · `[!]` = blocked

All tasks are gated on Phase 0 (Founder + Teacher approval of spec) unless marked
`[GATE]`. No implementation task begins until the gate opens.

---

## Founder Approval

These items require explicit Founder decision. Nothing moves without them.

| # | Item | Status | Notes |
|---|---|---|---|
| F-01 | Approve `BCA_Universal_User_Shell_Spec.md` — full spec sign-off | `[ ]` | Gate for all implementation |
| F-02 | Approve Standard vs Pro pricing: monthly price and token allowances | `[ ]` | Blocks Phase 5 entirely |
| F-03 | Approve Conrad greeting copy for Landing Shell | `[ ]` | Needed before Phase 3 content is final |
| F-04 | Confirm Conrad founder-approved image is cleared for Landing Shell use | `[ ]` | Asset decision, no code impact |
| F-05 | Approve launch giveaway amounts: onboarding grant tokens, founder credit code value | `[ ]` | Blocks Phase 6 seed data |
| F-06 | Approve referral bonus amounts (referrer + referee) | `[ ]` | Blocks referral n8n workflow |
| F-07 | Decide: extend MCP bridge (port 8001) OR new shell_api service (port 8002) | `[ ]` | Spec recommends new service — Founder confirm |
| F-08 | Unlock Phase 7 (frontend) when ready | `[ ]` | Explicit unlock required; not automatic |
| F-09 | Create Stripe product/price IDs for Standard and Pro in Stripe dashboard | `[ ]` | Founder must do this — Claude Code never touches live billing keys |
| F-10 | Approve tour token reward amounts (earned on tour completion per app) | `[ ]` | Blocks Phase 4 token reward wiring |
| F-11 | Teacher checkpoint (Opus 4.8): bless spec architecture | `[ ]` | Run before Phase 1 begins |
| F-12 | Teacher checkpoint (Opus 4.8): bless Phase 2 API skeleton before Phase 3 | `[ ]` | Mid-build checkpoint |

---

## Claude Code

These tasks are executed in Claude Code sessions. Ordered by phase.

### Phase 1 — Data Layer
| # | Task | Phase | Status | Output |
|---|---|---|---|---|
| CC-01 | Write idempotent SQLite storage initialization script for all 9 collections | 1 | `[ ]` | `shell_api/scripts/create_collections.py` |
| CC-02 | Write index definitions for all collections (see spec §6) | 1 | `[ ]` | Inline in CC-01 script |
| CC-03 | Write seed script: placeholder `tour_configs` for Foodtruck Apollo | 1 | `[ ]` | `shell_api/scripts/seed_tour_configs.py` |
| CC-04 | Write seed script: initial `launch_incentives` records (amounts blank pending F-05) | 1 | `[ ]` | `shell_api/scripts/seed_incentives.py` |
| CC-05 | Append `smartvault_activity` collection schema to `BCA_VaultSpace_NotebookLM_Architecture.md` §2 | 1 | `[ ]` | Updated arch doc |

### Phase 2 — Shell API Skeleton
| # | Task | Phase | Status | Output |
|---|---|---|---|---|
| CC-06 | Create `shell_api/` service structure with FastAPI app factory and health endpoint | 2 | `[ ]` | `shell_api/main.py`, `shell_api/db.py`, `shell_api/requirements.txt` |
| CC-07 | Build `shell_api/routes/session.py` — `POST /shell/session/start` and `POST /shell/session/end` | 2 | `[ ]` | Route file |
| CC-08 | Build `shell_api/routes/permissions.py` — `POST /shell/permissions/grant` | 2 | `[ ]` | Route file |
| CC-09 | Build `shell_api/routes/wallet.py` — balance, history, grant, debit (with SQLite transactions) | 2 | `[ ]` | Route file |
| CC-10 | Build `shell_api/routes/incentives.py` — claim-incentive, onboarding-grant (internal) | 2 | `[ ]` | Route file |
| CC-11 | Build `shell_api/routes/pricing.py` — GET /shell/pricing | 2 | `[ ]` | Route file |
| CC-12 | Build `shell_api/routes/stripe_webhook.py` — webhook handler with signature validation | 2 | `[ ]` | Route file |
| CC-13 | Build `shell_api/activity.py` — fire-and-forget async activity logger | 2 | `[ ]` | Utility module |
| CC-14 | Write n8n workflow JSON: support escalation notification | 2 | `[ ]` | `n8n/support_escalation.workflow.json` |
| CC-15 | Write integration tests for session and wallet routes | 2 | `[ ]` | `shell_api/tests/` |

### Phase 3 — Conrad Integration
| # | Task | Phase | Status | Output |
|---|---|---|---|---|
| CC-16 | Build `shell_api/routes/support.py` — message, escalate, history | 3 | `[ ]` | Route file |
| CC-17 | Wire `POST /support/message` to MCP bridge `POST /galaxy/query` (async) | 3 | `[ ]` | Support route updated |
| CC-18 | Wire `POST /support/escalate` → support ticket creation + n8n trigger | 3 | `[ ]` | Support route updated |
| CC-19 | Populate `bca-shell-v1` Galaxy (offline): upload spec + arch doc + CLAUDE.md | 3 | `[ ]` | Galaxy populated |
| CC-20 | Teacher checkpoint (Opus 4.8) on `bca-shell-v1` citation quality | 3 | `[ ]` | Galaxy marked active |

### Phase 4 — Tour System
| # | Task | Phase | Status | Output |
|---|---|---|---|---|
| CC-21 | Build `shell_api/routes/tour.py` — GET /shell/tour/{app_id}, POST /shell/tour/complete | 4 | `[ ]` | Route file |
| CC-22 | Wire tour/complete → `smartvault_activity` log + `wallet/grant` if reward configured (pending F-10) | 4 | `[ ]` | Tour route updated |
| CC-23 | Implement graceful step-skip on missing target_selector (no crash) | 4 | `[ ]` | Tour route updated |

### Phase 5 — Token Economy
| # | Task | Phase | Status | Blocked by |
|---|---|---|---|---|
| CC-24 | Fully wire `POST /stripe/webhook` for subscription events → tier update | 5 | `[!]` | F-09 (Stripe IDs) |
| CC-25 | Fully wire `POST /wallet/grant` and `POST /wallet/debit` with idempotency enforcement | 5 | `[!]` | F-02 (amounts) |
| CC-26 | Fully wire `POST /launch/claim-incentive` with atomic claim increment | 5 | `[!]` | F-05 (amounts) |
| CC-27 | Write n8n workflow JSON: onboarding token grant on first login | 5 | `[!]` | F-02, F-05 |
| CC-28 | Load test wallet grant/debit for concurrent race condition verification | 5 | `[ ]` | CC-25 |

### Phase 6 — Launch Prep
| # | Task | Phase | Status | Blocked by |
|---|---|---|---|---|
| CC-29 | Load launch giveaway seed data (amounts Founder-approved) | 6 | `[!]` | F-05, F-06 |
| CC-30 | Write n8n workflow JSON: referral bonus grant | 6 | `[!]` | F-06 |
| CC-31 | Offline Galaxy population cycle: strip PII from smartvault_activity export, upload to bca-shell-v1 | 6 | `[ ]` | Phase 3 complete |
| CC-32 | Append Shell go-live lessons to `memory.md` | 6 | `[ ]` | Phase 6 complete |
| CC-33 | Update `BCA_VaultSpace_NotebookLM_Architecture.md` §4: add shell_api service + bca-shell-v1 Galaxy | 6 | `[ ]` | Phase 3 complete |
| CC-34 | Run smoke test checklist (session → permissions → wallet → tour → support) | 6 | `[ ]` | All phases complete |

---

## Codex

Model: GLM-5.2 or equivalent. No secrets. Generation and scaffolding tasks only.

| # | Task | Phase | Status | Input | Output |
|---|---|---|---|---|---|
| CX-01 | Generate all Pydantic request/response models from spec §5 API contracts | 2 | `[ ]` | `BCA_Universal_User_Shell_Spec.md §5` | `shell_api/models.py` |
| CX-02 | Generate integration test fixtures for token wallet flow (grant, debit, history) | 2 | `[ ]` | Wallet route spec | `shell_api/tests/fixtures/wallet.py` |
| CX-03 | Generate seed data JSON for `launch_incentives` collection (amounts placeholder) | 1 | `[ ]` | Spec §6 data model | `shell_api/scripts/incentives_seed.json` |
| CX-04 | Generate tour step config seed data for remaining BCA apps (post Phase 4) | 4+ | `[ ]` | App feature lists | `shell_api/scripts/tour_seeds/` |
| CX-05 | Generate `user_incentive_claims` unique index migration (idempotency ledger) | 1 | `[ ]` | Spec §6 | Index script |
| CX-06 | Generate `GET /wallet/history` pagination boilerplate (limit/offset pattern) | 2 | `[ ]` | Wallet route spec | Route fragment |
| CX-07 | Generate Stripe webhook event handler stubs for each subscription event type | 2 | `[ ]` | Spec §5 Stripe section | `stripe_webhook.py` stubs |

---

## Gemini

Free tier. Long-context reads, content generation, Galaxy population prep.

| # | Task | Phase | Status | Input | Output |
|---|---|---|---|---|---|
| G-01 | Summarize `BCA_Universal_User_Shell_Spec.md` for Galaxy source document | 3 | `[ ]` | Full spec | Clean summary doc for Galaxy upload |
| G-02 | Generate tour narration copy for Foodtruck Apollo (5+ features) | 4 | `[ ]` | Foodtruck Apollo feature list | `tour_narration_foodtruck_apollo.md` |
| G-03 | Long-context review: audit all BCA app flows for tour content gaps | 4+ | `[ ]` | App documentation | Gap report per app |
| G-04 | Strip PII from `smartvault_activity` export for Galaxy population cycle | 6 | `[ ]` | Raw activity export | PII-clean version for Galaxy |
| G-05 | Generate FAQ content for `bca-shell-v1` Galaxy (common user questions) | 3 | `[ ]` | Conrad Support Desk spec | FAQ doc for Galaxy upload |
| G-06 | Draft Conrad Center greeting copy variants (Founder selects) | 3 | `[ ]` | BCA brand guidelines + spec §2.3 | 3 greeting variants for Founder review |

---

## Smoke Test Checklist (Phase 6)

End-to-end validation before launch prep is complete.

| # | Test | Expected result |
|---|---|---|
| ST-01 | `POST /shell/session/start` with new user, app_context=foodtruck-apollo | < 200ms, returns session_id + greeting_text + constellation_apps |
| ST-02 | `POST /shell/permissions/grant` with all permissions accepted | user_permissions doc created, token_wallet created, smartvault_activity event logged |
| ST-03 | `GET /wallet/balance/{user_id}` after onboarding grant | Returns correct balance, tier=standard |
| ST-04 | `GET /shell/tour/foodtruck-apollo` | Returns 5+ steps with selectors and narration |
| ST-05 | `POST /shell/tour/complete` | smartvault_activity logged, token reward granted if configured |
| ST-06 | `POST /support/message` with a basic question | Returns Conrad response within 10s, activity logged |
| ST-07 | `POST /support/escalate` | Ticket created, n8n workflow triggered |
| ST-08 | `POST /launch/claim-incentive` with valid code | Tokens granted, claims_used incremented |
| ST-09 | `POST /launch/claim-incentive` second attempt (same user, same code) | Returns `already_claimed` error, no double grant |
| ST-10 | `POST /wallet/debit` with insufficient balance | Returns `insufficient_balance` error, no balance change |
| ST-11 | Concurrent `POST /wallet/grant` (10 simultaneous, same idempotency_key) | Exactly one grant applied, others return idempotent success |
| ST-12 | `POST /stripe/webhook` with invalid signature | 400 rejected before DB touch |
| ST-13 | `GET /shell/tour/{app_id}` for app with no config | Graceful 404, no crash |
| ST-14 | `POST /shell/session/start` second call, same user | Returns existing permissions, no duplicate wallet |
