from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_db: str = "postgres"
    pgport: int = 5432
    redis_url: str = "redis://backend-redis:6379/0"

    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_pre_ping: bool = True
    db_pool_recycle: int = 3600

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.pgport}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
