import asyncio
import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from db.utils import save_multiple_instance_data, get_ids, dump_database
from settings import my_logger
from src.main import scraper


def start_scraper():
    start_time = datetime.datetime.now()
    my_logger.info(f"Script started at {start_time}")
    my_logger.info("Fetching existing IDs from the database...")
    existing_ids = asyncio.run(get_ids())
    if not existing_ids:
        my_logger.info("No existing IDs found in the database.")
    scraper.existing_ids = set(existing_ids)

    my_logger.info(f"Existing IDs: {len(scraper.existing_ids)}")
    my_logger.info("Starting requests to collect ads...")
    ads_start_time = datetime.datetime.now()
    asyncio.run(scraper.start_requests())
    ads_end_time = datetime.datetime.now()
    my_logger.info(
        f"Collecting ads completed. Elapsed time: {ads_end_time - ads_start_time}"
    )
    my_logger.info("Saving ad data to the database...")
    save_start_time = datetime.datetime.now()
    asyncio.run(save_multiple_instance_data(scraper.ads))
    save_end_time = datetime.datetime.now()
    my_logger.info(
        f"Data saving completed. Elapsed time: {save_end_time - save_start_time}"
    )
    end_time = datetime.datetime.now()
    my_logger.info(f"Script finished at {end_time}")
    my_logger.info(f"Total elapsed time: {end_time - start_time}")


async def setup_scheduling():
    scheduler = AsyncIOScheduler()

    scheduler.add_job(start_scraper, trigger=IntervalTrigger(minutes=1))
    scheduler.add_job(dump_database, trigger=CronTrigger(hour="12"))
    scheduler.start()
    my_logger.info("Scheduler started")
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit) as e:
        my_logger.error(f"Shutting down scheduler with {e}")
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(setup_scheduling())
