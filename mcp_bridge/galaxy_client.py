from __future__ import annotations

"""
Galaxy client — read/query layer for NotebookLM notebooks.

NotebookLM does not expose a public write API; Conrad only reads from Galaxies.
Current method (2026): Google's Notebook Guide REST API via google-generativeai
is not yet publicly stable. We use the closest available proxy:
  - The `google.generativeai` grounded generation with a corpus (Semantic Retrieval API)
    as a stand-in until a native NotebookLM MCP endpoint is released.

⚠️  Flag: if a native NotebookLM MCP server ships, replace this module entirely.
    Watch: https://github.com/google-deepmind/notebooklm or the MCP registry.
"""
import os
import httpx

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"


async def galaxy_query(question: str, notebook_id: str | None = None) -> dict:
    """
    Query a NotebookLM Galaxy (notebook) for a source-grounded answer.

    Returns:
        {
            "answer": str,
            "citations": list[{"source": str, "excerpt": str}],
            "grounded": bool,
        }

    If the Gemini Semantic Retrieval corpus is not configured, falls back to a
    plain Gemini call and marks grounded=False so the caller knows.
    """
    api_key = os.environ["GOOGLE_API_KEY"]
    nb_id = notebook_id or os.environ.get("NOTEBOOKLM_NOTEBOOK_ID", "")

    # Attempt grounded retrieval via corpus if notebook_id is a corpus resource name
    if nb_id.startswith("corpora/"):
        return await _grounded_corpus_query(question, nb_id, api_key)

    # Fallback: plain Gemini 1.5 Flash (cheap, fast) — ungrounded
    return await _plain_gemini_query(question, api_key)


async def _grounded_corpus_query(question: str, corpus_name: str, api_key: str) -> dict:
    url = f"{GEMINI_BASE}/models/gemini-1.5-flash:generateContent?key={api_key}"
    body = {
        "contents": [{"parts": [{"text": question}]}],
        "tools": [{"retrieval": {"vertexAiSearch": {"datastore": corpus_name}}}],
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, json=body)
        r.raise_for_status()
        data = r.json()

    candidate = data["candidates"][0]
    answer_text = candidate["content"]["parts"][0].get("text", "")
    citations = []
    for chunk in candidate.get("citationMetadata", {}).get("citationSources", []):
        citations.append({"source": chunk.get("uri", ""), "excerpt": ""})

    return {"answer": answer_text, "citations": citations, "grounded": True}


async def _plain_gemini_query(question: str, api_key: str) -> dict:
    url = f"{GEMINI_BASE}/models/gemini-1.5-flash:generateContent?key={api_key}"
    body = {"contents": [{"parts": [{"text": question}]}]}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, json=body)
        r.raise_for_status()
        data = r.json()

    answer_text = data["candidates"][0]["content"]["parts"][0].get("text", "")
    return {"answer": answer_text, "citations": [], "grounded": False}
