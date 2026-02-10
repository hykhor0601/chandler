"""AI Tech News and GitHub Trending tool.

Fetches daily AI/ML news from multiple sources and trending GitHub projects.
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any

import requests
from bs4 import BeautifulSoup

from chandler.tools import tool


def _fetch_github_trending_ai() -> List[Dict[str, Any]]:
    """Fetch trending AI/ML repositories from GitHub.

    Returns:
        List of trending repos with name, description, stars, language
    """
    try:
        # GitHub trending page (no auth required)
        url = "https://github.com/trending"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        repos = []

        # Parse trending repos
        for article in soup.find_all("article", class_="Box-row")[:10]:
            try:
                # Repo name and link
                h2 = article.find("h2")
                if not h2:
                    continue

                link = h2.find("a")
                if not link:
                    continue

                repo_name = link.get("href", "").strip("/")

                # Description
                desc_p = article.find("p", class_="col-9")
                description = desc_p.text.strip() if desc_p else "No description"

                # Check if AI/ML related
                text = (repo_name + " " + description).lower()
                ai_keywords = [
                    "ai", "ml", "machine learning", "deep learning", "neural",
                    "llm", "gpt", "transformer", "diffusion", "gan", "rag",
                    "pytorch", "tensorflow", "keras", "opencv", "nlp",
                    "computer vision", "chatbot", "agent", "embedding"
                ]

                if any(keyword in text for keyword in ai_keywords):
                    # Stars today
                    stars_span = article.find("span", class_="d-inline-block float-sm-right")
                    stars_today = stars_span.text.strip() if stars_span else "N/A"

                    # Language
                    lang_span = article.find("span", itemprop="programmingLanguage")
                    language = lang_span.text.strip() if lang_span else "Unknown"

                    repos.append({
                        "name": repo_name,
                        "description": description[:150],
                        "stars_today": stars_today,
                        "language": language,
                        "url": f"https://github.com/{repo_name}"
                    })
            except Exception as e:
                continue

        return repos[:5]  # Top 5 AI/ML repos

    except Exception as e:
        return [{"error": f"Failed to fetch GitHub trending: {str(e)}"}]


def _fetch_hackernews_ai() -> List[Dict[str, Any]]:
    """Fetch AI-related stories from Hacker News.

    Returns:
        List of HN stories related to AI/ML
    """
    try:
        # Hacker News API - top stories
        top_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        response = requests.get(top_url, timeout=10)
        response.raise_for_status()
        story_ids = response.json()[:30]  # Top 30 stories

        stories = []
        ai_keywords = [
            "ai", "ml", "llm", "gpt", "claude", "openai", "anthropic",
            "machine learning", "deep learning", "neural", "transformer",
            "chatgpt", "copilot", "midjourney", "stable diffusion"
        ]

        for story_id in story_ids:
            try:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                story_response = requests.get(story_url, timeout=5)
                story_data = story_response.json()

                if not story_data or story_data.get("type") != "story":
                    continue

                title = story_data.get("title", "")
                url = story_data.get("url", "")

                # Check if AI related
                if any(keyword in title.lower() for keyword in ai_keywords):
                    stories.append({
                        "title": title,
                        "url": url,
                        "score": story_data.get("score", 0),
                        "comments": story_data.get("descendants", 0),
                        "time": datetime.fromtimestamp(story_data.get("time", 0)).strftime("%Y-%m-%d %H:%M")
                    })

                if len(stories) >= 5:
                    break

            except Exception:
                continue

        return stories

    except Exception as e:
        return [{"error": f"Failed to fetch Hacker News: {str(e)}"}]


def _fetch_papers_with_code() -> List[Dict[str, Any]]:
    """Fetch trending papers from Papers with Code.

    Returns:
        List of trending AI/ML papers
    """
    try:
        url = "https://paperswithcode.com/greatest"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        papers = []

        # Find paper cards
        for item in soup.find_all("div", class_="paper-card")[:5]:
            try:
                title_link = item.find("h1").find("a") if item.find("h1") else None
                if not title_link:
                    continue

                title = title_link.text.strip()
                paper_url = "https://paperswithcode.com" + title_link.get("href", "")

                # Abstract/description
                abstract = item.find("p", class_="item-strip-abstract")
                abstract_text = abstract.text.strip()[:200] if abstract else ""

                papers.append({
                    "title": title,
                    "abstract": abstract_text,
                    "url": paper_url
                })

            except Exception:
                continue

        return papers

    except Exception as e:
        return [{"error": f"Failed to fetch Papers with Code: {str(e)}"}]


def _format_news_report(
    github_repos: List[Dict[str, Any]],
    hn_stories: List[Dict[str, Any]],
    papers: List[Dict[str, Any]]
) -> str:
    """Format the news into a readable report.

    Args:
        github_repos: List of GitHub repos
        hn_stories: List of HN stories
        papers: List of papers

    Returns:
        Formatted news report
    """
    report = []
    report.append("# 🤖 Daily AI Tech News Report")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("")

    # GitHub Trending
    report.append("## 📈 Trending AI/ML GitHub Projects")
    report.append("")
    if github_repos and "error" not in github_repos[0]:
        for i, repo in enumerate(github_repos, 1):
            report.append(f"{i}. **{repo['name']}** ({repo['language']})")
            report.append(f"   {repo['description']}")
            report.append(f"   ⭐ {repo['stars_today']} stars today")
            report.append(f"   🔗 {repo['url']}")
            report.append("")
    else:
        report.append("   ⚠️  Could not fetch GitHub trending")
        report.append("")

    # Hacker News
    report.append("## 🔥 Hacker News - AI Stories")
    report.append("")
    if hn_stories and "error" not in hn_stories[0]:
        for i, story in enumerate(hn_stories, 1):
            report.append(f"{i}. **{story['title']}**")
            report.append(f"   👍 {story['score']} points | 💬 {story['comments']} comments | 🕐 {story['time']}")
            if story['url']:
                report.append(f"   🔗 {story['url']}")
            report.append("")
    else:
        report.append("   ⚠️  Could not fetch Hacker News")
        report.append("")

    # Papers
    report.append("## 📄 Trending AI Research Papers")
    report.append("")
    if papers and "error" not in papers[0]:
        for i, paper in enumerate(papers, 1):
            report.append(f"{i}. **{paper['title']}**")
            if paper['abstract']:
                report.append(f"   {paper['abstract']}")
            report.append(f"   🔗 {paper['url']}")
            report.append("")
    else:
        report.append("   ⚠️  Could not fetch Papers with Code")
        report.append("")

    report.append("---")
    report.append("💡 Tip: Ask me to explain any of these topics in detail!")

    return "\n".join(report)


@tool(
    name="get_ai_news",
    description="Get daily AI/ML tech news including trending GitHub projects, Hacker News stories, and research papers"
)
def get_ai_news(sources: str = "all") -> str:
    """Fetch daily AI tech news from multiple sources.

    Args:
        sources: Which sources to fetch from. Options:
                - "all" (default): All sources
                - "github": Only GitHub trending
                - "hackernews": Only Hacker News
                - "papers": Only research papers

    Returns:
        Formatted news report with AI/ML updates

    Example:
        get_ai_news()  # All sources
        get_ai_news(sources="github")  # Only GitHub
    """
    sources = sources.lower().strip()

    github_repos = []
    hn_stories = []
    papers = []

    if sources in ("all", "github"):
        github_repos = _fetch_github_trending_ai()

    if sources in ("all", "hackernews", "hn"):
        hn_stories = _fetch_hackernews_ai()

    if sources in ("all", "papers", "research"):
        papers = _fetch_papers_with_code()

    return _format_news_report(github_repos, hn_stories, papers)


@tool(
    name="search_github_ai",
    description="Search GitHub for AI/ML repositories by keywords"
)
def search_github_ai(query: str, sort: str = "stars") -> str:
    """Search GitHub for AI/ML repositories.

    Args:
        query: Search query (e.g., "llm", "computer vision", "rag")
        sort: Sort by "stars", "updated", or "forks" (default: stars)

    Returns:
        List of matching repositories with details
    """
    try:
        # GitHub search API (no auth needed for basic search)
        url = "https://api.github.com/search/repositories"
        params = {
            "q": f"{query} language:python",
            "sort": sort,
            "order": "desc",
            "per_page": 10
        }
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Chandler-AI-Assistant"
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        repos = data.get("items", [])

        if not repos:
            return f"No repositories found for query: {query}"

        result = []
        result.append(f"# 🔍 GitHub Search: {query}")
        result.append(f"Found {data.get('total_count', 0)} repositories (showing top 10)")
        result.append("")

        for i, repo in enumerate(repos, 1):
            result.append(f"{i}. **{repo['full_name']}**")
            result.append(f"   {repo['description'] or 'No description'}")
            result.append(f"   ⭐ {repo['stargazers_count']:,} stars | 🍴 {repo['forks_count']:,} forks")
            result.append(f"   📅 Updated: {repo['updated_at'][:10]}")
            result.append(f"   🔗 {repo['html_url']}")
            result.append("")

        return "\n".join(result)

    except Exception as e:
        return f"Error searching GitHub: {str(e)}"
