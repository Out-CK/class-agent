import time

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from utils.logger import get_logger

logger = get_logger(__name__)

eastern = pytz.timezone("America/New_York")


def run_class_run() -> None:
    from agent.class_agent import ClassAgent
    logger.info("Scheduled Class Run triggered")
    try:
        ClassAgent().run()
    except Exception as e:
        logger.error(f"Scheduled Class Run failed: {e}", exc_info=True)


def run_venue_enricher() -> None:
    from agent.venue_enricher import VenueEnricher
    logger.info("Scheduled Venue Enricher triggered")
    try:
        VenueEnricher(event_type="class").run()
    except Exception as e:
        logger.error(f"Scheduled Venue Enricher failed: {e}", exc_info=True)


def start_scheduler() -> None:
    scheduler = BackgroundScheduler(timezone=eastern)
    scheduler.add_job(
        run_class_run,
        trigger=CronTrigger(hour=10, minute=0, timezone=eastern),
        id="daily_class_run",
        name="Daily NYC Class Run",
        replace_existing=True,
    )
    scheduler.add_job(
        run_venue_enricher,
        trigger=CronTrigger(hour=10, minute=30, timezone=eastern),
        id="daily_venue_enricher",
        name="Daily Venue Enricher",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started — Class Run fires daily at 10:00 America/New_York")
    logger.info("Venue Enricher fires daily at 10:30 America/New_York")
    logger.info("Press Ctrl+C to stop")
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down scheduler…")
        scheduler.shutdown()
        logger.info("Scheduler stopped")
