"""
BCA OS — the operating system layer for Blue Collar Apps Co.

Provides: routing, memory (Vault), policy/launch-gate enforcement,
Teacher Pattern dispatch, and the app catalog. All domain brains
run on top of this layer.
"""
from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any

import anthropic

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TaskClass(str, Enum):
    EXECUTION_LIGHT = "execution_light"   # Haiku
    EXECUTION_STD   = "execution_std"     # Sonnet
    ARCHITECTURE    = "architecture"      # Opus
    REVIEW          = "review"            # Opus


class Sensitivity(str, Enum):
    PUBLIC   = "public"
    INTERNAL = "internal"
    SECRET   = "secret"
    CUSTOMER = "customer"


# ---------------------------------------------------------------------------
# BCA App Catalog
# ---------------------------------------------------------------------------

BCA_APPS: dict[str, dict] = {
    "capkids": {
        "name": "CapKids",
        "domain": "youth-nutrition",
        "description": "Capacity-building nutrition tracker for K-12 programs",
        "launch_gates": ["COPPA", "school-district-MOU", "parental-consent"],
        "status": "pre-launch",
    },
    "roundtable": {
        "name": "RoundTable",
        "domain": "hospitality-ops",
        "description": "AI-assisted kitchen expediting and line communication tool",
        "launch_gates": ["beta-kitchen-partner"],
        "status": "beta",
    },
    "allergenshield": {
        "name": "AllergenShield",
        "domain": "food-safety",
        "description": "Real-time allergen cross-contact risk manager for restaurants",
        "launch_gates": ["liability-insurance", "licensed-dietitian-review"],
        "status": "pre-launch",
    },
    "trenchsms": {
        "name": "TrenchSMS",
        "domain": "hospitality-comms",
        "description": "Staff scheduling and shift-change SMS layer for hourly workers",
        "launch_gates": ["A2P-10DLC", "TCPA-compliance", "carrier-registration"],
        "status": "pre-launch",
    },
}

# ---------------------------------------------------------------------------
# BCA OS Brain Registry — all brains the OS knows about.
# Conrad handles everything until a dedicated brain is built and registered.
# ---------------------------------------------------------------------------

BCA_BRAINS: dict[str, dict] = {
    "conrad": {
        "name": "Conrad/EXPO",
        "scope": ["bca-company", "bca-apps", "agents", "host"],
        "description": "First brain. Front door for Chef. Hosts all BCA until a "
                       "dedicated brain exists for a domain.",
        "status": "active",
        "handles_until_built": ["personal", "staff"],
    },
    "personal": {
        "name": "Personal Brain",
        "scope": ["chef-personal", "calendar", "finance-personal", "life-ops"],
        "description": "Chef's personal context, calendar, notes, and life ops.",
        "status": "not-built",
        "owner": "conrad",   # Conrad handles this domain until brain is live
    },
    "staff": {
        "name": "Staff Brain",
        "scope": ["team", "hr-adjacent", "scheduling", "comms"],
        "description": "Team management, staff comms, scheduling, and HR-adjacent ops.",
        "status": "not-built",
        "owner": "conrad",
    },
}

# Domain → default brain mapping
DOMAIN_BRAIN: dict[str, str] = {
    "youth-nutrition":    "capkids",
    "hospitality-ops":    "roundtable",
    "food-safety":        "allergenshield",
    "hospitality-comms":  "trenchsms",
}

# Teacher Pattern: TaskClass → model
TEACHER_MODEL: dict[TaskClass, str] = {
    TaskClass.EXECUTION_LIGHT: "claude-haiku-4-5-20251001",
    TaskClass.EXECUTION_STD:   "claude-sonnet-4-6",
    TaskClass.ARCHITECTURE:    "claude-opus-4-8",
    TaskClass.REVIEW:          "claude-opus-4-8",
}

# Sensitivity tiers that must NOT go to cheaper/external adapters
_RESTRICTED_SENSITIVITY = {Sensitivity.SECRET, Sensitivity.CUSTOMER}


# ---------------------------------------------------------------------------
# Vault — simple JSON file-backed key/value store
# ---------------------------------------------------------------------------

class Vault:
    def __init__(self, path: Path):
        self._path = path
        self._data: dict[str, Any] = {}
        if path.exists():
            try:
                self._data = json.loads(path.read_text())
            except Exception:
                self._data = {}

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._path.write_text(json.dumps(self._data, indent=2, default=str))

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def all(self) -> dict:
        return dict(self._data)


# ---------------------------------------------------------------------------
# Routing decision
# ---------------------------------------------------------------------------

@dataclass
class RoutingDecision:
    intent: str
    brain: str
    domain: str
    task_class: TaskClass
    model: str
    policy_status: str
    gates_met: list[str] = field(default_factory=list)
    gates_missing: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        d = asdict(self)
        d["task_class"] = self.task_class.value
        return d


# ---------------------------------------------------------------------------
# BCA OS
# ---------------------------------------------------------------------------

class BCAOS:
    def __init__(self, vault_path: Path):
        self._vault = Vault(vault_path)
        self._client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self._providence_log: list[dict] = []

    # ---- catalog / status --------------------------------------------------

    def status(self) -> dict:
        return {
            "os": "BCA OS v1.0",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "brains": BCA_BRAINS,
            "apps": BCA_APPS,
            "vault_keys": list(self._vault.all().keys()),
            "providence_entries": len(self._providence_log),
        }

    # ---- policy / launch gates ---------------------------------------------

    def check_policy(self, brain: str) -> dict:
        app = BCA_APPS.get(brain)
        if not app:
            return {"ok": False, "error": f"Unknown brain/app: {brain}"}
        gates = app.get("launch_gates", [])
        met = self._vault.get(f"gates_met_{brain}") or []
        missing = [g for g in gates if g not in met]
        ok = len(missing) == 0
        return {
            "brain": brain,
            "status": app["status"],
            "gates_required": gates,
            "gates_met": met,
            "gates_missing": missing,
            "launch_ok": ok,
            "policy_status": "CLEAR" if ok else f"BLOCKED — missing: {missing}",
        }

    # ---- routing -----------------------------------------------------------

    def route(
        self,
        intent: str,
        domain_hint: str | None,
        task_class: TaskClass,
    ) -> RoutingDecision:
        domain = domain_hint or self._infer_domain(intent)
        brain  = DOMAIN_BRAIN.get(domain, "roundtable")
        model  = TEACHER_MODEL[task_class]
        policy = self.check_policy(brain)
        return RoutingDecision(
            intent=intent,
            brain=brain,
            domain=domain,
            task_class=task_class,
            model=model,
            policy_status=policy["policy_status"],
            gates_met=policy["gates_met"],
            gates_missing=policy["gates_missing"],
        )

    def _infer_domain(self, intent: str) -> str:
        intent_lower = intent.lower()
        if any(w in intent_lower for w in ("kid", "child", "school", "nutrition", "coppa")):
            return "youth-nutrition"
        if any(w in intent_lower for w in ("allergen", "allergy", "cross-contact")):
            return "food-safety"
        if any(w in intent_lower for w in ("sms", "text", "shift", "schedule")):
            return "hospitality-comms"
        return "hospitality-ops"

    # ---- dispatch (Teacher Pattern) ----------------------------------------

    def dispatch(
        self,
        decision: RoutingDecision,
        system: str,
        prompt: str,
        sensitivity: Sensitivity = Sensitivity.INTERNAL,
        max_tokens: int = 2048,
    ) -> str:
        if sensitivity in _RESTRICTED_SENSITIVITY and decision.task_class == TaskClass.EXECUTION_LIGHT:
            # Upgrade restricted data to Sonnet minimum
            model = TEACHER_MODEL[TaskClass.EXECUTION_STD]
        else:
            model = decision.model

        response = self._client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    # ---- vault helpers -----------------------------------------------------

    def remember(self, key: str, value: Any) -> None:
        self._vault.set(key, value)

    def recall(self, key: str) -> Any:
        return self._vault.get(key)

    # ---- providence --------------------------------------------------------

    def note_providence(self, note: str) -> None:
        entry = {
            "id": str(uuid.uuid4())[:8],
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "note": note,
        }
        self._providence_log.append(entry)
        existing = self._vault.get("providence_log") or []
        existing.append(entry)
        self._vault.set("providence_log", existing)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def boot_os(vault_path: str | Path | None = None) -> BCAOS:
    if vault_path is None:
        vault_path = Path(os.environ.get("BCA_VAULT_PATH", "bca_vault.json"))
    return BCAOS(Path(vault_path))
