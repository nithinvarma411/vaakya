"""
Web Operations Module
Handles web search operations without opening browser.
"""

import platform
from typing import Any, Dict, List, Optional

try:
    from ddgs import DDGS
except ImportError:
    DDGS = None  # type: ignore[assignment]

from src.app.config.settings import settings


class WebOperations:
    """Platform-aware web search operations."""

    # Use settings for constants
    @property
    def snippet_length(self) -> int:
        return settings.web_operations.SNIPPET_LENGTH

    @property
    def quick_answer_length(self) -> int:
        return settings.web_operations.QUICK_ANSWER_LENGTH

    def __init__(self) -> None:
        self.system = platform.system().lower()
        self._ddgs: Any = None

    def _get_ddgs(self) -> Any:
        """Get or create DDGS instance."""
        if DDGS is None:
            raise ImportError(
                "ddgs package not found. Please install with: pip install ddgs"
            )

        if self._ddgs is None:
            self._ddgs = DDGS()
        return self._ddgs

    def search_web(
        self, query: str, max_results: Optional[int] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Search the web for information."""
        try:
            if max_results is None:
                max_results = settings.web_operations.DEFAULT_MAX_RESULTS

            ddgs = self._get_ddgs()

            print(f"🔍 Searching web for: {query}")

            # Perform the search
            results = list(ddgs.text(query, max_results=max_results))

            if not results:
                print("❌ No search results found")
                return None

            print(f"✅ Found {len(results)} search results:")

            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_result = {
                    "title": result.get("title", "No title"),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", "No description"),
                }
                formatted_results.append(formatted_result)

                print(f"\n{i}. {formatted_result['title']}")
                print(f"   {formatted_result['url']}")
                print(
                    f"   {formatted_result['snippet'][: self.snippet_length]}{'...' if len(formatted_result['snippet']) > self.snippet_length else ''}"
                )

            return formatted_results

        except ImportError as e:
            print(f"❌ Search engine not available: {e}")
            return None
        except Exception as e:
            print(f"❌ Error performing web search: {e}")
            return None

    def search_news(
        self, query: str, max_results: Optional[int] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Search for news articles."""
        try:
            if max_results is None:
                max_results = settings.web_operations.DEFAULT_MAX_RESULTS

            ddgs = self._get_ddgs()

            print(f"📰 Searching news for: {query}")

            # Perform news search
            results = list(ddgs.news(query, max_results=max_results))

            if not results:
                print("❌ No news results found")
                return None

            print(f"✅ Found {len(results)} news results:")

            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_result = {
                    "title": result.get("title", "No title"),
                    "url": result.get("url", ""),
                    "snippet": result.get("body", "No description"),
                    "source": result.get("source", "Unknown"),
                    "date": result.get("date", ""),
                }
                formatted_results.append(formatted_result)

                print(f"\n{i}. {formatted_result['title']}")
                print(
                    f"   Source: {formatted_result['source']} | Date: {formatted_result['date']}"
                )
                print(f"   {formatted_result['url']}")
                print(
                    f"   {formatted_result['snippet'][: self.snippet_length]}{'...' if len(formatted_result['snippet']) > self.snippet_length else ''}"
                )

            return formatted_results

        except ImportError as e:
            print(f"❌ Search engine not available: {e}")
            return None
        except Exception as e:
            print(f"❌ Error performing news search: {e}")
            return None

    def search_images(
        self, query: str, max_results: Optional[int] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Search for images."""
        try:
            if max_results is None:
                max_results = settings.web_operations.DEFAULT_MAX_RESULTS

            ddgs = self._get_ddgs()

            print(f"🖼️ Searching images for: {query}")

            # Perform image search
            results = list(ddgs.images(query, max_results=max_results))

            if not results:
                print("❌ No image results found")
                return None

            print(f"✅ Found {len(results)} image results:")

            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_result = {
                    "title": result.get("title", "No title"),
                    "image_url": result.get("image", ""),
                    "thumbnail_url": result.get("thumbnail", ""),
                    "source": result.get("source", ""),
                    "width": result.get("width", 0),
                    "height": result.get("height", 0),
                }
                formatted_results.append(formatted_result)

                print(f"\n{i}. {formatted_result['title']}")
                print(
                    f"   Size: {formatted_result['width']}x{formatted_result['height']}"
                )
                print(f"   Image: {formatted_result['image_url']}")
                print(f"   Source: {formatted_result['source']}")

            return formatted_results

        except ImportError as e:
            print(f"❌ Search engine not available: {e}")
            return None
        except Exception as e:
            print(f"❌ Error performing image search: {e}")
            return None

    def search_videos(
        self, query: str, max_results: Optional[int] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Search for videos."""
        try:
            if max_results is None:
                max_results = settings.web_operations.DEFAULT_MAX_RESULTS

            ddgs = self._get_ddgs()

            print(f"📹 Searching videos for: {query}")

            # Perform video search
            results = list(ddgs.videos(query, max_results=max_results))

            if not results:
                print("❌ No video results found")
                return None

            print(f"✅ Found {len(results)} video results:")

            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_result = {
                    "title": result.get("title", "No title"),
                    "url": result.get("content", ""),
                    "thumbnail": result.get("thumbnail", ""),
                    "description": result.get("description", ""),
                    "publisher": result.get("publisher", ""),
                    "duration": result.get("duration", ""),
                }
                formatted_results.append(formatted_result)

                print(f"\n{i}. {formatted_result['title']}")
                print(
                    f"   Publisher: {formatted_result['publisher']} | Duration: {formatted_result['duration']}"
                )
                print(f"   {formatted_result['url']}")
                print(
                    f"   {formatted_result['description'][: self.snippet_length]}{'...' if len(formatted_result['description']) > self.snippet_length else ''}"
                )

            return formatted_results

        except ImportError as e:
            print(f"❌ Search engine not available: {e}")
            return None
        except Exception as e:
            print(f"❌ Error performing video search: {e}")
            return None

    def quick_answer(self, query: str) -> Optional[str]:
        """Get a quick answer for a query."""
        try:
            ddgs = self._get_ddgs()

            print(f"❓ Getting quick answer for: {query}")

            # Get search results and use the first one as a quick answer
            search_results = list(ddgs.text(query, max_results=1))
            if search_results:
                result = search_results[0]
                snippet = result.get("body", "")
                if snippet:
                    print(
                        f"✅ Quick answer: {snippet[: self.quick_answer_length]}{'...' if len(snippet) > self.quick_answer_length else ''}"
                    )
                    return snippet

            print("❌ No quick answer found")
            return None

        except ImportError as e:
            print(f"❌ Search engine not available: {e}")
            return None
        except Exception as e:
            print(f"❌ Error getting quick answer: {e}")
            return None
