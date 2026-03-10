from tavily import TavilyClient

from app.config import settings


def search(query: str, max_results: int | None = None) -> list[dict]:
    n = max_results or settings.search_results_per_query
    response = TavilyClient(api_key=settings.tavily_api_key).search(query=query, max_results=n)
    return [
        {"title": r.get("title", ""), "url": r.get("url", ""), "content": r.get("content", ""), "query": query}
        for r in response.get("results", [])
    ]
