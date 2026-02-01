from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    collector_interval: float = 0.25


settings = Settings()
