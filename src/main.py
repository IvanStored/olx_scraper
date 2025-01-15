import datetime

import asyncio

import aiohttp
import bs4
from loguru import Logger

from settings import config
from src.utils import (
    fetch_views,
    get_price,
    format_location,
    format_params,
    format_images,
    get_user_rating,
    get_ad_id,
)


class OLXScraper:
    DELIVERY_STATUS = {"active": True, "unactive": False}

    def __init__(self):
        self.ids: set = set()
        self.existing_ids: set = set()
        self.ads: list = []
        self.semaphore = asyncio.Semaphore(5)
        self.logger: Logger = config.get_logger()

    async def collect_ads_id(self, session, page_number: int) -> list:
        try:
            async with session.get(
                url=config.MAIN_PAGE, params={"page": page_number}
            ) as res:
                if res.status == 200:
                    res_text = await res.text()
                    soup = bs4.BeautifulSoup(res_text, "html.parser")
                    ads = soup.select(selector=config.AD_SELECTOR)
                    self.logger.info(f"Page: {page_number}|Ads: {len(ads)}")
                    return [get_ad_id(ad_element=ad) for ad in ads]
                else:
                    self.logger.error(f"Error when parsed ads {res.status}")
                    return []
        except Exception as e:
            self.logger.error(e)

    async def start_requests(self) -> None:
        async with aiohttp.ClientSession(trust_env=True) as session:
            tasks = []
            for page_number in range(1, 6):
                task = asyncio.create_task(
                    self.collect_ads_id(session, page_number)
                )
                tasks.append(task)

            await asyncio.gather(*tasks)

        for task in tasks:
            self.ids.update(task.result())
        self.logger.info(f"Collected {len(self.ids)} ad IDs.")

    async def __process_ad(self, session, ad_json: dict, ad_id: int) -> None:
        try:
            data = ad_json["data"]
            city = data["location"]["city"]["name"]
            district = data["location"].get("district")
            if not district:
                district = ""
            else:
                district = district["name"]
            region = data["location"]["region"]["name"]
            views = await fetch_views(session=session, ad_id=ad_id)
            instance_data = {
                "id": ad_id,
                "url": data["url"],
                "description": data["description"],
                "publication_date": datetime.datetime.fromisoformat(
                    data["last_refresh_time"]
                ),
                "title": data["title"],
                "price": get_price(data["params"]),
                "location": format_location(
                    city=city, district=district, region=region
                ),
                "username": data["user"]["name"],
                "user_registration": datetime.datetime.fromisoformat(
                    data["user"]["created"]
                ),
                "last_seen": datetime.datetime.fromisoformat(
                    data["user"]["last_seen"]
                ),
                "_params": format_params(ad_params=data["params"]),
                "_image_urls": format_images(ad_images=data.get("photos")),
                "business": data["business"],
                "olx_delivery": self.DELIVERY_STATUS[
                    data["safedeal"]["status"]
                ],
                "views": views,
                "user_rating": await get_user_rating(
                    session=session, user_uuid=data["user"]["uuid"]
                ),
            }
            self.logger.info(f"Processed ad ID: {ad_id}")
            self.ads.append(instance_data)
        except Exception as e:
            self.logger.error(f"Error processing ad {ad_id}: {e}")

    async def __request_to_api(self, session, ad_id: int) -> None:
        try:
            async with self.semaphore:
                async with session.get(
                    url=config.API_URL.format(ad_id)
                ) as res:
                    ad_json = await res.json()
                    await self.__process_ad(
                        session=session, ad_json=ad_json, ad_id=ad_id
                    )
        except Exception as e:
            self.logger.error(f"Error fetching ad ID {ad_id}: {e}")

    async def start_requests_to_api(self) -> None:
        new_ids = self.ids - self.existing_ids
        self.logger.info(f"New IDs to process: {len(new_ids)}")

        async with aiohttp.ClientSession(trust_env=True) as session:
            tasks = []
            for _id in new_ids:
                task = asyncio.create_task(self.__request_to_api(session, _id))
                tasks.append(task)

            await asyncio.gather(*tasks)


scraper = OLXScraper()
