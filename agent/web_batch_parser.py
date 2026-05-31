from __future__ import annotations

from typing import List, Optional

from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel

from utils.logger import get_logger

logger = get_logger(__name__)

MODEL = "claude-sonnet-4-6"
BATCH_SIZE = 3

SYSTEM_PROMPT = """You are a class event data extraction specialist. For each web page provided,
extract all individual NYC class, workshop, or skill-based experience events mentioned.

Rules:
- Create a SEPARATE entry for each distinct class date/session found on a page.
- For recurring classes (e.g., same class offered multiple times on different dates),
  create one entry per session — all share the same event_title.
- Set event_type = "class" always. Skip concerts, sports, theater, comedy shows, films, and conferences.
- Only include events that are:
    - A class, workshop, lesson, or skill-based experience
    - Clearly located in New York City (any borough)
    - Has a specific date
- The `artist` field should contain the instructor's name, or if unknown, the name of the
  business/studio/provider running the class (e.g., "ICE - Institute of Culinary Education",
  "Brooklyn Pottery", "The Wine School of Philadelphia").
- If a page has registration or booking links, populate tickets_source_1 with the booking URL and
  tickets_webpage_contents_1 with that page's content snippet. Otherwise use no_tickets_source_1.
- event_title format: "[Class Name] at [Venue/Provider]" (e.g., "Italian Pasta Making at Eataly NYC",
  "Wheel Throwing for Beginners at Brooklyn Pottery", "Mixology Masterclass at PKNY")
- date format: "MM-DD-YYYY" (e.g., "06-15-2026")
- start_time / end_time format: "00:00am" or "00:00pm" (e.g., "07:00pm")
- If the venue's full street address is visible anywhere on the page, populate the `address` field.
  Include the street number, street name, borough/city, state, and zip if available.
  If no street address is visible, leave `address` empty.
- If instructor/provider, venue, OR date cannot be confidently extracted, SKIP that entry.
- DO NOT set event_entry_id or entry_batch_id — leave them as empty strings "".
- For the `media_url` field: look for image markdown tags in the page content (format: ![alt](url)).
  Extract the URL of the most relevant image — prefer class photos, instructor headshots, studio images,
  or activity hero images. Skip navigation icons, logos under 100px, social media share buttons,
  tracking pixels, and ad banners. If no suitable image is found, leave media_url as null.
- Return a JSON object with key "entries" containing an array of EventEntry objects.
"""


class EventEntry(BaseModel):
    event_entry_id: str = ""
    entry_batch_id: str = ""
    event_title: str
    description: str
    artist: str          # instructor name or provider/studio name
    venue: str
    event_type: str = "class"
    multi_day_event: bool = False
    date: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    tickets_source_1: Optional[str] = None
    tickets_webpage_contents_1: Optional[str] = None
    tickets_source_2: Optional[str] = None
    tickets_webpage_contents_2: Optional[str] = None
    tickets_source_3: Optional[str] = None
    tickets_webpage_contents_3: Optional[str] = None
    tickets_source_4: Optional[str] = None
    tickets_webpage_contents_4: Optional[str] = None
    no_tickets_source_1: Optional[str] = None
    no_tickets_webpage_contents_1: Optional[str] = None
    no_tickets_source_2: Optional[str] = None
    no_tickets_webpage_contents_2: Optional[str] = None
    no_tickets_source_3: Optional[str] = None
    no_tickets_webpage_contents_3: Optional[str] = None
    no_tickets_source_4: Optional[str] = None
    no_tickets_webpage_contents_4: Optional[str] = None
    media_url: Optional[str] = None
    webpage_contents: Optional[str] = None
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class EntryList(BaseModel):
    entries: List[EventEntry]


class WebBatchParser:
    def __init__(self):
        self._llm = ChatAnthropic(model=MODEL).with_structured_output(EntryList)

    def parse(self, web_batch: list[dict]) -> list[EventEntry]:
        """Parse a full Web Batch into Class Event Entries, processing BATCH_SIZE pages per LLM call."""
        logger.info(f"WebBatchParser processing {len(web_batch)} pages in batches of {BATCH_SIZE}…")
        all_entries: list[EventEntry] = []

        for batch_start in range(0, len(web_batch), BATCH_SIZE):
            batch = web_batch[batch_start: batch_start + BATCH_SIZE]
            try:
                entries = self._parse_batch(batch)
                logger.info(
                    f"Batch {batch_start}–{batch_start + len(batch)}: parsed {len(entries)} entries"
                )
                all_entries.extend(entries)
            except Exception as e:
                logger.error(
                    f"WebBatchParser batch {batch_start}–{batch_start + len(batch)} failed: {e}"
                )

        logger.info(f"WebBatchParser total entries parsed: {len(all_entries)}")
        return all_entries

    def _parse_batch(self, batch: list[dict]) -> list[EventEntry]:
        pages_text = ""
        for record in batch:
            content_snippet = (record.get("content") or "")[:8000]
            pages_text += (
                f"\n\n---\n"
                f"PAGE URL: {record.get('url', '')}\n"
                f"QUERY USED: {record.get('query_used', '')}\n"
                f"CONTENT:\n{content_snippet}"
            )

        result: EntryList = self._llm.invoke(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Extract class event entries from these pages:{pages_text}"},
            ]
        )
        entries = result.entries or []
        for entry in entries:
            if not entry.webpage_contents:
                for record in batch:
                    if record.get("url"):
                        entry.webpage_contents = (record.get("content") or "")[:10000]
                        break
        return entries
