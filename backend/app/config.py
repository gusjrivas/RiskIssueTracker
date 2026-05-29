from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql://riskuser:riskpass@localhost:5432/risktracker"
    environment: str = "development"
    api_prefix: str = "/api/v1"

    auth_secret_key: str = "change-me-in-production"
    auth_algorithm: str = "HS256"
    auth_token_expire_minutes: int = 60 * 24

    google_client_id: str = ""


settings = Settings()
