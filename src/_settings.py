from pydantic.v1 import BaseSettings
from src.constants import ENV_PATH


class Settings(BaseSettings):
    REQUEST_TIMEOUT: int = 60
    API_TOKEN: str
    OPENAI_API_KEY: str


def settings_factory() -> Settings:
    return Settings(_env_file=ENV_PATH)
