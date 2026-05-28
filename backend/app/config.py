from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://riskuser:riskpass@localhost:5432/risktracker"
    environment: str = "development"
    api_prefix: str = "/api/v1"

    auth_secret_key: str = "change-me-in-production"
    auth_algorithm: str = "HS256"
    auth_token_expire_minutes: int = 60 * 24  # 24 hours

    google_client_id: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
