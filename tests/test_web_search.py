"""Tests for web search (open_notebook/utils/web_search.py, api/routers/web_search.py)."""

import httpx
import pytest
from fastapi.testclient import TestClient

from open_notebook.exceptions import ExternalServiceError
from open_notebook.utils import web_search as ws


@pytest.fixture
def client():
    from api.main import app

    return TestClient(app)


SEARXNG_ANSWER = {
    "query": "rybník",
    "results": [
        {
            "url": "https://cs.wikipedia.org/wiki/Rybn%C3%ADk",
            "title": "Rybník – Wikipedie",
            "content": "Rybník je   umělá vodní nádrž\n určená k chovu ryb.",
            "engine": "wikipedia",
        },
        {"url": "https://cs.wikipedia.org/wiki/Rybn%C3%ADk", "title": "duplicate"},
        {"url": "javascript:alert(1)", "title": "bad scheme"},
        {"url": "ftp://example.com/file", "title": "ftp"},
        {
            "url": "https://example.com/a",
            "title": "",
            "content": None,
            "publishedDate": "2026-01-02",
        },
        "not a dict",
    ],
}


class TestParse:
    def test_keeps_http_urls_deduplicates_and_cleans(self):
        results = ws.parse_searxng_results(SEARXNG_ANSWER)
        assert [r.url for r in results] == [
            "https://cs.wikipedia.org/wiki/Rybn%C3%ADk",
            "https://example.com/a",
        ]
        assert results[0].snippet == "Rybník je umělá vodní nádrž určená k chovu ryb."
        assert results[0].engine == "wikipedia"
        # Empty title falls back to the URL
        assert results[1].title == "https://example.com/a"
        assert results[1].published_date == "2026-01-02"

    def test_limit(self):
        assert len(ws.parse_searxng_results(SEARXNG_ANSWER, limit=1)) == 1

    @pytest.mark.parametrize("payload", [None, [], {"results": "x"}, {}])
    def test_unexpected_payload(self, payload):
        with pytest.raises(ExternalServiceError):
            ws.parse_searxng_results(payload)


class TestConfiguration:
    def test_not_configured(self, monkeypatch):
        monkeypatch.delenv(ws.WEB_SEARCH_URL_ENV, raising=False)
        assert ws.web_search_configured() is False

    def test_trailing_slash_stripped(self, monkeypatch):
        monkeypatch.setenv(ws.WEB_SEARCH_URL_ENV, " http://searxng:8080/ ")
        assert ws.web_search_url() == "http://searxng:8080"


def _mock_searxng(monkeypatch, handler):
    real_client = httpx.AsyncClient

    def factory(*args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(handler)
        return real_client(*args, **kwargs)

    monkeypatch.setattr(ws.httpx, "AsyncClient", factory)


class TestEndpoint:
    def test_not_configured_returns_422(self, client, monkeypatch):
        monkeypatch.delenv(ws.WEB_SEARCH_URL_ENV, raising=False)
        response = client.get("/api/web-search", params={"q": "rybník"})
        assert response.status_code == 422

    def test_success_passes_query_and_language(self, client, monkeypatch):
        monkeypatch.setenv(ws.WEB_SEARCH_URL_ENV, "http://searxng:8080")
        seen = {}

        def handler(request: httpx.Request) -> httpx.Response:
            seen["url"] = str(request.url)
            seen["params"] = dict(request.url.params)
            return httpx.Response(200, json=SEARXNG_ANSWER)

        _mock_searxng(monkeypatch, handler)
        response = client.get(
            "/api/web-search", params={"q": " rybník ", "language": "cs"}
        )
        assert response.status_code == 200
        body = response.json()
        assert body["query"] == "rybník"
        assert len(body["results"]) == 2
        assert seen["url"].startswith("http://searxng:8080/search?")
        assert seen["params"]["format"] == "json"
        assert seen["params"]["q"] == "rybník"
        assert seen["params"]["language"] == "cs"

    def test_json_format_disabled_returns_502(self, client, monkeypatch):
        monkeypatch.setenv(ws.WEB_SEARCH_URL_ENV, "http://searxng:8080")
        _mock_searxng(
            monkeypatch, lambda request: httpx.Response(403, text="Forbidden")
        )
        response = client.get("/api/web-search", params={"q": "rybník"})
        assert response.status_code == 502

    def test_unreachable_returns_502(self, client, monkeypatch):
        monkeypatch.setenv(ws.WEB_SEARCH_URL_ENV, "http://searxng:8080")

        def handler(request):
            raise httpx.ConnectError("boom", request=request)

        _mock_searxng(monkeypatch, handler)
        response = client.get("/api/web-search", params={"q": "rybník"})
        assert response.status_code == 502

    @pytest.mark.parametrize(
        "params",
        [
            {"q": ""},
            {"q": "x" * 301},
            {"q": "a", "language": "cs;drop"},
            {"q": "a", "page": 0},
        ],
    )
    def test_invalid_input_rejected(self, client, monkeypatch, params):
        monkeypatch.setenv(ws.WEB_SEARCH_URL_ENV, "http://searxng:8080")
        response = client.get("/api/web-search", params=params)
        assert response.status_code == 422

    def test_capabilities_report_web_search(self, client, monkeypatch):
        monkeypatch.setenv(ws.WEB_SEARCH_URL_ENV, "http://searxng:8080")
        assert client.get("/api/capabilities").json()["web_search_available"] is True
        monkeypatch.delenv(ws.WEB_SEARCH_URL_ENV)
        assert client.get("/api/capabilities").json()["web_search_available"] is False
