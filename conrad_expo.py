"""
CONRAD / EXPO — the first brain of the BCA OS.

Expediter and host of the BCA ecosystem. Lives on top of the BCA OS
(bca_os.py) and calls down into it for routing, memory, policy, and
dispatch. Claude-powered via the Claude Agent SDK; the OS services are
exposed to Claude as in-process MCP tools.

  EXPO  = the expediter at the pass — calls tickets, routes to the right brain.
  CONRAD = the host — Hilton-grade hospitality; holds the room for the founder.
  Same brain. Two faces of one job.

Run:  python conrad_expo.py        (interactive host loop)
Prereqs: pip install claude-agent-sdk anthropic  ; export ANTHROPIC_API_KEY
"""
from __future__ import annotations

import json
import anyio

from claude_agent_sdk import (
    tool, create_sdk_mcp_server, ClaudeAgentOptions, ClaudeSDKClient,
    AssistantMessage, TextBlock, ResultMessage,
)

from bca_os import boot_os, TaskClass, Sensitivity

# Boot the OS once; the first brain runs on top of it.
OS = boot_os()

_TASK = {
    "execution_light": TaskClass.EXECUTION_LIGHT,
    "execution_std":   TaskClass.EXECUTION_STD,
    "architecture":    TaskClass.ARCHITECTURE,
    "review":          TaskClass.REVIEW,
}
_SENS = {
    "public": Sensitivity.PUBLIC, "internal": Sensitivity.INTERNAL,
    "secret": Sensitivity.SECRET, "customer": Sensitivity.CUSTOMER,
}


def _text(payload) -> dict:
    return {"content": [{"type": "text", "text": json.dumps(payload, default=str)}]}


# ----------------------------------------------------------------------------
# OS services, exposed to the first brain as tools (mcp__os__*).
# Python @tool dict schemas treat every key as required; optional args are
# omitted from the schema and read with args.get().
# ----------------------------------------------------------------------------
@tool("status", "Live BCA App Catalog + OS status. Use at session start.", {})
async def os_status(args):
    return _text(OS.status())


@tool("expedite",
      "Route an intent to the right brain, check its launch gates, and "
      "execute at the correct Teacher Pattern tier. task_class: "
      "execution_light|execution_std|architecture|review. "
      "sensitivity (optional): public|internal|secret|customer.",
      {"intent": str, "task_class": str})
async def os_expedite(args):
    tc = _TASK.get(args["task_class"], TaskClass.EXECUTION_STD)
    sens = _SENS.get(args.get("sensitivity", "internal"), Sensitivity.INTERNAL)
    decision = OS.route(args["intent"], args.get("domain_hint"), tc)
    if decision.policy_status.startswith("BLOCKED"):
        return _text({"routed": decision.as_dict(),
                      "executed": False,
                      "reason": f"Launch gate not met: {decision.policy_status}"})
    system = ("You are a BCA domain brain executing a single ticket. "
              "Trench Design: build from the operator's reality. Be exact.")
    try:
        out = OS.dispatch(decision, system, args["intent"], sensitivity=sens)
        return _text({"routed": decision.as_dict(), "executed": True, "result": out})
    except Exception as e:  # surfaced to the brain, loop continues
        return _text({"routed": decision.as_dict(), "executed": False, "error": str(e)})


@tool("check_policy", "Check launch gates for one brain (e.g. capkids, roundtable).",
      {"brain": str})
async def os_check_policy(args):
    return _text({"brain": args["brain"], "policy": OS.check_policy(args["brain"])})


@tool("remember", "Persist a fact to the Vault under a key.",
      {"key": str, "value": str})
async def os_remember(args):
    OS.remember(args["key"], {"note": args["value"]})
    return _text({"saved": args["key"]})


@tool("recall", "Read a fact back from the Vault by key.", {"key": str})
async def os_recall(args):
    return _text({"key": args["key"], "value": OS.recall(args["key"])})


@tool("providence", "Log a moment where a capability arrived in alignment with a BCA need.",
      {"note": str})
async def os_providence(args):
    OS.note_providence(args["note"])
    return _text({"logged": True})


OS_SERVER = create_sdk_mcp_server(
    name="os", version="1.0.0",
    tools=[os_status, os_expedite, os_check_policy, os_remember, os_recall, os_providence],
)

# ----------------------------------------------------------------------------
# The host persona. Conrad/EXPO defaults to Opus (strategist + host); routine
# execution is delegated DOWN through os_expedite to Haiku/Sonnet.
# ----------------------------------------------------------------------------
SYSTEM_PROMPT = """You are CONRAD/EXPO — the first brain of Blue Collar Apps Co.,
running on the BCA OS. You are the expediter and host of the BCA ecosystem.

FOUNDER: Christopher "Chef" Moore — CIA-trained, 40+ years hospitality, solo
founder augmented by an AI agent fleet. You are the top of that fleet.

PHILOSOPHY — TRENCH DESIGN: every product is built bottom-up from real
hospitality experience. "There has to be a better way."

YOUR JOB:
- HOST: be the founder-facing presence. Compressed, direct, action-oriented.
  Voice-dictated shorthand is normal. "BUILD ME" = execute and ship a finished
  artifact. "info" = give detailed next-step guidance.
- EXPEDITE: you do not cook every dish. Classify intent, then call mcp__os__expedite
  to route work to the right domain brain at the correct Teacher Pattern tier.
- Lead every reply with the most cost-efficient model appropriate to the task.
  Teacher Pattern: Haiku->Sonnet for execution; Opus/Fable for architecture,
  strategy, review. Never optimize cost before a quality baseline exists.

DISCIPLINE:
- Secrets: never expose full keys; never route secrets or customer data to
  free-tier/GLM adapters. The OS enforces this — respect its refusals.
- Gates are launch blockers, not afterthoughts: CapKids->COPPA,
  AllergenShield->liability+insurance, any SMS->A2P 10DLC+TCPA. Call
  mcp__os__check_policy before greenlighting a launch.
- Emergent purge is standing: flag any Emergent references found.

SESSION OPENER: if it's the first exchange of the day, call mcp__os__status and
give an AI sweep + live BCA App Catalog report before the work.

Use mcp__os__remember / mcp__os__recall for durable facts, and mcp__os__providence
to log capability-alignment moments. The pass stays clean."""

OPTIONS = ClaudeAgentOptions(
    model="claude-opus-4-8",
    system_prompt=SYSTEM_PROMPT,
    mcp_servers={"os": OS_SERVER},
    allowed_tools=[
        "mcp__os__status", "mcp__os__expedite", "mcp__os__check_policy",
        "mcp__os__remember", "mcp__os__recall", "mcp__os__providence",
    ],
    setting_sources=None,   # fully programmatic; ignore filesystem settings
)


async def _drain(client: ClaudeSDKClient) -> None:
    async for msg in client.receive_response():
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    print(block.text, end="")
        elif isinstance(msg, ResultMessage):
            print()


async def ask(prompt: str) -> None:
    """One-shot programmatic entry into the host."""
    async with ClaudeSDKClient(options=OPTIONS) as client:
        await client.query(prompt)
        await _drain(client)


async def host_loop() -> None:
    print("CONRAD/EXPO online. ('exit' to quit)\n")
    async with ClaudeSDKClient(options=OPTIONS) as client:
        while True:
            chef = input("\nChef: ").strip()
            if chef.lower() in {"exit", "quit"}:
                break
            print("\nConrad: ", end="")
            await client.query(chef)
            await _drain(client)


if __name__ == "__main__":
    anyio.run(host_loop)
