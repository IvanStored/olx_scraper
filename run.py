import asyncio
import datetime

from db.utils import save_multiple_instance_data, get_ids
from settings import config
from src.main import scraper

logger = config.get_logger()

if __name__ == "__main__":
    start_time = datetime.datetime.now()
    logger.info(f"Script started at {start_time}")
    logger.info("Fetching existing IDs from the database...")
    existing_ids = asyncio.run(get_ids())
    if not existing_ids:
        logger.info("No existing IDs found in the database.")
    scraper.existing_ids = set(existing_ids)

    logger.info(f"Existing IDs: {len(scraper.existing_ids)}")
    logger.info("Starting requests to collect ads...")
    ads_start_time = datetime.datetime.now()
    asyncio.run(scraper.start_requests())
    ads_end_time = datetime.datetime.now()
    logger.info(
        f"Collecting ads completed. Elapsed time: {ads_end_time - ads_start_time}"
    )
    logger.info("Starting requests to fetch ad details...")
    api_start_time = datetime.datetime.now()
    asyncio.run(scraper.start_requests_to_api())
    api_end_time = datetime.datetime.now()
    logger.info(
        f"Fetching ad details completed. Elapsed time: {api_end_time - api_start_time}"
    )
    logger.info("Saving ad data to the database...")
    save_start_time = datetime.datetime.now()
    asyncio.run(save_multiple_instance_data(scraper.ads))
    save_end_time = datetime.datetime.now()
    logger.info(
        f"Data saving completed. Elapsed time: {save_end_time - save_start_time}"
    )
    end_time = datetime.datetime.now()
    logger.info(f"Script finished at {end_time}")
    logger.info(f"Total elapsed time: {end_time - start_time}")
