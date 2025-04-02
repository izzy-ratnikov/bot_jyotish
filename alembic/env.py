from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# Импортируем нашу базу данных и модели
from database.models import Base
import database.models  # noqa: F401
from config import settings


# Подключаем логгер
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


DATABASE_URL = (
    f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)


# Создаём движок SQLAlchemy
connectable = create_async_engine(DATABASE_URL, poolclass=pool.NullPool)


def run_migrations_offline():
    """Запускаем миграции в оффлайн-режиме (без подключения к базе)"""
    context.configure(
        url=DATABASE_URL, target_metadata=Base.metadata, literal_binds=True
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Запускаем миграции в онлайн-режиме (с подключением к базе)"""
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


def do_run_migrations(connection):
    """Запуск миграций"""
    context.configure(connection=connection, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio

    asyncio.run(run_migrations_online())
