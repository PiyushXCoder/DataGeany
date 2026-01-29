from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    llm: str = Field(default="gemini", alias="LLM")
    ollama_host: str = Field(default="http://localhost:11434", alias="OLLAMA_HOST")
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    upload_dir: str = Field(default="uploads", alias="UPLOAD_DIR")
    
    # MySQL Database Configuration
    mysql_host: str = Field(default="localhost", alias="MYSQL_HOST")
    mysql_port: int = Field(default=3306, alias="MYSQL_PORT")
    mysql_user: str = Field(default="root", alias="MYSQL_USER")
    mysql_password: str = Field(default="", alias="MYSQL_PASSWORD")
    mysql_database: str = Field(default="", alias="MYSQL_DATABASE")
    mysql_pool_name: str = Field(default="myapp_pool", alias="MYSQL_POOL_NAME")
    mysql_pool_size: int = Field(default=5, alias="MYSQL_POOL_SIZE")

    class Config:
        env_file = ".env"

settings = Settings()
