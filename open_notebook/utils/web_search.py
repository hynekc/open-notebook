"""Web search for finding new sources, backed by a self-hosted SearXNG.

The search engine is an operator setting, not a user one: the API talks only
to the SearXNG instance named in ``OPEN_NOTEBOOK_WEB_SEARCH_URL`` (for example
``http://searxng:8080``). Users never supply a URL here, so there is no
user-controlled outbound request; the result URLs are only handed back to the
browser, which adds the chosen ones as ordinary link sources (and those go
through the usual URL validation when they are processed).

SearXNG must have the ``json`` output format enabled (``search.formats`` in
its ``settings.yml``), otherwise it answers ``403 Forbidden``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlsplit

import httpx
from loguru import logger

from open_notebook.exceptions import (
    ConfigurationError,
    ExternalServiceError,
    InvalidInputError,
    NetworkError,
)

WEB_SEARCH_URL_ENV = "OPEN_NOTEBOOK_WEB_SEARCH_URL"
WEB_SEARCH_TIMEOUT_ENV = "OPEN_NOTEBOOK_WEB_SEARCH_TIMEOUT"
DEFAULT_TIMEOUT_SECONDS = 15.0
MAX_QUERY_LENGTH = 300
MAX_RESULTS = 30
MAX_SNIPPET_LENGTH = 500


@dataclass(frozen=True)
class WebSearchResult:
    title: str
    url: str
    snippet: str
    engine: str | None = None
    published_date: str | None = None


def web_search_url() -> str | None:
    """The configured SearXNG base URL, without a trailing slash, or None."""
    value = os.environ.get(WEB_SEARCH_URL_ENV, "").strip().rstrip("/")
    return value or None


def web_search_configured() -> bool:
    return web_search_url() is not None


def _timeout() -> float:
    raw = os.environ.get(WEB_SEARCH_TIMEOUT_ENV, "").strip()
    try:
        value = float(raw) if raw else DEFAULT_TIMEOUT_SECONDS
    except ValueError:
        return DEFAULT_TIMEOUT_SECONDS
    return value if value > 0 else DEFAULT_TIMEOUT_SECONDS


def _is_http_url(value: str) -> bool:
    try:
        parts = urlsplit(value)
    except ValueError:
        return False
    return parts.scheme in ("http", "https") and bool(parts.netloc)


def _clean(value: object, limit: int | None = None) -> str:
    text = " ".join(str(value or "").split())
    if limit is not None and len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return text


def parse_searxng_results(
    payload: object, limit: int = MAX_RESULTS
) -> list[WebSearchResult]:
    """Turn a SearXNG JSON answer into results: http(s) only, de-duplicated."""
    if not isinstance(payload, dict):
        raise ExternalServiceError("Unexpected answer from the search engine")
    raw_results = payload.get("results")
    if not isinstance(raw_results, list):
        raise ExternalServiceError("Unexpected answer from the search engine")

    results: list[WebSearchResult] = []
    seen: set[str] = set()
    for item in raw_results:
        if not isinstance(item, dict):
            continue
        url = str(item.get("url") or "").strip()
        if not _is_http_url(url) or url in seen:
            continue
        seen.add(url)
        engine = item.get("engine")
        published = item.get("publishedDate")
        results.append(
            WebSearchResult(
                title=_clean(item.get("title"), 300) or url,
                url=url,
                snippet=_clean(item.get("content"), MAX_SNIPPET_LENGTH),
                engine=str(engine) if engine else None,
                published_date=str(published) if published else None,
            )
        )
        if len(results) >= limit:
            break
    return results


async def search_web(
    query: str,
    language: str | None = None,
    page: int = 1,
    limit: int = MAX_RESULTS,
) -> list[WebSearchResult]:
    """Search the web through the configured SearXNG instance."""
    base_url = web_search_url()
    if base_url is None:
        raise ConfigurationError(
            f"Web search is not configured (set {WEB_SEARCH_URL_ENV})"
        )
    query = query.strip()
    if not query:
        raise InvalidInputError("Search query is empty")
    if len(query) > MAX_QUERY_LENGTH:
        raise InvalidInputError(
            f"Search query is longer than {MAX_QUERY_LENGTH} characters"
        )

    params: dict[str, str | int] = {
        "q": query,
        "format": "json",
        "pageno": max(1, min(page, 10)),
        "safesearch": 1,
    }
    if language:
        params["language"] = language

    try:
        # The search engine is an internal service (compose network), so the
        # outbound proxy settings of the container are not used for it.
        async with httpx.AsyncClient(timeout=_timeout(), trust_env=False) as client:
            response = await client.get(f"{base_url}/search", params=params)
    except httpx.TimeoutException as e:
        raise NetworkError("The search engine did not answer in time") from e
    except httpx.HTTPError as e:
        logger.warning(f"Web search request failed: {type(e).__name__}")
        raise NetworkError("The search engine is not reachable") from e

    if response.status_code == 403:
        raise ExternalServiceError(
            "The search engine refused the request (is the JSON format enabled in SearXNG?)"
        )
    if response.status_code != 200:
        raise ExternalServiceError(
            f"The search engine answered with HTTP {response.status_code}"
        )
    try:
        payload = response.json()
    except ValueError as e:
        raise ExternalServiceError("Unexpected answer from the search engine") from e
    return parse_searxng_results(payload, limit=max(1, min(limit, MAX_RESULTS)))
