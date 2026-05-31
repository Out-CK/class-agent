from __future__ import annotations

from typing import List, Literal

from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel

from utils.logger import get_logger

logger = get_logger(__name__)

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are an expert at generating search queries to find upcoming NYC class events.
Your task is to produce exactly 50 search queries that will surface the widest possible range of
upcoming classes, workshops, and skill-based experiences in New York City.

Rules:
- Generate EXACTLY 50 queries — no more, no fewer.
- Each query must have a query_type of "broad" or "niche".
- Broad queries (~15): General searches like "upcoming classes NYC this week",
  "workshops NYC this month", "things to learn in NYC 2026", "NYC skill classes for adults",
  "best cooking classes NYC", "creative workshops NYC", "NYC drop-in classes this weekend",
  "one-time workshops NYC", "date night classes NYC", "NYC group classes for beginners".
- Niche queries (~35): Category-specific or provider-specific. Must include dedicated queries
  for EACH of these categories:

    FOOD & DRINK:
      cooking classes NYC, baking classes NYC, sushi making class NYC,
      pasta making class NYC, bread baking workshop NYC, knife skills class NYC,
      chocolate making class NYC, fermentation class NYC, butchery class NYC,
      bagel making class NYC

    COCKTAILS & WINE:
      mixology class NYC, wine tasting class NYC, cocktail making class NYC,
      spirits tasting NYC, natural wine class NYC

    POTTERY & CERAMICS:
      pottery class NYC, ceramics wheel throwing class NYC, hand-building ceramics NYC,
      sculpture class NYC

    ART & PAINTING:
      painting class NYC, figure drawing class NYC, watercolor class NYC,
      oil painting workshop NYC, art class for beginners NYC

    CRAFT & MAKERS:
      candle making class NYC, soap making class NYC, perfume making workshop NYC,
      leather working class NYC, jewelry making class NYC, floral arrangement class NYC,
      screen printing class NYC, letterpress workshop NYC

    WOODWORKING & GLASS:
      woodworking class NYC, furniture making class NYC, glassblowing class NYC,
      stained glass workshop NYC

    TEXTILE & FIBER:
      sewing class NYC, knitting class NYC, embroidery workshop NYC,
      quilting class NYC, fashion design class NYC, weaving class NYC

    DANCE:
      salsa class NYC, bachata class NYC, swing dance class NYC,
      hip hop dance class NYC, ballet class NYC adults, contemporary dance class NYC,
      flamenco class NYC, ballroom dance class NYC

    MUSIC:
      guitar lessons NYC, piano class NYC, singing lessons NYC,
      music production class NYC, DJ class NYC, songwriting workshop NYC

    FITNESS & WELLNESS:
      yoga workshop NYC, meditation class NYC, aerial yoga class NYC,
      tai chi class NYC, boxing class NYC

    WRITING & COMEDY:
      creative writing class NYC, improv class NYC, standup comedy class NYC,
      screenwriting workshop NYC, poetry workshop NYC

    PHOTOGRAPHY & FILM:
      photography class NYC, film photography class NYC, video editing workshop NYC,
      iPhone photography class NYC

    TECH & PROFESSIONAL:
      coding bootcamp NYC, web design class NYC, data science class NYC,
      3D printing workshop NYC, AI workshop NYC

    LANGUAGE:
      Spanish class NYC, French class NYC, Japanese class NYC,
      sign language class NYC, Italian class NYC

    OTHER:
      calligraphy class NYC, first aid CPR class NYC, plant care workshop NYC,
      terrarium making class NYC, soap making class NYC

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
