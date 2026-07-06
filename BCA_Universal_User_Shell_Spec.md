# BCA Universal User Shell — Product Spec
**Module:** BCA Universal User Shell
**Status:** Spec — awaiting Founder approval (Phase 0 gate)
**Last updated:** 2026-06-18
**Architecture rule:** No code written until Founder approves this document.

---

## 1. Module Overview

The BCA Universal User Shell is the standard entry and containment layer for every
BCA product. Any link, QR code, ad, embed, or shared preview routes through it.
It handles first-contact identity, permissions, onboarding, agent presence, support,
and token economy — once, across all BCA apps — so no individual app has to rebuild
this infrastructure.

**Invariants (non-negotiable):**
- Deterministic hot-path flows stay in FastAPI + SQLite. Conrad never sits in that loop.
- Agents live at the edges only (support desk, tour narration, async logging).
- n8n is the orchestration layer for all multi-step workflows.
- VaultSpace is the only runtime write target.
- Galaxies are read-only at runtime.
- MCP bridge is the only sanctioned path between Conrad and the memory layers.
- No frontend code built without explicit Founder approval (Phase 7 gate).
- No secrets, billing keys, or customer PII in any content field.

---

## 2. Named Concepts

### 2.1 BCA Landing Shell
The universal entry point. Every inbound link, QR code, advertisement, embed, or
app preview routes to this shell first — regardless of which BCA product was the
origin. The shell detects the origin app context from the URL query param, subdomain,
or referrer and bootstraps the correct experience. It is a lightweight host layer,
not a full-stack app.

### 2.2 BCA App Constellation
A floating visual array of BCA apps displayed on the Landing Shell. Gives the user
awareness of the full BCA ecosystem and allows lateral navigation between apps
without leaving the shell context. Each constellation node carries: app name,
thumbnail, short tagline, and launch action.

### 2.3 Conrad Center Greeting
Conrad appears front-and-center on first load using the founder-approved Conrad image.
He delivers a personalized (or context-aware) welcome message and orients the user
to the shell and the selected app. This is the user's first interaction with Conrad.
Greeting copy is approved by Founder before launch.

### 2.4 Conrad Permission Cards
A structured, sequential permission request UI. Conrad presents plain-language cards
for each permission category. The user accepts or declines each individually. Cards
are shown once per session for new users; returning users see only changed or
pending permissions. Permission state is written to VaultSpace immediately on grant.

Permission categories (v1):
- Memory & personalization (cross-session Conrad memory)
- Notifications (push/email opt-in)
- Cross-app token wallet (link wallet to account)
- Location (app-specific, shown only when relevant)

### 2.5 App Takeover Stage
After permissions are handled, the selected app (e.g., Foodtruck Apollo) expands to
fill the primary viewport. The landing shell recedes. The App Takeover Stage is the
main content area that hosts the active BCA product. The shell chrome (Conrad HUD,
token badge) persists as an overlay layer.

### 2.6 Conrad HUD
Conrad minimizes to a compact persistent corner element (default: bottom-right,
configurable per-app). The HUD contains: Conrad avatar thumbnail, unread message
badge, quick-action icon row (support, wallet, tour). It does not block app content.
The HUD is the primary re-entry point for all Conrad interactions post-onboarding.

### 2.7 Conrad Spotlight Tour
An optional guided tour triggered from the Conrad HUD post-onboarding. Conrad
walks the user through key features one step at a time. Each step: a target
UI element lifts (CSS z-index), a darkened overlay surrounds it, Conrad narrates
the feature via text (and optionally audio). Tour steps are app-specific configs
stored in SQLite. Tour completion is logged to SmartVault and may trigger a
token reward.

### 2.8 Conrad Support Desk
Conrad's help surface, accessible at any time from the Conrad HUD. Handles:
- FAQ answers (Galaxy-backed, source-grounded)
- Complaint intake and logging
- App feature questions
- Human escalation trigger (creates support ticket, fires n8n notification)

All support interactions are logged async to SmartVault Activity Ledger. Conrad
never blocks the hot path; support desk calls are async at the edge.

### 2.9 BCA Token Wallet
A cross-app token economy. Users hold a single token balance usable in any BCA app.
Token operations (earn, spend, grant, transfer) are deterministic FastAPI + SQLite
flows — no agent in the loop. The wallet balance is displayed in the Conrad HUD and
on a dedicated wallet panel. Tier (Standard/Pro) is stored on the wallet document
and governs token allowances.

### 2.10 SmartVault Activity Ledger
A VaultSpace collection (`smartvault_activity`) that is the canonical audit trail
for all user activity across the BCA shell and apps. Events logged: session start,
permission grants, tour steps, support messages, token operations, app navigation,
escalations, incentive claims. The ledger is append-only. It feeds offline Galaxy
population cycles — never queried in the hot path.

### 2.11 Standard and Pro Pricing
Two subscription tiers, Stripe-backed.

| | Standard | Pro |
|---|---|---|
| Price | TBD (Founder approval) | TBD (Founder approval) |
| Monthly token allowance | TBD | TBD |
| Conrad routing priority | Standard queue | Priority queue |
| Cross-app analytics | No | Yes |
| Support SLA | Best effort | Accelerated |
| Giveaway eligibility | Yes | Yes |

Stripe product and price IDs require Founder approval before creation.
Webhook signature validation is mandatory (existing BCA guardrail).

### 2.12 Launch Giveaways
An incentive layer active at launch and for configurable campaigns. Components:
- **Automatic onboarding grant:** free token credit on first verified login (one
  per `user_id`, idempotency enforced).
- **Founder credit codes:** short alphanumeric codes the Founder can distribute
  directly, each with a configurable token value and claim limit.
- **Referral bonus:** tokens granted to referrer and referee on first referred
  sign-up (n8n workflow governs).
- **Time-limited giveaways:** campaign records with expiry, max-claims counter,
  and eligibility rules.

All giveaway logic lives in the `launch_incentives` collection. Eligibility checks
and atomic claim increments prevent abuse.

---

## 3. User Flow

```
[Entry: link / QR / ad / embed / shared link → any BCA app]
         |
         v
[BCA Landing Shell loads]
  · Detects origin app context (query param ?app=foodtruck-apollo, subdomain, referrer)
  · Calls POST /shell/session/start → receives session_id + shell_config
  · Renders BCA App Constellation
  · Fires Conrad Center Greeting
         |
         v
[Conrad Permission Cards]
  · Cards shown sequentially for new users
  · Each card: ACCEPT → writes to user_permissions, triggers VaultSpace log
  · DECLINE → user proceeds with limited/default-off feature set
  · All permissions processed → calls POST /shell/permissions/grant
         |
         v
[App Takeover Stage]
  · Selected app expands to fill viewport (animation)
  · Shell chrome (Conrad HUD, token badge) overlays
  · Calls GET /wallet/balance/{user_id} to populate HUD badge
         |
         v
[Conrad HUD activates]
  · Conrad: "Would you like a quick guided tour, or would you rather get started?"
         |
         ├──── [Tour] ────────────────────────────────────────────────────┐
         |                                                                 |
         v                                                                 v
[Get Started — app runs normally]                            [Conrad Spotlight Tour]
  · Conrad HUD available on demand                             · GET /shell/tour/{app_id}
  · Support Desk via HUD tap                                   · Steps loop: overlay → spotlight
                                                               · Conrad narrates each feature
                                                               · User: Next / Skip / Pause
                                                               · POST /shell/tour/complete
                                                               · Token reward logged
                                                                         |
                                                                         v
                                                               [App runs normally]
                                                               Conrad HUD active
         |
         v
[Conrad Support Desk — available any time via HUD]
  · User sends message → POST /support/message
  · Conrad responds (async Galaxy query via MCP bridge)
  · Escalation path → POST /support/escalate → ticket + n8n notification
  · All interactions logged → smartvault_activity
         |
         v
[SmartVault Activity Ledger — continuous, async, background]
  · All events appended asynchronously — never blocks UI or hot path
  · Feeds offline Galaxy population cycles
```

**Returning user flow (abbreviated):**
```
[Entry] → [Landing Shell: session restored] → [App Takeover Stage] → [HUD active]
          · No permission cards if already granted
          · No tour prompt if already completed
          · Token balance refreshed
```

---

## 4. Frontend Component Map

These are planning-only. No frontend is built until Founder approves Phase 7.

| Component | Role | Parent | Key Props/State |
|---|---|---|---|
| `<BCALandingShell>` | Root wrapper. Manages shell state, routing, app context. | — | `appContext`, `sessionId`, `userId` |
| `<AppConstellation>` | Floating grid of BCA app nodes. | LandingShell | `apps[]`, `onAppSelect` |
| `<ConstellationNode>` | Single app card in constellation. | AppConstellation | `appId`, `name`, `thumbnail`, `tagline` |
| `<ConradCenter>` | Hero greeting. Conrad image + welcome text. Manages permission card queue. | LandingShell | `greetingText`, `permissionsQueue[]` |
| `<PermissionCard>` | Single permission request card. | ConradCenter | `type`, `title`, `description`, `onAccept`, `onDecline` |
| `<AppTakeoverStage>` | Full-viewport app container. Handles takeover animation. | LandingShell | `appId`, `appUrl`, `onReady` |
| `<ConradHUD>` | Persistent mini-Conrad corner element. | LandingShell (overlay) | `unreadCount`, `tokenBalance`, `position` |
| `<HUDAvatar>` | Conrad thumbnail image in HUD. | ConradHUD | `src`, `onClick` |
| `<HUDActionRow>` | Icon row: support, wallet, tour buttons. | ConradHUD | `onSupportOpen`, `onWalletOpen`, `onTourStart` |
| `<SpotlightTour>` | Tour engine. Manages step sequence and overlay. | LandingShell (overlay) | `steps[]`, `currentStep`, `onComplete`, `onSkip` |
| `<SpotlightOverlay>` | Dimmed backdrop with cutout for spotlighted element. | SpotlightTour | `targetSelector`, `narration`, `onNext`, `onSkip` |
| `<ConradSupportDesk>` | Chat/FAQ panel. Expands from HUD. | ConradHUD | `sessionId`, `appContext`, `history[]` |
| `<SupportMessage>` | Single message bubble in support desk. | ConradSupportDesk | `role` (user/conrad), `content`, `timestamp` |
| `<TokenWalletBadge>` | Token balance display in HUD. Taps to open panel. | ConradHUD | `balance`, `tier` |
| `<TokenWalletPanel>` | Full wallet view: balance, tier, history, earn opportunities. | ConradHUD | `userId`, `balance`, `transactions[]` |
| `<OnboardingIncentiveBanner>` | Launch giveaway notification. Dismissible. | BCALandingShell | `tokensGranted`, `message`, `onDismiss` |
| `<PricingModal>` | Standard vs Pro comparison. Triggered from HUD or upgrade prompt. | BCALandingShell | `currentTier`, `onSelectPlan` |

**Shell state machine (high level):**
```
LOADING → GREETING → PERMISSIONS → TAKEOVER → HUD_ACTIVE
                                                  ↓        ↑
                                               TOUR    SUPPORT_DESK
```

---

## 5. Backend / API Contract Map

All endpoints extend the existing MCP Bridge FastAPI service or a new `shell_api`
service. Decision (Founder input needed): extend port 8001 or add a new port 8002.
Recommendation: new `shell_api` service to keep concerns separate and avoid
overloading the MCP bridge.

### Shell Session

**`POST /shell/session/start`**
```
Request:  { app_context: str, referrer_url: str, user_id: str | null }
Response: { session_id: str, shell_config: obj, constellation_apps: App[],
            greeting_text: str, existing_permissions: obj | null }
Side effects: writes shell_sessions doc; appends smartvault_activity event
Hot path: YES — must complete < 200ms. No agent call. No Galaxy query.
```

**`POST /shell/session/end`**
```
Request:  { session_id: str, user_id: str | null }
Response: { ok: bool, duration_seconds: int }
Side effects: closes session doc; logs to smartvault_activity
```

### Permissions

**`POST /shell/permissions/grant`**
```
Request:  { session_id: str, user_id: str, permissions: [{type: str, granted: bool}] }
Response: { ok: bool, wallet_created: bool, wallet_id: str | null }
Side effects: upserts user_permissions doc; creates token_wallet if cross_app_tokens
              granted and no wallet exists; logs to smartvault_activity
Hot path: YES — synchronous. No agent call.
```

### Tour

**`GET /shell/tour/{app_id}`**
```
Response: { app_id: str, steps: TourStep[], version: str }
TourStep: { step_id: int, target_selector: str, title: str, narration: str }
Source: tour_configs collection. Static read — no agent, no Galaxy.
```

**`POST /shell/tour/complete`**
```
Request:  { session_id: str, user_id: str, app_id: str, steps_completed: int }
Response: { ok: bool, tokens_earned: int }
Side effects: logs to smartvault_activity; if tokens_earned > 0 calls wallet/grant
```

### Token Wallet

**`GET /wallet/balance/{user_id}`**
```
Response: { balance: int, tier: str, monthly_allowance: int }
Hot path: YES — direct SQLite read, no agent.
```

**`GET /wallet/history/{user_id}`**
```
Query params: limit (default 20), offset (default 0)
Response: { transactions: Transaction[], total: int }
Transaction: { id: str, amount: int, direction: str, reason: str,
               app_context: str, ts: ISODate }
```

**`POST /wallet/grant`**
```
Request:  { user_id: str, amount: int, reason: str, source: str, idempotency_key: str }
Response: { ok: bool, new_balance: int, transaction_id: str }
Side effects: SQLite transaction: token_transactions insert + token_wallet
              balance update (atomic). Idempotency key prevents double-grant.
Guardrail: source must be in allowlist (onboarding-grant, tour-complete,
           referral, founder-credit, admin).
```

**`POST /wallet/debit`**
```
Request:  { user_id: str, amount: int, reason: str, app_context: str,
            idempotency_key: str }
Response: { ok: bool, new_balance: int, transaction_id: str }
              | { ok: false, error: "insufficient_balance" }
Side effects: SQLite transaction (same as grant, direction=debit).
Guardrail: balance check inside transaction. Fail-fast on insufficient funds.
```

### Support Desk

**`POST /support/message`**
```
Request:  { session_id: str, user_id: str | null, message: str, app_context: str }
Response: { response: str, suggested_actions: Action[] | null, escalate_flag: bool }
Side effects: Conrad agent call (async via MCP bridge → Galaxy query);
              logs both message and response to smartvault_activity.
NOT in hot path — async edge call. Client shows typing indicator while pending.
```

**`POST /support/escalate`**
```
Request:  { session_id: str, user_id: str, issue_summary: str }
Response: { ticket_id: str, eta: str }
Side effects: creates support_tickets doc; fires n8n escalation notification
              workflow; logs to smartvault_activity.
```

**`GET /support/history/{session_id}`**
```
Response: { messages: SupportMessage[] }
SupportMessage: { role: str, content: str, ts: ISODate }
Source: smartvault_activity filtered by session_id + event_type=support_message.
```

### Launch Incentives

**`POST /launch/claim-incentive`**
```
Request:  { user_id: str, incentive_code: str | null }
Response: { ok: bool, tokens_granted: int, message: str }
              | { ok: false, error: "already_claimed" | "expired" | "invalid_code" }
Side effects: atomic $inc on claims_used; idempotency check on (user_id, incentive_id);
              calls wallet/grant on success; logs to smartvault_activity.
```

**`POST /launch/onboarding-grant`** *(internal — called by session/start on first login)*
```
Request:  { user_id: str, session_id: str }
Response: { ok: bool, tokens_granted: int }
Guardrail: one grant per user_id (idempotency enforced in DB layer).
```

### Pricing

**`GET /shell/pricing`**
```
Response: { tiers: Tier[] }
Tier: { name: str, price_monthly_cents: int, token_allowance: int, features: str[] }
Source: static config collection or env-driven JSON. No agent.
```

### Stripe Webhooks

**`POST /stripe/webhook`** *(existing BCA pattern — extend, not replace)*
```
Events handled:
  customer.subscription.created  → update token_wallet.tier, log activity
  customer.subscription.updated  → same
  customer.subscription.deleted  → downgrade to standard, log activity
Guardrail: Stripe-Signature header validated before any processing.
```

---

## 6. Data Model Sketch

### `shell_sessions`
```json
{
  "_id": "ObjectId",
  "session_id": "uuid-v4",
  "user_id": "string | null",
  "app_context": "foodtruck-apollo",
  "referrer_url": "string",
  "permissions_granted": ["memory", "cross_app_tokens"],
  "tour_completed": false,
  "support_message_count": 0,
  "created_at": "ISODate",
  "last_active": "ISODate",
  "ended_at": "ISODate | null"
}
```
Indexes: `session_id` (unique), `user_id`, `created_at`

### `user_permissions`
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "permissions": {
    "memory": true,
    "notifications": false,
    "location": false,
    "cross_app_tokens": true
  },
  "granted_at": "ISODate",
  "updated_at": "ISODate"
}
```
Index: `user_id` (unique)

### `token_wallet`
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "balance": 500,
  "tier": "standard",
  "monthly_allowance": 1000,
  "stripe_subscription_id": "string | null",
  "stripe_customer_id": "string | null",
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```
Index: `user_id` (unique)

### `token_transactions`
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "amount": 100,
  "direction": "credit",
  "reason": "onboarding-grant",
  "app_context": "bca-shell",
  "idempotency_key": "string",
  "ts": "ISODate"
}
```
Indexes: `user_id + ts`, `idempotency_key` (unique sparse)

### `smartvault_activity`
```json
{
  "_id": "ObjectId",
  "user_id": "string | null",
  "session_id": "string",
  "event_type": "session_start",
  "payload": {},
  "app_context": "string",
  "ts": "ISODate"
}
```
Event types: `session_start`, `session_end`, `permission_granted`, `tour_step`,
`tour_complete`, `support_message`, `support_escalate`, `token_grant`, `token_debit`,
`app_navigate`, `incentive_claim`
Indexes: `user_id + ts`, `session_id`, `event_type + ts`
Note: this collection is append-only. No updates, no deletes.

### `support_tickets`
```json
{
  "_id": "ObjectId",
  "ticket_id": "uuid-v4",
  "user_id": "string",
  "session_id": "string",
  "issue_summary": "string",
  "status": "open",
  "app_context": "string",
  "created_at": "ISODate",
  "updated_at": "ISODate"
}
```
Indexes: `ticket_id` (unique), `user_id`, `status`

### `tour_configs`
```json
{
  "_id": "ObjectId",
  "app_id": "foodtruck-apollo",
  "steps": [
    {
      "step_id": 1,
      "target_selector": "#menu-panel",
      "title": "Your Menu",
      "narration": "This is where you manage your full menu..."
    }
  ],
  "version": "1.0",
  "updated_at": "ISODate"
}
```
Index: `app_id` (unique)

### `launch_incentives`
```json
{
  "_id": "ObjectId",
  "incentive_id": "uuid-v4",
  "code": "FOUNDER50",
  "type": "token_grant",
  "amount": 500,
  "max_claims": 1000,
  "claims_used": 0,
  "eligible_tiers": ["standard", "pro"],
  "expires_at": "ISODate | null",
  "active": true,
  "created_at": "ISODate"
}
```
Index: `code` (unique sparse), `active + expires_at`

### `user_incentive_claims` *(idempotency ledger)*
```json
{
  "_id": "ObjectId",
  "user_id": "string",
  "incentive_id": "string",
  "claimed_at": "ISODate"
}
```
Index: `(user_id, incentive_id)` (unique — enforces one-claim-per-user-per-incentive)

---

## 7. Risks and Guardrails

| Risk | Severity | Guardrail |
|---|---|---|
| Conrad in the hot path causes latency spikes | High | All Conrad/agent calls are async. `POST /shell/session/start` must complete < 200ms with no agent call. |
| Token wallet race condition / double-grant | High | SQLite transaction wraps every token debit/credit. Idempotency keys on all grant and debit requests. |
| Permission state lost between sessions | Medium | `user_permissions` written synchronously on grant. Shell reads it at session start and injects into shell_config. |
| Stripe webhook missed or skipped | High | Existing BCA guardrail: Stripe-Signature header validated before any processing. n8n handles retry on webhook failure. |
| PII or secrets written to Galaxies | Critical | `smartvault_activity` never fed to Galaxies directly. Population cycles strip user_id and PII fields. Existing invariant. |
| Tour selector drift (UI changes break tour steps) | Medium | Tour configs versioned. If target_selector returns no element, step is skipped gracefully — tour does not crash. |
| Incentive abuse (multiple onboarding claims) | Medium | `user_incentive_claims` unique index on (user_id, incentive_id). Atomic $inc on claims_used with max_claims guard. |
| Frontend built without approval | Low/Policy | Hard rule in this spec and in CLAUDE.md: no frontend code until Founder explicitly unlocks Phase 7. |
| Shell API scope creep on MCP bridge | Medium | Shell API runs as a separate FastAPI service (port 8002). MCP bridge stays focused on Conrad ↔ memory layer only. |
| Conrad support response latency > 5s | Medium | Client shows typing indicator. Support desk is async — response time SLA is a UX concern, not a correctness concern. Long-term: stream Conrad responses. |
| Token allowance config not yet approved | Blocking | Phase 5 cannot begin until Founder approves Standard/Pro amounts. Placeholder values must not ship. |
