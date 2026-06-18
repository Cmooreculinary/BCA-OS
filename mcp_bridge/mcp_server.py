"""
MCP server definition — exposes Conrad's tools to any MCP client (Claude Code, n8n, etc.).
Run with: python mcp_server.py
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from galaxy_client import galaxy_query
from vaultspace import vault_write, vault_read_recent

server = Server("conrad-mcp-bridge")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="galaxy_query",
            description="Query a NotebookLM Galaxy for a source-grounded answer with citations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "The question to ask the Galaxy."},
                    "notebook_id": {"type": "string", "description": "Optional corpus resource name (corpora/...)."},
                },
                "required": ["question"],
            },
        ),
        Tool(
            name="vault_write",
            description="Write a result or lesson to VaultSpace (MongoDB). Returns inserted doc id.",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "content": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["source", "content"],
            },
        ),
        Tool(
            name="vault_read_recent",
            description="Return the most recent VaultSpace entries for context injection.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 10},
                },
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "galaxy_query":
        result = await galaxy_query(arguments["question"], arguments.get("notebook_id"))
        text = f"Answer: {result['answer']}\n\nGrounded: {result['grounded']}"
        if result["citations"]:
            text += "\n\nCitations:\n" + "\n".join(f"- {c['source']}" for c in result["citations"])
        return [TextContent(type="text", text=text)]

    if name == "vault_write":
        doc_id = await vault_write(
            arguments["source"], arguments["content"], arguments.get("tags", [])
        )
        return [TextContent(type="text", text=f"Inserted: {doc_id}")]

    if name == "vault_read_recent":
        entries = await vault_read_recent(arguments.get("limit", 10))
        text = "\n\n".join(
            f"[{e.get('ts', '')}] {e.get('source', '')}: {e.get('content', '')[:200]}"
            for e in entries
        )
        return [TextContent(type="text", text=text or "No entries.")]

    raise ValueError(f"Unknown tool: {name}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
