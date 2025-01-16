from bs4 import Tag

from settings import my_logger


def get_ad_id(ad_element: Tag) -> int | None:
    try:
        return int(ad_element.get("id"))
    except AttributeError as e:
        my_logger.error(e)


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
