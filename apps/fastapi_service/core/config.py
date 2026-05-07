from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, ValidationInfo


class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379/0"
    S3_ENDPOINT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET: str
    DJANGO_API_URL: str = "http://localhost:8000"
    INTERNAL_SERVICE_TOKEN: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("REDIS_URL", "S3_ENDPOINT", "S3_ACCESS_KEY", 
                     "S3_SECRET_KEY", "S3_BUCKET", "DJANGO_API_URL", 
                     "INTERNAL_SERVICE_TOKEN")
    @classmethod
    def validate_non_empty(cls, v: str, info: ValidationInfo) -> str:
        if not v or not v.strip():
            raise ValueError(f"Field cannot be empty: {info.field_name}")
        return v


settings = Settings()
