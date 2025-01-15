import os

from dotenv import load_dotenv
from loguru import logger, Logger

load_dotenv()


class Config:
    BASE_URL = "https://www.olx.ua"
    MAIN_PAGE = f"{BASE_URL}/list/"
    AD_SELECTOR = ".css-l9drzq"
    HEADERS_FOR_VIEWS = {
        "Content-Type": "application/json",
        "Authorization": "ANONYMOUS",
        "site": "olxua",
    }
    REQUEST_FOR_VIEWS = {
        "operationName": "PageViews",
        "variables": {"adId": None},
        "query": "query PageViews($adId: String!) {\n  myAds {\n    pageViews(adId: $adId) {\n      pageViews\n    }\n  }\n}",
    }
    URL_FOR_RATING = (
        "https://rating-cdn.css.olx.io/ratings/v1/public/olxua/user/{}/score"
    )
    URL_FOR_VIEWS = (
        "https://production-graphql.eu-sharedservices.olxcdn.com/graphql"
    )
    API_URL = "https://www.olx.ua/api/v1/offers/{}"
    DATABASE_URI = os.getenv("DATABASE_URI")
    LOG_DIR = "logs"

    def get_logger(self) -> Logger:
        os.makedirs(self.LOG_DIR, exist_ok=True)
        logger.add(
            f"{self.LOG_DIR}/scraper.log",
            rotation="1 GB",
            retention=5,
            compression="zip",
        )
        return logger


config = Config()
