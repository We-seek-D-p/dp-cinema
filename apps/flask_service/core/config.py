from pydantic import field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URI: str = "postgresql+psycopg2://user:pass@localhost:5432/reviews_db"

    DJANGO_API_URL: str = "http://localhost:8000"
    INTERNAL_SERVICE_TOKEN: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("SQLALCHEMY_DATABASE_URI", "DJANGO_API_URL", "INTERNAL_SERVICE_TOKEN")
    @classmethod
    def validate_non_empty(cls, v: str, info: ValidationInfo) -> str:
        if not v or not v.strip():
            raise ValueError(f"Field {info.field_name} cannot be empty")
        return v


settings = Settings()
