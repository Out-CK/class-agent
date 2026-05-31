"""
Seed Providers — curated list of known NYC class aggregators and studios.

These URLs are crawled directly each run (bypassing the search step) to ensure
high-yield class sources are always included in the web batch.
"""
from __future__ import annotations

import asyncio
from typing import Any

from tools.nimble_extract_tool import NimbleExtractTool
from utils.logger import get_logger

logger = get_logger(__name__)

CONCURRENCY_LIMIT = 5

# Each entry: (url, label) — label is for logging only.
SEED_URLS: list[tuple[str, str]] = [
    # --- Aggregators / Marketplaces ---
    ("https://coursehorse.com/nyc/classes", "CourseHorse — all classes"),
    ("https://coursehorse.com/nyc/classes/art", "CourseHorse — art"),
    ("https://coursehorse.com/nyc/classes/cooking", "CourseHorse — cooking"),
    ("https://coursehorse.com/nyc/classes/dance", "CourseHorse — dance"),
    ("https://coursehorse.com/nyc/classes/music", "CourseHorse — music"),
    ("https://coursehorse.com/nyc/classes/fitness", "CourseHorse — fitness"),
    ("https://coursehorse.com/nyc/classes/crafts", "CourseHorse — crafts"),
    ("https://classbento.com/new-york", "ClassBento — NYC"),
    ("https://classbento.com/new-york/pottery-classes", "ClassBento — pottery"),
    ("https://classbento.com/new-york/cooking-classes", "ClassBento — cooking"),
    ("https://classbento.com/new-york/candle-making-classes", "ClassBento — candle making"),
    ("https://classbento.com/new-york/painting-classes", "ClassBento — painting"),
    ("https://www.eventbrite.com/d/ny--new-york/classes--workshops/", "Eventbrite — classes & workshops"),
    ("https://www.eventbrite.com/d/ny--new-york/cooking-classes/", "Eventbrite — cooking"),
    ("https://www.eventbrite.com/d/ny--new-york/art-classes/", "Eventbrite — art"),
    ("https://www.eventbrite.com/d/ny--new-york/yoga-classes/", "Eventbrite — yoga"),
    ("https://www.eventbrite.com/d/ny--new-york/photography-classes/", "Eventbrite — photography"),
    ("https://www.dabble.co/new-york", "Dabble — NYC"),
    ("https://www.hisawyer.com/nyc", "Sawyer — NYC"),

    # --- Cooking Schools & Food ---
    ("https://www.eataly.com/us_en/stores/nyc-flatiron/nyc-flatiron-cooking-classes", "Eataly Flatiron — cooking"),
    ("https://www.eataly.com/us_en/stores/nyc-downtown/nyc-downtown-cooking-classes", "Eataly Downtown — cooking"),
    ("https://www.ice.edu/new-york/recreational-classes", "ICE — recreational classes"),
    ("https://www.murrayscheese.com/classes", "Murray's Cheese — classes"),
    ("https://www.thebkk.com/cooking-classes", "Brooklyn Kitchen — cooking"),
    ("https://www.dirtcandy.com/cooking-classes", "Dirt Candy — cooking"),
    ("https://www.nycwine.com/classes", "NYC Wine Company — classes"),

    # --- Art & Craft Studios ---
    ("https://www.bfriendsart.com/classes", "BFriends Art — classes"),
    ("https://www.paintlounge.com/new-york/classes", "Paint Lounge NYC — classes"),
    ("https://www.thewheelnyc.com/classes", "The Wheel NYC — pottery"),
    ("https://www.ceramicsclubbk.com/classes", "Ceramics Club BK — pottery"),
    ("https://www.mudmatter.com/classes", "Mud Matter — ceramics"),
    ("https://www.brooklynglass.com/classes", "Brooklyn Glass — glassblowing"),
    ("https://www.3rdwardbrooklyn.com/classes", "3rd Ward — maker classes"),

    # --- Fitness & Wellness ---
    ("https://www.ymcanyc.org/programs/health-fitness/group-exercise", "YMCA NYC — group classes"),

    # --- Creative & Other ---
    ("https://www.gothamwritersworkshop.com/classes", "Gotham Writers — writing"),
    ("https://www.photographyworkshopnyc.com/workshops", "Photography Workshop NYC"),
    ("https://www.nycimprov.com/classes", "NYC Improv — classes"),
]


async def crawl_seed_providers(
    extract_tool: NimbleExtractTool,
    existing_urls: set[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Crawl all seed provider URLs via Nimble Extract.
    Returns a list of dicts matching the web_batch format:
      {"url": ..., "content": ..., "query_used": "seed_provider"}
    Skips URLs already present in *existing_urls*.
    """
    existing_urls = existing_urls or set()
    to_crawl = [(url, label) for url, label in SEED_URLS if url not in existing_urls]
    logger.info(
        f"Seed Providers: {len(to_crawl)} URLs to crawl "
        f"({len(SEED_URLS) - len(to_crawl)} already fetched)"
    )

    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

    async def extract_one(url: str, label: str) -> dict[str, Any]:
        async with semaphore:
            loop = asyncio.get_event_loop()
            try:
                result = await loop.run_in_executor(
                    None, lambda: extract_tool._run(url)
                )
                status = "ok" if result.get("content") else "empty"
                logger.info(f"  Seed [{status}] {label}: {url}")
                return {
                    "url": result["url"],
                    "content": result.get("content"),
                    "query_used": "seed_provider",
                }
            except Exception as e:
                logger.error(f"  Seed [FAIL] {label}: {url} — {e}")
                return {"url": url, "content": None, "query_used": "seed_provider"}

    tasks = [extract_one(url, label) for url, label in to_crawl]
    results = await asyncio.gather(*tasks)
    successful = [r for r in results if r.get("content")]
    logger.info(f"Seed Providers: {len(successful)}/{len(to_crawl)} pages returned content")
    return successful
