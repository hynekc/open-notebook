"""
Web Search Router

Finds candidate sources on the web through the operator-configured SearXNG
instance (``OPEN_NOTEBOOK_WEB_SEARCH_URL``). The router only returns result
metadata; the UI adds the URLs the user picks as ordinary link sources.

Endpoints:
- GET /web-search?q=... - Search the web
"""

from typing import Optional

from fastapi import APIRouter, Query

from api.models import WebSearchResponse, WebSearchResultResponse
from open_notebook.utils.web_search import MAX_QUERY_LENGTH, MAX_RESULTS, search_web

router = APIRouter(prefix="/web-search", tags=["web-search"])


@router.get("", response_model=WebSearchResponse)
async def web_search(
    q: str = Query(
        ..., min_length=1, max_length=MAX_QUERY_LENGTH, description="Search query"
    ),
    language: Optional[str] = Query(
        None,
        max_length=16,
        pattern=r"^[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})?$|^all$|^auto$",
        description="Result language for the search engine, e.g. cs or cs-CZ",
    ),
    page: int = Query(1, ge=1, le=10, description="Result page"),
    limit: int = Query(
        20, ge=1, le=MAX_RESULTS, description="Maximum number of results"
    ),
):
    """Search the web for new sources. Typed errors map to 400 / 422 / 502."""
    results = await search_web(q, language=language, page=page, limit=limit)
    return WebSearchResponse(
        query=q.strip(),
        results=[
            WebSearchResultResponse(
                title=r.title,
                url=r.url,
                snippet=r.snippet,
                engine=r.engine,
                published_date=r.published_date,
            )
            for r in results
        ],
    )
