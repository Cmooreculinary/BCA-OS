import os
import tempfile

from fastapi.testclient import TestClient


_db = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
_db.close()
os.environ["SQLITE_PATH"] = _db.name
os.environ["CONRAD_ACCESS_TOKEN"] = "founder-test-access"
os.environ.pop("RENDER", None)

from mcp_bridge import app as production  # noqa: E402


def test_health_is_public_but_founder_surface_is_locked():
    with TestClient(production.app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["founder_access_configured"] is True

        root = client.get("/")
        assert root.status_code == 401
        assert "Founder Access" in root.text

        protected = client.get("/openapi.json")
        assert protected.status_code == 401


def test_unlock_uses_http_only_session_cookie():
    with TestClient(production.app) as client:
        rejected = client.post("/unlock", json={"token": "wrong"})
        assert rejected.status_code == 401

        accepted = client.post("/unlock", json={"token": "founder-test-access"})
        assert accepted.status_code == 200
        cookie = accepted.headers.get("set-cookie", "")
        assert production.COOKIE_NAME in cookie
        assert "HttpOnly" in cookie
        assert "founder-test-access" not in cookie

        root = client.get("/")
        assert root.status_code == 200
        assert "Talk to Conrad" in root.text


def test_bearer_access_supports_server_to_server_callers():
    with TestClient(production.app) as client:
        response = client.get(
            "/openapi.json",
            headers={"Authorization": "Bearer founder-test-access"},
        )
        assert response.status_code == 200
        assert "/conrad" in response.json()["paths"]


def test_conrad_prompt_is_catalog_grounded_and_has_no_retired_platform_reference():
    prompt = production.server._CONRAD_SYSTEM
    assert "canonical catalog" in prompt.lower()
    assert "Never invent" in prompt
    assert "third-party app platform" not in prompt
