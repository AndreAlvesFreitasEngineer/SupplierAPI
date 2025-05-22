from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    DATABASE_URL: str = Field("sqlite+aiosqlite:///./shipping.db", env="DATABASE_URL")
    TEST_DATABASE_URL: str = Field(
        "sqlite+aiosqlite:///./test.db", env="TEST_DATABASE_URL"
    )
    APP_NAME: str = Field("Shipping API", env="APP_NAME")
    DEBUG: bool = Field(False, env="DEBUG")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
