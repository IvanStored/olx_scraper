from typing import Sequence

from sqlalchemy import insert, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from db.connect_to_db import get_async_session
from db.model import Ad
from settings import config

logger = config.get_logger()


class DBHelper:
    model = Ad

    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_save_ad(self, instances_data: list[dict]) -> None:
        try:
            query = insert(self.model).values(instances_data)
            await self.session.execute(query)
        except SQLAlchemyError as e:
            logger.error(f"Error saving ads in bulk: {e}")

    async def get_ids_from_db(self) -> Sequence:
        query = select(self.model.id)  # noqa
        res = await self.session.execute(statement=query)
        return res.scalars().all()


async def save_multiple_instance_data(instances_data: list[dict]):
    async for session in get_async_session():
        saver = DBHelper(session)
        await saver.bulk_save_ad(instances_data=instances_data)


async def get_ids() -> Sequence:
    async for session in get_async_session():
        saver = DBHelper(session)
        return await saver.get_ids_from_db()
