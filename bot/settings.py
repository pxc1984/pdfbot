from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    token: str = Field(alias="TOKEN")
    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    pg_host: str = Field(default="db", alias="POSTGRES_HOST")
    pg_port: int = Field(default=5432, alias="POSTGRES_PORT")
    pg_db: str = Field(default="pdfbot", alias="POSTGRES_DB")
    pg_user: str = Field(default="pdfbot", alias="POSTGRES_USER")
    pg_password: str = Field(default="pdfbot", alias="POSTGRES_PASSWORD")
    webhook_url: str | None = Field(default=None, alias="WEBHOOK_URL")
    webhook_host: str = Field(default="0.0.0.0", alias="WEBHOOK_HOST")
    webhook_port: int = Field(default=8080, alias="WEBHOOK_PORT")

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql://{self.pg_user}:{self.pg_password}"
            f"@{self.pg_host}:{self.pg_port}/{self.pg_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
