import datetime
import os
import subprocess
from typing import Sequence

from sqlalchemy import insert, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from db.connect_to_db import get_async_session
from db.model import Ad
from settings import config, my_logger


class DBHelper:
    model = Ad

    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_save_ad(self, instances_data: list[dict]) -> None:
        try:
            query = insert(self.model).values(instances_data)
            await self.session.execute(query)
        except SQLAlchemyError as e:
            my_logger.error(f"Error saving ads in bulk: {e}")

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


def dump_database() -> None:
    os.makedirs(config.DUMPS_DIR, exist_ok=True)
    now_time = datetime.datetime.now()
    output_path = os.path.join(
        config.DUMPS_DIR, config.DUMP_FILENAME.format(now_time)
    )

    pg_dump_command = f"PGPASSWORD={config.POSTGRES_PASSWORD} pg_dump --host={config.POSTGRES_HOST} --username={config.POSTGRES_USERNAME} {config.POSTGRES_DB}"

    try:
        with open(output_path, "w") as dump_file:
            subprocess.run(
                pg_dump_command,
                shell=True,
                stdout=dump_file,
                stderr=subprocess.PIPE,
                check=True,
            )
        my_logger.success(f"Database dumped successfully to {output_path}")
    except subprocess.CalledProcessError as e:
        my_logger.error(f"An error occurred: {e.stderr.decode()}")
