# BCA Full-Stack Agents Architecture

This document defines the operating hierarchy for BCA OS and Conrad.

## Parent Hierarchy

BCA OS is the single founder-controlled parent operating system. Conrad is the
central brain beneath BCA OS.

Claude, ChatGPT, Gemini, GLM, Opus, Sonnet, Haiku, and other models are tools
Conrad may use. They are not the parent brain.

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

## Conrad Role

Conrad is the founder assistant, public host, voice, tour guide, EXPO traffic
director, and universal intake point. The founder can send Conrad a note, file,
idea, decision, instruction, bug report, or task. Conrad must classify the
information, determine where it belongs, route it, record the action, and return
a routing receipt.

## Agent Operating Law

- Deterministic FastAPI routes handle intake and routing before any model is used.
- LLMs and agents operate at the edges: drafting, review, enrichment, execution,
  and asynchronous follow-up.
- Specialized brains live beneath Conrad and do not bypass Conrad's intake,
  routing, audit, or security rules.
- Project sources of truth remain authoritative for code, schemas, deployments,
  tests, and technical plans.

## Memory Layers

- Conrad Inbox: temporary intake folders for unclassified information.
- Working Memory: `~/dev/expo-os/memory.md`, used for current context and
  short-lived operating notes.
- VaultSpace: SQLite-backed durable write and system-of-record layer.
- Project Sources of Truth: approved repositories and project documentation.
- NotebookLM Galaxies: curated read/query layers, never primary write locations.
- Founder Private Vault: founder-only encrypted location for sensitive personal,
  strategy, financial, legal, confidential, and restricted information.
- Secrets Storage: `.env`, hosting environment variables, or secret manager only.

## Phase 1 Intake Hot Path

`POST /intake` is deterministic:

1. Accept the submitted content and metadata.
2. Detect and redact likely secrets.
3. Classify the intake item.
4. Infer company, project, and product when possible.
5. Route to the correct destination.
6. Store the intake record in `intake_items`.
7. Store the routing decision in append-only `audit_log`.
8. Return a routing receipt.

Secrets are quarantined and routed to `secret_manager_required`. Secret values
must never be written to Git, `memory.md`, narrative VaultSpace records,
NotebookLM Galaxies, logs, routing receipts, or chat memory.
