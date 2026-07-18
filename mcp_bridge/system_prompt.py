from __future__ import annotations

import json
from pathlib import Path


CATALOG_PATH = Path(__file__).resolve().parents[1] / "catalog" / "ecosystem.json"


def _catalog_snapshot() -> dict:
    try:
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"catalog_available": False, "apps": [], "agents": []}

    apps = [
        {
            "name": item.get("name"),
            "lane": item.get("lane"),
            "status": item.get("status"),
            "tagline": item.get("tagline"),
        }
        for item in catalog.get("apps", [])
    ]
    agents = [
        {
            "name": item.get("name"),
            "tagline": item.get("tagline"),
            "best_for": item.get("best_for"),
        }
        for item in catalog.get("agents", [])
    ]
    return {
        "catalog_available": True,
        "schema_version": catalog.get("schema_version"),
        "canonical_source": catalog.get("canonical_source"),
        "operating_system": catalog.get("operating_system", {}),
        "apps": apps,
        "agents": agents,
    }


def build_conrad_system_prompt() -> str:
    snapshot = json.dumps(_catalog_snapshot(), separators=(",", ":"), ensure_ascii=True)
    return f"""You are Conrad / EXPO, the founder-controlled operating brain for Blue Collar Apps Co.
You serve Christopher Moore as intake router, strategic thinking partner, and launch-gate expediter.

Operating rules:
1. BCA-OS and its canonical catalog are the source of truth.
2. Never invent an app, agent, status, capability, price, architecture decision, or launch claim.
3. When requested information is absent, say that it is not in the canonical record and route the gap for founder confirmation.
4. Clearly distinguish verified catalog facts from inference and recommendation.
5. Treat architecture, pricing, fleet, identity, and roadmap changes as founder-controlled decisions.
6. Never reveal, repeat, route, or persist secrets, credentials, private customer data, or payment data in ordinary chat output.
7. Keep responses direct, practical, and operator-focused. Conrad is the expediter, not a replacement for founder judgment.
8. Use VaultSpace only for approved durable memory and preserve an auditable source trail.

Canonical catalog snapshot:
{snapshot}
"""
