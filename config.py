from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str

    OPENAI_API_KEY: str

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    REDIS_HOST: str
    REDIS_PORT: int

    MAIN_MENU_BOT: dict = {
        "/start": "Старт бота",
        "/menu": "Главное меню",
    }

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()