from __future__ import annotations

from typing import List

from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel

from utils.logger import get_logger

logger = get_logger(__name__)

MODEL = "claude-sonnet-4-6"
BATCH_SIZE = 5

SYSTEM_PROMPT = """You are a class event link finder. You will receive raw web page content from a
search session. Your job is to extract hyperlinks that lead to individual class, workshop, or
skill-based experience detail pages.

INCLUDE links that:
- Lead to a single specific class, workshop, or lesson booking/detail page
  (e.g., Eventbrite class page, studio booking page, provider event detail page)
- Relate to: cooking, baking, art, pottery, ceramics, painting, yoga, dance, fitness, photography,
  language, mixology, wine, improv, calligraphy, crafts, jewelry making, floral arrangement,
  or any similar skill-based experience

EXCLUDE:
- Links to concerts, sports events, comedy shows, theatrical performances, films
- Links to general listings/category pages (e.g., "all classes in NYC")
- Navigation/utility links (home page, login, search, account, etc.)
- Links already provided in the "already fetched" list
- Duplicate links

Return ONLY a JSON array of URL strings. If no valid class links are found, return [].
"""


class LinkList(BaseModel):
    urls: List[str]


class LinkFinderAgent:
    def __init__(self):
        self._llm = ChatAnthropic(model=MODEL).with_structured_output(LinkList)

    def find_links(self, web_batch: list[dict], existing_urls: set[str]) -> list[str]:
        logger.info(f"LinkFinder scanning {len(web_batch)} pages in batches of {BATCH_SIZE}…")
        found_urls: set[str] = set()

        for batch_start in range(0, len(web_batch), BATCH_SIZE):
            batch = web_batch[batch_start: batch_start + BATCH_SIZE]
            urls_so_far = existing_urls | found_urls
            try:
                batch_urls = self._process_batch(batch, urls_so_far)
                found_urls.update(batch_urls)
            except Exception as e:
                logger.error(f"LinkFinder batch {batch_start}–{batch_start + BATCH_SIZE} failed: {e}")

        new_urls = [u for u in found_urls if u not in existing_urls]
        logger.info(f"LinkFinder found {len(new_urls)} new class URLs")
        return new_urls

    def _process_batch(self, batch: list[dict], already_fetched: set[str]) -> list[str]:
        already_list = "\n".join(sorted(already_fetched)[:200])
        pages_text = ""
        for record in batch:
            pages_text += f"\n\n---\nURL: {record.get('url', '')}\nCONTENT:\n{record.get('content', '')[:3000]}"

        user_message = (
            f"Already-fetched URLs (exclude these):\n{already_list}\n\n"
            f"Pages to scan:{pages_text}"
        )
        result: LinkList = self._llm.invoke(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ]
        )
        return result.urls or []
