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
    # ── Aggregators / Marketplaces ────────────────────────────────────
    ("https://coursehorse.com/nyc/classes", "CourseHorse — all classes"),
    ("https://coursehorse.com/nyc/classes/cooking", "CourseHorse — cooking"),
    ("https://coursehorse.com/nyc/classes/art", "CourseHorse — art"),
    ("https://coursehorse.com/nyc/classes/crafts", "CourseHorse — crafts"),
    ("https://coursehorse.com/nyc/classes/music", "CourseHorse — music"),
    ("https://coursehorse.com/nyc/classes/dance", "CourseHorse — dance"),
    ("https://coursehorse.com/nyc/classes/fitness", "CourseHorse — fitness"),
    ("https://coursehorse.com/nyc/classes/photography", "CourseHorse — photography"),
    ("https://classbento.com/new-york", "ClassBento — NYC"),
    ("https://classbento.com/new-york/cooking-classes", "ClassBento — cooking"),
    ("https://classbento.com/new-york/pottery-classes", "ClassBento — pottery"),
    ("https://classbento.com/new-york/art-classes", "ClassBento — art"),
    ("https://classbento.com/new-york/candle-making-classes", "ClassBento — candle making"),
    ("https://classbento.com/new-york/woodworking-classes", "ClassBento — woodworking"),
    ("https://classbento.com/new-york/sewing-classes", "ClassBento — sewing"),
    ("https://www.eventbrite.com/d/ny--new-york/classes--workshops/", "Eventbrite — classes & workshops"),
    ("https://www.eventbrite.com/d/ny--new-york/cooking-classes/", "Eventbrite — cooking"),
    ("https://www.eventbrite.com/d/ny--new-york/art-classes/", "Eventbrite — art"),
    ("https://www.eventbrite.com/d/ny--new-york/music-classes/", "Eventbrite — music"),
    ("https://www.eventbrite.com/d/ny--new-york/crafts-classes/", "Eventbrite — crafts"),
    ("https://www.dabble.co/new-york", "Dabble — NYC"),
    ("https://www.airbnb.com/s/New-York--NY/experiences", "Airbnb Experiences — NYC"),
    ("https://www.meetup.com/find/?location=us--ny--New+York&source=EVENTS&categoryId=546", "Meetup — arts & crafts NYC"),
    ("https://www.meetup.com/find/?location=us--ny--New+York&source=EVENTS&categoryId=530", "Meetup — cooking NYC"),

    # ── Major NYC Institutions ────────────────────────────────────────
    ("https://www.92ny.org/classes", "92nd Street Y — classes"),
    ("https://www.brooklynbrainery.com/courses", "Brooklyn Brainery — courses"),
    ("https://www.nycgovparks.org/programs", "NYC Parks — programs"),
    ("https://www.nycgovparks.org/programs/recreation", "NYC Parks — recreation"),
    ("https://www.nypl.org/events/classes", "NYPL — classes"),
    ("https://www.bklynlibrary.org/calendar", "Brooklyn Public Library — events"),

    # ── Museum Workshops ──────────────────────────────────────────────
    ("https://www.moma.org/calendar/programs", "MoMA — programs"),
    ("https://www.metmuseum.org/events/programs", "Met Museum — programs"),
    ("https://www.brooklynmuseum.org/education/adult", "Brooklyn Museum — adult education"),
    ("https://madmuseum.org/programs", "MAD Museum — programs"),
    ("https://www.guggenheim.org/plan-your-visit/classes-and-workshops", "Guggenheim — workshops"),

    # ── Cooking & Food ────────────────────────────────────────────────
    ("https://www.murrayscheese.com/classes", "Murray's Cheese — classes"),
    ("https://www.eataly.com/us_en/stores/nyc-flatiron/nyc-flatiron-cooking-classes", "Eataly Flatiron — cooking"),
    ("https://www.ice.edu/new-york/recreational-classes", "ICE — recreational classes"),
    ("https://www.thebrooklynkitchen.com/pages/classes", "Brooklyn Kitchen — classes"),
    ("https://www.degustibusnyc.com/upcoming-classes", "De Gustibus — cooking classes"),
    ("https://www.homecookingny.com/schedule", "Home Cooking NY — schedule"),
    ("https://www.tastebudsnyc.com/classes", "Taste Buds Kitchen — classes"),
    ("https://www.hipcooks.com/new-york-city/", "Hipcooks — NYC"),
    ("https://www.sur-la-table.com/cooking-classes?storeId=576", "Sur La Table — NYC classes"),
    ("https://www.mokedsbrooklynbagel.com/classes", "Mokeds Brooklyn Bagel — classes"),

    # ── Cocktails / Wine / Spirits ────────────────────────────────────
    ("https://www.mixologynyc.com/classes", "Mixology NYC — classes"),
    ("https://www.nycwineclass.com/classes", "NYC Wine Class — classes"),
    ("https://www.theurbangrape.com/pages/events", "Urban Grape — events"),

    # ── Pottery / Ceramics ────────────────────────────────────────────
    ("https://www.bfrnt.com/classes", "BKLYN Clay — classes"),
    ("https://www.greenwichhouse.org/pottery/", "Greenwich House Pottery — classes"),
    ("https://www.mudsharks.com/classes", "MudShark Studios — classes"),
    ("https://www.thewheelbrooklyn.com/classes", "The Wheel Brooklyn — classes"),
    ("https://www.claybykats.com/classes", "Clay by Kats — classes"),

    # ── Art / Painting / Drawing ──────────────────────────────────────
    ("https://www.paintloungenyc.com/classes", "Paint Lounge NYC — classes"),
    ("https://www.artstudentsleague.org/classes", "Art Students League — classes"),
    ("https://www.paintandpour.com/nyc", "Paint & Pour — NYC"),
    ("https://www.moishestreehouse.com/calendar", "Moishe's Treehouse — calendar"),

    # ── Woodworking / Makers ──────────────────────────────────────────
    ("https://www.makeville.com/classes", "Makeville Studio — woodworking"),
    ("https://www.brooklynshopclass.com/classes", "Brooklyn Shop Class — classes"),

    # ── Glass / Jewelry / Metalwork ───────────────────────────────────
    ("https://www.urbanglass.org/classes", "UrbanGlass — classes"),
    ("https://www.brooklynglass.com/classes", "Brooklyn Glass — classes"),
    ("https://www.92y.org/jewelry", "92Y — jewelry classes"),

    # ── Textile / Sewing / Fashion ────────────────────────────────────
    ("https://www.textileartscenter.com/classes", "Textile Arts Center — classes"),
    ("https://www.bfrnt.com/sewing-classes", "BKLYN Sewing — classes"),
    ("https://www.gothamquilts.com/classes", "Gotham Quilts — classes"),

    # ── Screen Printing / Letterpress ─────────────────────────────────
    ("https://www.swinyc.com/workshops", "School of Visual Arts — workshops"),
    ("https://www.bowneprinters.org/workshops", "Bowne & Co Printers — workshops"),

    # ── Candle / Soap / Perfume ───────────────────────────────────────
    ("https://www.candlemaking.com/new-york-classes", "NYC Candle Making — classes"),
    ("https://www.olfactorynyc.com/workshops", "Olfactory NYC — perfume workshops"),

    # ── Dance ─────────────────────────────────────────────────────────
    ("https://www.broadwaydancecenter.com/schedule", "Broadway Dance Center — schedule"),
    ("https://www.pericet.com/classes", "Pericet — flamenco classes"),
    ("https://www.alvinailey.org/extension/classes", "Alvin Ailey — extension classes"),
    ("https://www.gibneydance.org/take-class/", "Gibney Dance — classes"),
    ("https://www.dfrnyc.com/schedule", "DanceFit Revolution — schedule"),

    # ── Music ─────────────────────────────────────────────────────────
    ("https://www.nycsgt.com/group-classes", "NYC School of Guitar — classes"),
    ("https://www.nyssma.org/programs/", "NYSSMA — programs"),

    # ── Writing / Improv / Comedy ─────────────────────────────────────
    ("https://www.gothamwritersworkshop.com/classes", "Gotham Writers — writing"),
    ("https://www.nycimprov.com/classes", "NYC Improv — classes"),
    ("https://ucbcomedy.com/classes", "UCB — improv classes"),
    ("https://www.pitnyc.com/classes", "PIT NYC — classes"),
    ("https://www.magnettheater.com/classes", "Magnet Theater — classes"),

    # ── Fitness / Wellness / Yoga ─────────────────────────────────────
    ("https://www.yogaworks.com/new-york/workshops/", "YogaWorks — NYC workshops"),
    ("https://www.sky-ting.com/schedule", "Sky Ting Yoga — schedule"),

    # ── Photography ───────────────────────────────────────────────────
    ("https://www.icp.org/school/continuing-education", "ICP — continuing education"),
    ("https://www.bfrnt.com/photography-classes", "BKLYN Photography — classes"),

    # ── Tech / Coding ─────────────────────────────────────────────────
    ("https://generalassemb.ly/locations/new-york-city", "General Assembly — NYC"),
    ("https://flatironschool.com/courses/", "Flatiron School — courses"),
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
