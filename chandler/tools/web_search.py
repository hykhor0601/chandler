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
        # Use new ddgs package (renamed from duckduckgo_search)
        try:
            from ddgs import DDGS
        except ImportError:
            # Fallback to old package name for backward compatibility
            from duckduckgo_search import DDGS

        results = []

        # Try with timeout and better error handling
        with DDGS() as ddgs:
            search_results = ddgs.text(
                query,
                max_results=max_results,
                backend="api"  # Use API backend for better reliability
            )

            for r in search_results:
                results.append(f"**{r['title']}**\n{r['href']}\n{r['body']}\n")

        if not results:
            return "No results found. This could be due to rate limiting or connectivity issues. Try:\n- Using a more specific query\n- Waiting a moment and trying again\n- Using web_browse to visit a specific URL directly"

        return "\n".join(results)

    except ImportError as e:
        return f"Search error: Missing ddgs package. Run: pip install ddgs\nDetails: {e}"
    except Exception as e:
        return f"Search error: {e}\n\nTip: If searches consistently fail, try:\n- More specific queries\n- Using web_browse to visit known URLs\n- Checking internet connection"
