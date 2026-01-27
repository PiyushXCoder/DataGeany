from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    llm: str = Field(default="gemini", alias="LLM")
    ollama_host: str = Field(default="http://localhost:11434", alias="OLLAMA_HOST")
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    upload_dir: str = Field(default="uploads", alias="UPLOAD_DIR")

    class Config:
        env_file = ".env"

settings = Settings()
