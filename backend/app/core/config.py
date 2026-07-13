from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    app_secret_key: str = "dev-only-insecure-key-override-me"
    roll_number_pepper: str = "dev-only-insecure-pepper-override-me"

    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    database_url: str = "mysql+aiomysql://akp_user:akp_password@localhost:3306/anti_kuddus_protocol"

    cors_origins: str = "http://localhost:5173"

    google_client_id: str | None = None

    facebook_app_id: str | None = None
    facebook_app_secret: str | None = None

    llm_provider: str = "openai"
    openai_api_key: str | None = None
    gemini_api_key: str | None = None

    storage_backend: str = "local"
    uploads_dir: str = "./uploads"
    s3_bucket: str | None = None
    s3_region: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None

    login_rate_limit: str = "5/minute"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Settings are read once and cached; tests override via dependency_overrides
    or by constructing Settings() directly with env vars set."""
    return Settings()
