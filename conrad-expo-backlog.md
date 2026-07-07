# Conrad / EXPO Backlog
# Source: EXPO_Prototype_Build_Sheet_v0.1.md — Packets A–E
# Rule: one task per run, check off when committed.

- [x] A — Conrad's Constitution: CLAUDE.md committed with identity, delegation law, learning loop, cost law, guardrails
- [x] B — The Learning Loop: confirm memory.md appends work in a live session (add one corrected-lesson test entry; verify file grows)
- [x] C — MCP Bridge to SmartVaultSpace: working MCP connection Conrad → NotebookLM Galaxy (read/query) + SQLite VaultSpace (write); source-grounded answer with citation
- [x] D — The n8n Loop Runner: one n8n workflow — trigger → Conrad queries Galaxy → acts → writes vaultspace collection → appends memory.md, unattended
- [x] E — Teacher Routing Config: routing.md mapping task-type → model (Haiku / Sonnet / Opus ladder)
- [ ] F — BCA Universal User Shell: full product spec + implementation plan + task board; 3 new planning files created (Spec, Plan, Tasks); awaiting Founder + Teacher approval (Phase 0 gate) before any implementation begins

## Phase 1 — Conrad Intake and Memory Routing

- [x] Define BCA OS as the founder-controlled parent and Conrad as the central brain beneath it
- [x] Create Conrad Inbox folders at `~/BCA_OS_INBOX/{new,processing,processed,failed,receipts}`
- [x] Document canonical memory locations: Conrad Inbox, Working Memory, VaultSpace, project sources, NotebookLM Galaxies, Founder Private Vault, and Secrets Storage
- [x] Add deterministic `POST /intake` FastAPI endpoint
- [x] Generate routing receipt fields for intake submissions
- [x] Add deterministic routing rules for product ideas, technical bugs, founder-private notes, staff tasks, founder decisions, research notes, and general intake
- [x] Add likely-secret detection, redaction, quarantine status, and secret-manager routing
- [x] Add SQLite persistence helpers for `intake_items` and append-only `audit_log`
- [x] Add `GET /intake/recent` and `GET /intake/{intake_id}`
- [x] Add unit tests for Venue IQ product idea, Foodtruck Apollo bug, founder-private note, staff task, fake API key quarantine, and intake retrieval
- [x] Promote latest umbrella story into `catalog/umbrella-story.md` and `catalog/ecosystem.json`
- [x] Add Margin IQ intake alias and routing test

## Phase 2 — Conrad Intake Expansion

- [ ] Wire live SQLite-backed integration tests for `/intake`, `/intake/recent`, and `/intake/{intake_id}`
- [ ] Add durable routing receipts in `~/BCA_OS_INBOX/receipts`
- [ ] Add approved project backlog write adapters
- [ ] Add NotebookLM Galaxy population from approved VaultSpace/project-source exports
- [ ] Add n8n follow-up workflow for routed intake items
- [ ] Add public hosting deployment for the intake bridge
- [ ] Add voice intake
- [ ] Add email intake
- [ ] Add automatic file watching for `~/BCA_OS_INBOX/new`
