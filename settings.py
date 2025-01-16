import os

from dotenv import load_dotenv
from loguru import logger

load_dotenv()


class Config:
    MAIN_API = "https://www.olx.ua/api/v1/offers/"
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
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_USERNAME = os.getenv("POSTGRES_USER")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    DATABASE_URI = os.getenv("DATABASE_URI")
    LOG_DIR = "logs"
    DUMPS_DIR = "dumps"
    DUMP_FILENAME = "dump_{}.sql"

    def get_logger(self):
        os.makedirs(self.LOG_DIR, exist_ok=True)
        logger.add(
            f"{self.LOG_DIR}/scraper.log",
            rotation="1 GB",
            retention=5,
            compression="zip",
        )
        return logger


config = Config()
my_logger = config.get_logger()
