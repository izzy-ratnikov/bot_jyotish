import logging
import logging.config
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import UserData
from utils.logger import logging_config


logging.config.dictConfig(logging_config)
logger = logging.getLogger("db_operations")


class BaseDO:
    """Базовый класс с операциями к БД"""

    model = None

    @classmethod
    async def get_all(cls, session: AsyncSession):
        """Получить все элементы из БД"""
        try:
            logger.info(f"Fetching all records for {cls.model.__name__}")
            query = select(cls.model)
            result = await session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(
                f"An error occurred while fetching all records for "
                f"{cls.model.__name__}: {e}",
            )
            raise e

    @classmethod
    async def get_by_id(cls, session: AsyncSession, id: int):
        """Получить элементы по id или вернуть None если нет"""
        try:
            logger.info(f"Fetching {cls.model.__name__} with id {id}")
            query = select(cls.model).where(cls.model.id == id)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(
                f"An error occurred while fetching "
                f"{cls.model.__name__} with id {id}: {e}",
            )
            raise e

    @classmethod
    async def add(cls, session: AsyncSession, **values):
        """Добавить объект в БД"""
        new_instance = cls.model(**values)
        session.add(new_instance)
        try:
            await session.commit()
            logger.info(f"Added new {cls.model.__name__}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error adding {cls.model.__name__}: {e}")
            raise e
        return new_instance

    @classmethod
    async def update(cls, session: AsyncSession, id: int, **values):
        """Изменить элементы для id"""
        logger.info(f"Updating {cls.model.__name__} with id {id}")
        instance = await cls.get_by_id(session, id)
        if not instance:
            logger.warning(f"{cls.model.__name__} with id {id} not found")
            return None

        for key, value in values.items():
            setattr(instance, key, value)

        try:
            await session.commit()
            logger.info(f"Updated {cls.model.__name__} with id {id}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error updating {cls.model.__name__}: {e}")
            raise e
        return instance

    @classmethod
    async def delete(cls, session: AsyncSession, id: int):
        """Удалить по id"""
        logger.info(f"Deleting {cls.model.__name__} with id {id}")
        try:
            data = await cls.get_by_id(session=session, id=id)
            if data:
                await session.delete(data)
                await session.commit()
                logger.info(f"Deleted {cls.model.__name__} with id {id}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Error deleting {cls.model.__name__}: {e}")
            raise e


class UserDataDO(BaseDO):
    """Класс c операциями для модели UserData"""

    model = UserData
