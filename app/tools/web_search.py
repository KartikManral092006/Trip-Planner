import logging
import os

from dotenv import load_dotenv
from langchain_core.tools import tool
from tavily import TavilyClient

load_dotenv()

logger = logging.getLogger(__name__)

MAX_RESULTS = 3
MAX_CONTENT_CHARS = 500

if not os.getenv("TAVILY_API_KEY"):
    raise RuntimeError("TAVILY_API_KEY is missing. Add it to your .env file.")

tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


@tool
def web_search(query: str) -> list[dict]:
    """Search the web for travel information such as transport options,
    fares, hotels, attractions, and prices. Use a specific query that
    includes the place and, where useful, the month or year."""
    if not query.strip():
        return [{"error": "Query cannot be empty."}]

    try:
        response = tavily.search(query=query, max_results=MAX_RESULTS)
    except Exception as error:
        logger.exception("Tavily search failed")
        return [{"error": f"Search failed: {error}. Treat this information as unavailable."}]

    return [
        {
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "content": item.get("content", "")[:MAX_CONTENT_CHARS],
        }
        for item in response.get("results", [])
    ]