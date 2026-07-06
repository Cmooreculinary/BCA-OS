# BCA VaultSpace & NotebookLM Architecture

**Source of truth — memory layer for BCA OS / Conrad.**
Treat this as binding. Do not collapse or reroute these layers.

---

## 1. BCA OS Hierarchy

BCA OS is the single founder-controlled parent operating system. Conrad is the
central brain beneath BCA OS: founder assistant, public host, voice, tour guide,
EXPO traffic director, and universal intake router.

Claude is not the parent brain. Claude is a tool or model Conrad may use.

```
BCA OS
└── Conrad
    ├── Companies
    ├── Projects
    ├── Products
    ├── Apps
    ├── Agents
    ├── Staff
    ├── Specialized brains
    ├── Founder projects
    └── Founder-private systems
```

---

## 2. Canonical Memory Locations

### A. Conrad Inbox

Temporary intake location for unclassified information.

Local folders:

```
~/BCA_OS_INBOX/new
~/BCA_OS_INBOX/processing
~/BCA_OS_INBOX/processed
~/BCA_OS_INBOX/failed
~/BCA_OS_INBOX/receipts
```

### B. Working Memory

Location:

```
~/dev/expo-os/memory.md
```

Purpose: current context, temporary lessons, active priorities, and short-lived
operating notes. This is not the permanent source of truth.

### C. VaultSpace

VaultSpace is the durable write and system-of-record layer. It is SQLite-backed.

Canonical collections:

- `intake_items`
- `audit_log`
- `companies`
- `projects`
- `products`
- `apps`
- `agents`
- `people`
- `tasks`
- `decisions`
- `documents`
- `ideas`
- `research`
- `communications`
- `incidents`
- `approvals`
- `memory_log`

### D. Project Sources of Truth

The correct Git repository and approved project documentation remain
authoritative for code, configuration, schemas, deployment files, tests, and
technical plans.

### E. NotebookLM Galaxies

NotebookLM Galaxies are curated read and query layers created only from approved
VaultSpace or project-source material. Galaxies are not primary write locations.

### F. Founder Private Vault

The Founder Private Vault is a separate founder-only encrypted location for
personal information, sensitive strategy, financial information, legal
information, confidential communications, and restricted projects.

### G. Secrets Storage

API keys, passwords, database credentials, OAuth tokens, and other secrets may
only be stored in `.env` files, hosting environment variables, or a secret
manager.

Never store secrets in:

- Git
- `memory.md`
- narrative VaultSpace records
- NotebookLM Galaxies
- logs
- routing receipts
- chat memory

---

## 3. Runtime Read/Write Model

Conrad's memory is split across two distinct layers with a hard rule:

| Layer | System | Role | Direction |
|---|---|---|---|
| **Write / Store** | VaultSpace (SQLite) | Operational results, lessons, loop outputs, audit trail | Conrad → VaultSpace |
| **Read / Recall** | NotebookLM Galaxies | Long-term source-grounded knowledge, cited answers | Conrad ← Galaxies |

**The invariant:** Conrad writes to VaultSpace. Conrad reads from Galaxies. VaultSpace is never a Galaxy source at runtime — it feeds Galaxies offline during population cycles. Galaxies are never written to at runtime.

---

## 4. VaultSpace (Write Layer)

### What it is
VaultSpace is the operational write store. Every result Conrad produces, every lesson learned, every loop output lands here first. It is SQLite-backed and lives on Render alongside the FastAPI core.

### SQLite schema

**Collection: `vaultspace`**
```json
{
  "_id": "ObjectId",
  "source": "string",       // who wrote it: "conrad-loop", "n8n-loop-runner", "manual"
  "content": "string",      // the result, lesson, or answer
  "tags": ["string"],       // e.g. ["loop", "auto"], ["memory-append"], ["lesson"]
  "ts": "ISODate"           // UTC timestamp, indexed for recency reads
}
```

**Collection: `memory_log`** *(optional second index — mirrors memory.md for queryability)*
```json
{
  "_id": "ObjectId",
  "date": "YYYY-MM-DD",
  "lesson": "string",
  "ts": "ISODate"
}
```

**Collection: `intake_items`**
Stores deterministic Conrad intake routing records. Content is redacted before
storage when a likely secret is detected.

**Collection: `audit_log`**
Append-only routing decisions. It must never include raw secret values.

### Access pattern
- **Write:** `POST /vault/write` on the MCP bridge (see §4).
- **Read recent:** `GET /vault/recent?limit=N` — used for context injection before Conrad acts.
- **Direct query:** `sqlite3 mcp_bridge/data/expo_os.sqlite3 "select document_json from documents where collection_name='vaultspace' order by updated_at desc limit 5;"`

### Rules
- Deterministic intake may write `intake_items` and `audit_log` synchronously.
- LLMs and agents do **not** sit in the intake hot path.
- Guest/product hot-path routes do **not** call Galaxy or agent workflows synchronously.
- Never route live Stripe keys or customer PII into VaultSpace content fields.
- VaultSpace is the general operational runtime write target. NotebookLM Galaxies are read-only at runtime.
- Founder-only material routes to the Founder Private Vault, not public project memory.
- Secrets route to secret-manager-required quarantine, not narrative memory.

---

## 5. NotebookLM Galaxies (Read / Recall Layer)

### What they are
Galaxies are NotebookLM notebooks populated with curated source documents — architecture docs, session summaries, domain knowledge, operator playbooks. Conrad queries them for source-grounded, cited answers.

### How they are populated (offline)
1. Export relevant documents (session summaries, VaultSpace snapshots, architecture docs) to a staging folder.
2. Upload to the target Galaxy in NotebookLM manually, or via the Gemini File API + corpus creation.
3. Run a Teacher checkpoint (Opus 4.8) to confirm citation quality before marking a Galaxy active.

**Never populate a Galaxy with live credentials, Stripe data, or customer PII.**

### How Conrad queries them (runtime)
Conrad queries via the MCP bridge (`galaxy_query` tool), which calls the Gemini Semantic Retrieval API against a corpus resource (`corpora/...`). The response includes an answer and citation sources.

If a native NotebookLM MCP endpoint ships, replace `galaxy_client.py` with that — the interface (`question` in, `{answer, citations, grounded}` out) stays the same.

### Galaxy naming convention
```
[domain]-[version]   e.g.  expo-os-v1, footruck-apollo-v1, maestro-ops-v1
```

---

## 6. MCP Bridge (The Corpus Callosum)

The MCP bridge is the only sanctioned path between Conrad and the memory layers. It runs as a FastAPI service on Render (port 8001 locally).

### Endpoints

| Endpoint | Direction | Purpose |
|---|---|---|
| `POST /galaxy/query` | Conrad → Galaxy | Source-grounded read with citations |
| `POST /vault/write` | Conrad → VaultSpace | Write result or lesson |
| `GET /vault/recent` | VaultSpace → Conrad | Recent context injection |
| `POST /intake` | Conrad → VaultSpace audit | Deterministic intake classification, routing, and receipt |
| `GET /intake/recent` | VaultSpace → Conrad | Recent intake records |
| `GET /intake/{intake_id}` | VaultSpace → Conrad | One intake record |
| `POST /conrad` | n8n → full loop | Query Galaxy + write VaultSpace in one call |

### MCP tools (for Claude Code / n8n direct use)
- `galaxy_query(question, notebook_id?)` — query a Galaxy, returns `{answer, citations, grounded}`
- `vault_write(source, content, tags?)` — write to VaultSpace, returns `inserted_id`
- `vault_read_recent(limit?)` — return recent VaultSpace entries

### Config
Copy `mcp_bridge/claude_mcp_config.json` into your Claude Code MCP settings. Set env vars:
```
SQLITE_PATH=./mcp_bridge/data/expo_os.sqlite3
SQLITE_DB=expo_os
GOOGLE_API_KEY=<your key>
NOTEBOOKLM_NOTEBOOK_ID=corpora/<your-corpus-id>
```

---

## 7. The Full Memory Data Flow

```
                    ┌─────────────────────────────────┐
                    │         BCA OS / Conrad           │
                    │   (central intake and routing)    │
                    └────────────┬────────────┬─────────┘
                                 │            │
                    query        │            │  write result / lesson
                                 ▼            ▼
              ┌──────────────────────┐   ┌─────────────────────────┐
              │  NotebookLM Galaxies │   │  VaultSpace (SQLite)    │
              │  (read-only, cited)  │   │  collection: vaultspace  │
              └──────────┬───────────┘   └──────────┬──────────────┘
                         │                          │
                  source-grounded                   │ offline (population cycle)
                  answers + citations               │ curated export → Galaxy
                         │                          │
                         └──────────────────────────┘
                                    ▲
                          MCP Bridge (FastAPI, Render)
                          corpus callosum of the brain

                    ┌─────────────────────────────────┐
                    │    n8n (orchestration layer)     │
                    │  triggers the /conrad loop,      │
                    │  writes lesson back to VaultSpace│
                    └─────────────────────────────────┘
```

---

## 8. Working Memory (`memory.md`)

`memory.md` is Conrad's session-scoped working memory. It sits in the repo root and is read at every session start.

**Format:**
```markdown
## YYYY-MM-DD
- Lesson or correction, one line.
```

**Write rule:** Conrad appends to `memory.md` when corrected or when something durable is learned. The n8n loop runner also appends after each unattended loop run. `memory.md` is committed to git — it is the human-readable audit trail of what Conrad has learned.

**Promotion:** Periodically, export `memory.md` content to the active Galaxy (offline population cycle) so long-term lessons become source-grounded citations.

---

## 9. Invariants (Non-Negotiable)

1. **BCA OS is the parent.** Conrad is the central brain beneath BCA OS.
2. **Conrad is universal intake.** Notes, files, ideas, decisions, instructions, bug reports, and tasks enter through Conrad and return a routing receipt.
3. **VaultSpace = durable write layer.** Intake writes go to `intake_items`; routing decisions go to append-only `audit_log`.
4. **Project sources remain authoritative.** Code, config, schemas, deployments, tests, and technical plans live in the correct Git repo and approved project docs.
5. **Founder-only means founder-only.** Founder-private information routes to the Founder Private Vault.
6. **Secrets never enter narrative memory.** Secret values do not go to Git, `memory.md`, VaultSpace content fields, Galaxies, logs, receipts, or chat memory.
7. **No LLM in the intake hot path.** Intake classification starts with deterministic rules.
8. **Galaxies = read only (at runtime).** Population is an offline, manual, Teacher-blessed process.
9. **MCP bridge is the only path.** Direct SQLite calls from application code bypass the audit trail; do not bypass it except in the bridge itself.
10. **Agents at the edges.** Guest/product hot paths never call the MCP bridge synchronously. Galaxy queries and non-intake VaultSpace writes are async, advisory, or batch.
