from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str = Field(default=..., alias="GEMINI_API_KEY")

    class Config:
        env_file = ".env"

settings = Settings()
