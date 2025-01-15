from bs4 import Tag

from settings import config

logger = config.get_logger()


def get_ad_id(ad_element: Tag) -> int | None:
    try:
        return int(ad_element.get("id"))
    except AttributeError as e:
        logger.error(e)


async def fetch_views(session, ad_id: id) -> int:
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
                logger.error(
                    f"Error fetching views for ad {ad_id}: {res.status}"
                )
                return 0
    except Exception as e:
        logger.error(f"Exception while fetching views for ad {ad_id}: {e}")
        return 0


def get_price(params_list: list) -> int | None:
    for param in params_list:
        if param["key"] == "price":
            return param["value"]["value"]


def format_params(ad_params: list) -> str:
    final_string = ""
    for param in ad_params:
        if param["key"] not in ("price", "salary"):
            final_string += f"{param['name']}:{param['value']['label']}|"
        if param["key"] == "salary":
            final_string += f"{param['name']}:{param['value']['from']}-{param['value']['to']}/{param['value']['type']}|"
    return final_string


def format_images(ad_images: list | None) -> str:
    final_string = ""
    if ad_images:
        for image_url in ad_images:
            final_string += f"{image_url['link'].split(';s=')[0]}|"
    return final_string


def format_location(city: str, region: str, district: str) -> str:
    if district:
        return f"{city},{district},{region}"
    return f"{city},{region}"


async def get_user_rating(session, user_uuid: str) -> float:
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
                logger.error(
                    f"Error fetching rating for user {user_uuid}: {res.status}"
                )
                return 0
    except Exception as e:
        logger.error(
            f"Exception while fetching rating for user {user_uuid}: {e}"
        )
        return 0
