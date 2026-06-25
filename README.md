# BCA OS / Conrad Intake

BCA OS is the single founder-controlled parent operating system. Conrad is the
central brain beneath BCA OS: founder assistant, public host, voice, tour guide,
EXPO traffic director, and universal intake router. Claude and other models are
tools Conrad may use; they are not the parent brain.

## Architecture Summary

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

Conrad receives notes, files, ideas, decisions, instructions, bug reports, and
tasks. The Phase 1 intake path is deterministic: classify, infer destination,
redact likely secrets, store the intake record in MongoDB, append an audit
record, and return a routing receipt.

## Memory Locations

- Conrad Inbox: temporary intake folders at `~/BCA_OS_INBOX/{new,processing,processed,failed,receipts}`.
- Working Memory: `~/dev/expo-os/memory.md` for current context, temporary lessons,
  active priorities, and short-lived operating notes. It is not the permanent
  source of truth.
- VaultSpace: MongoDB durable write layer and system of record. Collections:
  `intake_items`, `audit_log`, `companies`, `projects`, `products`, `apps`,
  `agents`, `people`, `tasks`, `decisions`, `documents`, `ideas`, `research`,
  `communications`, `incidents`, `approvals`, and `memory_log`.
- Project Sources of Truth: the correct Git repo and approved project docs for
  code, config, schemas, deployment files, tests, and technical plans.
- NotebookLM Galaxies: curated read/query layers created only from approved
  VaultSpace or project-source material. Galaxies are not primary write locations.
- Founder Private Vault: separate founder-only encrypted location for sensitive
  strategy, financial, legal, confidential, personal, and restricted information.
- Secrets Storage: `.env`, hosting environment variables, or a secret manager only.

## Startup

MongoDB is required for live `/intake` storage and retrieval.

```bash
cd ~/dev/expo-os/mcp_bridge
python3.11 -m pip install -r requirements.txt
cp .env.example .env
uvicorn server:app --host 127.0.0.1 --port 8001
```

Expected `.env` values:

```bash
MONGO_URI=mongodb://localhost:27017
MONGO_DB=expo_os
GOOGLE_API_KEY=your_google_api_key_here
NOTEBOOKLM_NOTEBOOK_ID=your_notebook_id_here
PORT=8001
```

## Curl Examples

Health:

```bash
curl -sS http://127.0.0.1:8001/health
```

Expected response:

```json
{"status":"ok","service":"conrad-mcp-bridge"}
```

Submit a product idea:

```bash
curl -sS -X POST http://127.0.0.1:8001/intake \
  -H 'Content-Type: application/json' \
  -d '{"content":"Venue IQ should compare the current BEO against the previous approved version and display every change."}'
```

Expected response shape:

```json
{
  "intake_id": "intake_...",
  "received_at": "2026-...",
  "classification": "product_feature_idea",
  "company": "Blue Collar Apps Co.",
  "project": "Venue IQ",
  "product": "Venue IQ",
  "sensitivity": "NORMAL",
  "primary_destination": "VaultSpace / ideas",
  "secondary_destination": "Venue IQ product backlog",
  "action_taken": "routed_to_ideas_and_backlog",
  "approval_required": true,
  "routing_confidence": 0.86,
  "status": "routed"
}
```

Recent intake:

```bash
curl -sS 'http://127.0.0.1:8001/intake/recent?limit=5'
```

One intake item:

```bash
curl -sS http://127.0.0.1:8001/intake/intake_REPLACE_WITH_ID
```

Secret quarantine example using a fake test key:

```bash
curl -sS -X POST http://127.0.0.1:8001/intake \
  -H 'Content-Type: application/json' \
  -d '{"content":"Store this fake test key: sk-proj-FAKEKEYFORTESTINGONLY1234567890ABCDE"}'
```

Expected secret response fields:

```json
{
  "classification": "secret_or_credential",
  "sensitivity": "SECRET",
  "primary_destination": "secret_manager_required",
  "action_taken": "redacted_and_quarantined",
  "approval_required": true,
  "status": "quarantined"
}
```

## Founder Intake Convention

Messages beginning with:

```text
CONRAD:
```

are BCA OS intake items. Conrad must return a routing receipt containing:
classification, destination, sensitivity, action taken, approval required, and
status.

## Troubleshooting

Check MongoDB:

```bash
mongosh --eval 'db.runCommand({ ping: 1 })'
```

Check intake collections:

```bash
mongosh expo_os --eval 'db.intake_items.find().sort({timestamp:-1}).limit(5)'
mongosh expo_os --eval 'db.audit_log.find().sort({timestamp:-1}).limit(5)'
```

Run unit tests without MongoDB:

```bash
cd ~/dev/expo-os
python3.11 -m unittest tests.test_intake
```

## Security Rules

Never store API keys, passwords, database credentials, OAuth tokens, private
keys, bearer tokens, JWTs, or live payment credentials in Git, `memory.md`,
narrative VaultSpace records, NotebookLM Galaxies, logs, routing receipts, or
chat memory. Secret-looking values are redacted, quarantined, and routed to
`secret_manager_required`.
