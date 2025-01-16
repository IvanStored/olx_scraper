import datetime

import asyncio

import aiohttp


from settings import config, my_logger
from src.utils import (
    get_price,
    format_location,
    format_params,
    format_images,
)


class OLXScraper:
    DELIVERY_STATUS = {"active": True, "unactive": False}

    def __init__(self):
        self.existing_ids: set = set()
        self.ads: list = []
        self.lock = asyncio.Lock()

    async def collect_ads(self, session, offset: int) -> None:
        try:

            async with session.get(
                url=config.MAIN_API,
                params={"offset": offset, "limit": 40},
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
                },
            ) as res:
                if res.status == 200:
                    res_json = await res.json()
                    await self.__process_ads(session=session, ad_json=res_json)
                else:
                    my_logger.error(f"Error when parsed ads {res.status}")
        except Exception as e:
            my_logger.error(e)

    async def start_requests(self) -> None:
        async with aiohttp.ClientSession(trust_env=True) as session:
            tasks = []
            for offset in range(0, 160, 40):
                task = asyncio.create_task(self.collect_ads(session, offset))
                tasks.append(task)

            await asyncio.gather(*tasks)

    async def __process_ads(self, session, ad_json: dict) -> None:

        data: list = ad_json["data"]

        for ad in data:
            try:
                ad_id = ad["id"]
                async with self.lock:
                    if ad_id in self.existing_ids:
                        my_logger.warning(f"Duplicate ad ID skipped: {ad_id}")
                        continue
                    self.existing_ids.add(ad_id)
                city = ad["location"]["city"]["name"]
                district = ad["location"].get("district")
                if not district:
                    district = ""
                else:
                    district = district["name"]
                region = ad["location"]["region"]["name"]
                views = await self.__fetch_views(session=session, ad_id=ad_id)
                rating = await self.__get_user_rating(
                    session=session, user_uuid=ad["user"]["uuid"]
                )
                instance_data = {
                    "id": ad_id,
                    "url": ad["url"],
                    "description": ad["description"],
                    "publication_date": datetime.datetime.fromisoformat(
                        ad["last_refresh_time"]
                    ),
                    "title": ad["title"],
                    "price": get_price(ad["params"]),
                    "location": format_location(
                        city=city, district=district, region=region
                    ),
                    "username": ad["user"]["name"],
                    "user_registration": datetime.datetime.fromisoformat(
                        ad["user"]["created"]
                    ),
                    "last_seen": datetime.datetime.fromisoformat(
                        ad["user"]["last_seen"]
                    ),
                    "_params": format_params(ad_params=ad["params"]),
                    "_image_urls": format_images(ad_images=ad.get("photos")),
                    "business": ad["business"],
                    "olx_delivery": self.DELIVERY_STATUS[
                        ad["safedeal"]["status"]
                    ],
                    "views": views,
                    "user_rating": rating,
                }
                my_logger.info(f"Processed ad ID: {ad_id}")
                self.ads.append(instance_data)
            except Exception as e:
                my_logger.error(f"Error processing ad {ad_id}: {e}")

    async def __fetch_views(self, session, ad_id: id) -> int:
        payload = config.REQUEST_FOR_VIEWS
        payload["variables"]["adId"] = str(ad_id)

        try:

            async with session.post(
                url=config.URL_FOR_VIEWS,
                json=payload,
                headers=config.HEADERS_FOR_VIEWS,
            ) as res:
                if res.status == 200:
                    resp_json = await res.json()
                    return resp_json["data"]["myAds"]["pageViews"]["pageViews"]
                else:
                    my_logger.error(
                        f"Error fetching views for ad {ad_id}: {res.status}"
                    )
                    return 0
        except Exception as e:
            my_logger.error(
                f"Exception while fetching views for ad {ad_id}: {e}"
            )
            return 0

    async def __get_user_rating(self, session, user_uuid: str) -> float:
        try:
            async with session.get(
                url=config.URL_FOR_RATING.format(user_uuid),
            ) as res:
                if res.status == 200:
                    resp_json = await res.json()
                    return float(resp_json["value"])
                elif res.status == 204:
                    return 0
                else:
                    my_logger.error(
                        f"Error fetching rating for user {user_uuid}: {res.status}"
                    )
                    return 0
        except Exception as e:
            my_logger.error(
                f"Exception while fetching rating for user {user_uuid}: {e}"
            )
            return 0


scraper = OLXScraper()
