# BCA VaultSpace & NotebookLM Architecture

**Source of truth — memory layer for the EXPO OS / Conrad brain.**
Treat this as binding. Do not collapse or reroute these layers.

---

## 1. The Two-Layer Memory Model

Conrad's memory is split across two distinct layers with a hard rule:

| Layer | System | Role | Direction |
|---|---|---|---|
| **Write / Store** | VaultSpace (MongoDB) | Operational results, lessons, loop outputs, audit trail | Conrad → VaultSpace |
| **Read / Recall** | NotebookLM Galaxies | Long-term source-grounded knowledge, cited answers | Conrad ← Galaxies |

**The invariant:** Conrad writes to VaultSpace. Conrad reads from Galaxies. VaultSpace is never a Galaxy source at runtime — it feeds Galaxies offline during population cycles. Galaxies are never written to at runtime.

---

## 2. VaultSpace (Write Layer)

### What it is
VaultSpace is the operational write store. Every result Conrad produces, every lesson learned, every loop output lands here first. It is MongoDB-backed and lives on Render alongside the FastAPI core.

### MongoDB schema

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

### Access pattern
- **Write:** `POST /vault/write` on the MCP bridge (see §4).
- **Read recent:** `GET /vault/recent?limit=N` — used for context injection before Conrad acts.
- **Direct query:** `mongosh expo_os --eval "db.vaultspace.find().sort({ts:-1}).limit(5)"`

### Rules
- Hot-path FastAPI routes do **not** write to VaultSpace in the synchronous path. VaultSpace writes are async, at the edges.
- Never route live Stripe keys or customer PII into VaultSpace content fields.
- VaultSpace is the **only** runtime write target. NotebookLM Galaxies are read-only at runtime.

---

## 3. NotebookLM Galaxies (Read / Recall Layer)

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

## 4. MCP Bridge (The Corpus Callosum)

The MCP bridge is the only sanctioned path between Conrad and the memory layers. It runs as a FastAPI service on Render (port 8001 locally).

### Endpoints

| Endpoint | Direction | Purpose |
|---|---|---|
| `POST /galaxy/query` | Conrad → Galaxy | Source-grounded read with citations |
| `POST /vault/write` | Conrad → VaultSpace | Write result or lesson |
| `GET /vault/recent` | VaultSpace → Conrad | Recent context injection |
| `POST /conrad` | n8n → full loop | Query Galaxy + write VaultSpace in one call |

### MCP tools (for Claude Code / n8n direct use)
- `galaxy_query(question, notebook_id?)` — query a Galaxy, returns `{answer, citations, grounded}`
- `vault_write(source, content, tags?)` — write to VaultSpace, returns `inserted_id`
- `vault_read_recent(limit?)` — return recent VaultSpace entries

### Config
Copy `mcp_bridge/claude_mcp_config.json` into your Claude Code MCP settings. Set env vars:
```
MONGO_URI=mongodb://localhost:27017
MONGO_DB=expo_os
GOOGLE_API_KEY=<your key>
NOTEBOOKLM_NOTEBOOK_ID=corpora/<your-corpus-id>
```

---

## 5. The Full Memory Data Flow

```
                    ┌─────────────────────────────────┐
                    │         EXPO OS / Conrad          │
                    │   (executive layer, Sonnet 4.6)   │
                    └────────────┬────────────┬─────────┘
                                 │            │
                    query        │            │  write result / lesson
                                 ▼            ▼
              ┌──────────────────────┐   ┌─────────────────────────┐
              │  NotebookLM Galaxies │   │  VaultSpace (MongoDB)   │
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

## 6. Working Memory (`memory.md`)

`memory.md` is Conrad's session-scoped working memory. It sits in the repo root and is read at every session start.

**Format:**
```markdown
## YYYY-MM-DD
- Lesson or correction, one line.
```

**Write rule:** Conrad appends to `memory.md` when corrected or when something durable is learned. The n8n loop runner also appends after each unattended loop run. `memory.md` is committed to git — it is the human-readable audit trail of what Conrad has learned.

**Promotion:** Periodically, export `memory.md` content to the active Galaxy (offline population cycle) so long-term lessons become source-grounded citations.

---

## 7. Invariants (Non-Negotiable)

1. **VaultSpace = write only (at runtime).** Never read VaultSpace in the synchronous hot path — use `/vault/recent` for async context injection only.
2. **Galaxies = read only (at runtime).** Population is an offline, manual, Teacher-blessed process.
3. **MCP bridge is the only path.** Direct MongoDB calls from application code bypass the audit trail — don't do it except in the bridge itself.
4. **No secrets in content fields.** Neither VaultSpace nor Galaxies should ever hold live API keys, Stripe credentials, or customer PII.
5. **Agents at the edges.** The FastAPI hot path (guest flow, menu filter, ticket) never calls the MCP bridge synchronously. Galaxy queries and VaultSpace writes are async, advisory, or batch.
