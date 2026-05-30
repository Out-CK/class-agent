from __future__ import annotations

from typing import List, Literal

from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel

from utils.logger import get_logger

logger = get_logger(__name__)

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are an expert at generating search queries to find upcoming NYC class events.
Your task is to produce exactly 40 search queries that will surface the widest possible range of
upcoming classes, workshops, and skill-based experiences in New York City.

Rules:
- Generate EXACTLY 40 queries — no more, no fewer.
- Each query must have a query_type of "broad" or "niche".
- Broad queries (~15): General searches like "upcoming classes NYC this week",
  "workshops NYC this month", "things to learn in NYC 2026", "NYC skill classes for adults",
  "best cooking classes NYC", "creative workshops NYC".
- Niche queries (~25): Category-specific or provider-specific. Must include dedicated queries
  for each of these categories and providers:
    FOOD & DRINK: cooking classes NYC, baking classes NYC, sushi making class NYC,
      pasta making class NYC, mixology class NYC, wine tasting class NYC,
      cheese making class NYC, bread baking workshop NYC, knife skills class NYC
    ART & CRAFT: pottery class NYC, ceramics class NYC, painting class NYC,
      drawing class NYC, floral arrangement class NYC, candle making class NYC,
      leather working class NYC, jewelry making class NYC
    FITNESS & WELLNESS: yoga workshop NYC, meditation class NYC, dance class NYC,
      salsa class NYC, aerial yoga class NYC, pilates workshop NYC
    OTHER: photography class NYC, improv class NYC, calligraphy class NYC,
      language class NYC, coding workshop NYC
- Output a JSON array of objects, each with "query" (string) and "query_type" ("broad" or "niche").
"""


class SearchQuery(BaseModel):
    query: str
    query_type: Literal["broad", "niche"]


class SearchPlan(BaseModel):
    queries: List[SearchQuery]


class SearchPlanAgent:
    def __init__(self):
        self._llm = ChatAnthropic(model=MODEL).with_structured_output(SearchPlan)

    def generate(self) -> SearchPlan:
        logger.info("Generating Class Search Plan…")
        plan: SearchPlan = self._llm.invoke(
            [{"role": "user", "content": SYSTEM_PROMPT}]
        )
        logger.info(f"Class Search Plan generated with {len(plan.queries)} queries")
        for i, q in enumerate(plan.queries, 1):
            logger.debug(f"  [{i:02d}] [{q.query_type}] {q.query}")
        return plan
