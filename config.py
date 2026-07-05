"""Application settings loaded from environment variables (and an optional .env file)."""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV:str = "dev"
    APP_HOST:str = "0.0.0.0"
    APP_PORT:int = 8000
    OPENAI_API_KEY: str = ""

    class Config:
        # Read overrides from a local .env file when present.
        env_file = ".env"

# Import-time singleton shared across the app.
settings = Settings()