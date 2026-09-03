"""
Central configuration. Reads from environment variables / .env file.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "GramVyapaar AI"
    anthropic_api_key: str = ""
    data_gov_in_api_key: str = ""
    agmarknet_api_key: str = ""
    frontend_origin: str = "http://localhost:5173"
    jwt_secret_key: str = "dev-only-insecure-secret-change-in-.env"

    class Config:
        env_file = ".env"


settings = Settings()
