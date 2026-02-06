"""Web browsing tool: fetch and parse web pages."""

from chandler.tools import tool


@tool(name="web_browse", description="Fetch a web page and extract its text content. Useful for reading articles, documentation, or any web page.")
def web_browse(url: str) -> str:
    """
    Args:
        url: The full URL to fetch (e.g. https://example.com)
    """
    try:
        import requests
        from bs4 import BeautifulSoup

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove script and style elements
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)

        # Collapse multiple newlines
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        text = "\n".join(lines)

        # Truncate if too long
        if len(text) > 8000:
            text = text[:8000] + "\n\n[...truncated]"

        return text
    except Exception as e:
        return f"Error fetching {url}: {e}"
