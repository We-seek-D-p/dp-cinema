from pydantic import ValidationInfo, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    DJANGO_INTERNAL_URL: str = "http://localhost:8000"
    INTERNAL_SERVICE_TOKEN: str
    DJANGO_SECRET_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @field_validator(
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
        "POSTGRES_HOST",
        "DJANGO_INTERNAL_URL",
        "INTERNAL_SERVICE_TOKEN",
        "DJANGO_SECRET_KEY",
    )
    @classmethod
    def validate_non_empty(cls, v: str, info: ValidationInfo) -> str:
        if not v or not v.strip():
            raise ValueError(f"Field {info.field_name} cannot be empty")
        return v

    @field_validator("DJANGO_INTERNAL_URL")
    @classmethod
    def normalize_django_internal_url(cls, v: str) -> str:
        return v.strip().rstrip("/")


settings = Settings()
