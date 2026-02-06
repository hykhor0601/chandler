"""Web search tool using DuckDuckGo."""

from chandler.tools import tool


@tool(name="web_search", description="Search the web using DuckDuckGo. Returns a list of search results with titles, URLs, and snippets.")
def web_search(query: str, max_results: int = 5) -> str:
    """
    Args:
        query: The search query string
        max_results: Maximum number of results to return (default 5)
    """
    try:
        from duckduckgo_search import DDGS

        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(f"**{r['title']}**\n{r['href']}\n{r['body']}\n")

        if not results:
            return "No results found."
        return "\n".join(results)
    except Exception as e:
        return f"Search error: {e}"
