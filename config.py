from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV:str = "dev"
    APP_HOST:str = "0.0.0.0"
    APP_PORT:int = 8000
    OPENAI_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()