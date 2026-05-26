from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://riskuser:riskpass@localhost:5432/risktracker"
    environment: str = "development"
    api_prefix: str = "/api/v1"

    class Config:
        env_file = ".env"


settings = Settings()
