"""Deterministic Conrad intake classification and routing.

No LLMs or agents run in this hot path. The rules here produce a routing
record, a redacted storage document, and a receipt for the caller.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class IntakeRequest(BaseModel):
    source: str | None = None
    submitted_by: str | None = None
    content_type: str | None = None
    content: str = Field(min_length=1)
    filename: str | None = None
    company: str | None = None
    project: str | None = None
    product: str | None = None
    sensitivity: str | None = None
    requested_action: str | None = None
    tags: list[str] = Field(default_factory=list)


SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("google_api_key", re.compile(r"AIza[0-9A-Za-z_-]{30,45}")),
    ("openai_key", re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}")),
    ("anthropic_key", re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}")),
    ("stripe_key", re.compile(r"\b(?:sk|pk|rk)_(?:live|test)_[A-Za-z0-9]{16,}\b")),
    ("github_token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("mongodb_uri", re.compile(r"mongodb(?:\+srv)?://[^:\s/@]+:[^@\s]+@[^\s]+")),
    ("jwt_token", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    (
        "private_key",
        re.compile(
            r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]+?-----END [A-Z ]*PRIVATE KEY-----",
            re.MULTILINE,
        ),
    ),
    ("password", re.compile(r"(?i)\b(password|passwd|pwd)\s*[:=]\s*['\"]?([^'\"\s]{8,})")),
    ("bearer_token", re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{20,}")),
)


PROJECT_ALIASES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Venue IQ", ("venue iq", "venue-iq", "venueiq")),
    ("Foodtruck Apollo", ("foodtruck apollo", "footruck apollo", "food truck apollo", "apollo checkout")),
    ("BCA OS", ("bca os", "expo os", "conrad", "vaultspace", "notebooklm", "notebook lm")),
)


def redact_secrets(value: str) -> tuple[str, set[str]]:
    redacted = value
    detected: set[str] = set()
    for name, pattern in SECRET_PATTERNS:
        if pattern.search(redacted):
            detected.add(name)
            if name == "password":
                redacted = pattern.sub(lambda m: f"{m.group(1)}=[REDACTED_SECRET]", redacted)
            else:
                redacted = pattern.sub("[REDACTED_SECRET]", redacted)
    return redacted, detected


def _joined_request_text(req: IntakeRequest) -> str:
    pieces = [
        req.source,
        req.submitted_by,
        req.content_type,
        req.content,
        req.filename,
        req.company,
        req.project,
        req.product,
        req.sensitivity,
        req.requested_action,
        " ".join(req.tags),
    ]
    return " ".join(piece for piece in pieces if piece)


def _redact_optional(value: str | None) -> str | None:
    if value is None:
        return None
    return redact_secrets(value)[0]


def _redact_tags(tags: list[str]) -> list[str]:
    return [redact_secrets(tag)[0] for tag in tags]


def _infer_project(req: IntakeRequest, text_lower: str) -> str | None:
    if req.project:
        return req.project
    if req.product:
        return req.product
    for project, aliases in PROJECT_ALIASES:
        if any(alias in text_lower for alias in aliases):
            return project
    return None


def _infer_product(req: IntakeRequest, inferred_project: str | None) -> str | None:
    if req.product:
        return req.product
    return inferred_project


def _infer_company(req: IntakeRequest, text_lower: str) -> str | None:
    if req.company:
        return req.company
    if "blue collar apps" in text_lower or "bca" in text_lower:
        return "Blue Collar Apps Co."
    if any(alias in text_lower for _, aliases in PROJECT_ALIASES for alias in aliases):
        return "Blue Collar Apps Co."
    return None


def _has_any(text_lower: str, words: tuple[str, ...]) -> bool:
    return any(word in text_lower for word in words)


def _build_audit_record(record: dict) -> dict:
    return {
        "intake_id": record["intake_id"],
        "timestamp": record["timestamp"],
        "classification": record["classification"],
        "sensitivity": record["sensitivity"],
        "destination": record["primary_destination"],
        "action_taken": record["action_taken"],
        "approval_required": record["approval_required"],
        "routing_confidence": record["routing_confidence"],
        "status": record["status"],
    }


def _build_receipt(record: dict) -> dict:
    return {
        "intake_id": record["intake_id"],
        "received_at": record["timestamp"],
        "classification": record["classification"],
        "company": record["inferred_company"],
        "project": record["inferred_project"],
        "product": record["inferred_product"],
        "sensitivity": record["sensitivity"],
        "primary_destination": record["primary_destination"],
        "secondary_destination": record["secondary_destination"],
        "action_taken": record["action_taken"],
        "approval_required": record["approval_required"],
        "routing_confidence": record["routing_confidence"],
        "status": record["status"],
    }


def classify_and_route(req: IntakeRequest) -> tuple[dict, dict, dict]:
    raw_text = _joined_request_text(req)
    redacted_content, content_secret_types = redact_secrets(req.content)
    redacted_text, secret_types = redact_secrets(raw_text)
    secret_types.update(content_secret_types)

    text_lower = raw_text.lower()
    redacted_text_lower = redacted_text.lower()
    inferred_project = _infer_project(req, text_lower)
    inferred_product = _infer_product(req, inferred_project)
    inferred_company = _infer_company(req, text_lower)
    stored_company = _redact_optional(inferred_company)
    stored_project = _redact_optional(inferred_project)
    stored_product = _redact_optional(inferred_product)

    record = {
        "intake_id": f"intake_{uuid4().hex}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": _redact_optional(req.source) or "unknown",
        "submitted_by": _redact_optional(req.submitted_by) or "unknown",
        "content_type": _redact_optional(req.content_type) or "text",
        "classification": "general_intake",
        "inferred_company": stored_company,
        "inferred_project": stored_project,
        "inferred_product": stored_product,
        "sensitivity": (_redact_optional(req.sensitivity) or "NORMAL").upper(),
        "primary_destination": "VaultSpace / documents",
        "secondary_destination": None,
        "requested_action": _redact_optional(req.requested_action),
        "action_taken": "routed_to_vaultspace_documents",
        "approval_required": False,
        "routing_confidence": 0.55,
        "status": "routed",
        "tags": _redact_tags(req.tags),
        "content": redacted_content,
    }

    if secret_types:
        record.update(
            {
                "classification": "secret_or_credential",
                "sensitivity": "SECRET",
                "primary_destination": "secret_manager_required",
                "secondary_destination": "audit_log",
                "action_taken": "redacted_and_quarantined",
                "approval_required": True,
                "routing_confidence": 1.0,
                "status": "quarantined",
                "detected_secret_types": sorted(secret_types),
            }
        )
        return record, _build_audit_record(record), _build_receipt(record)

    if _has_any(
        redacted_text_lower,
        (
            "founder-private",
            "founder only",
            "founder-only",
            "private founder",
            "must not be available to staff",
            "not be available to staff",
            "personal financial",
            "confidential communication",
            "restricted project",
        ),
    ):
        record.update(
            {
                "classification": "founder_private_note",
                "sensitivity": "FOUNDER_ONLY",
                "primary_destination": "Founder Private Vault",
                "secondary_destination": None,
                "action_taken": "routed_to_founder_private_vault",
                "approval_required": True,
                "routing_confidence": 0.94,
            }
        )
    elif _has_any(redacted_text_lower, ("assign ", "assigned ", "assignment", "design team", "staff task", "to the team")):
        record.update(
            {
                "classification": "staff_task",
                "primary_destination": "VaultSpace / tasks",
                "secondary_destination": f"{stored_project} project workflow" if stored_project else "matching project workflow",
                "action_taken": "routed_to_tasks",
                "approval_required": False,
                "routing_confidence": 0.88,
            }
        )
    elif _has_any(
        redacted_text_lower,
        (" bug", "500 error", " error", "exception", "failing", "fails", "failed", "broken", "crash", "checkout returns"),
    ):
        record.update(
            {
                "classification": "technical_bug",
                "primary_destination": f"{stored_project} project issue queue" if stored_project else "matching project issue queue",
                "secondary_destination": "VaultSpace / incidents",
                "action_taken": "routed_to_project_issue_queue",
                "approval_required": False,
                "routing_confidence": 0.9,
            }
        )
    elif _has_any(
        redacted_text_lower,
        ("product idea", "feature idea", " should ", " should compare", "display every change", "new feature", "improve"),
    ):
        record.update(
            {
                "classification": "product_feature_idea",
                "primary_destination": "VaultSpace / ideas",
                "secondary_destination": f"{stored_project} product backlog" if stored_project else "matching project backlog",
                "action_taken": "routed_to_ideas_and_backlog",
                "approval_required": True,
                "routing_confidence": 0.86,
            }
        )
    elif _has_any(redacted_text_lower, ("founder decision", "i decided", "decision:", "approved", "must now", "must become")):
        record.update(
            {
                "classification": "founder_decision",
                "primary_destination": "VaultSpace / decisions",
                "secondary_destination": "VaultSpace / audit_log",
                "action_taken": "routed_to_decisions_and_audit_log",
                "approval_required": False,
                "routing_confidence": 0.84,
            }
        )
    elif _has_any(redacted_text_lower, ("research", "investigate", "market", "competitor")):
        record.update(
            {
                "classification": "research_note",
                "primary_destination": "VaultSpace / research",
                "secondary_destination": None,
                "action_taken": "routed_to_research",
                "approval_required": False,
                "routing_confidence": 0.72,
            }
        )

    return record, _build_audit_record(record), _build_receipt(record)
