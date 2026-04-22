from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # Air Quality API
    REALTIME_AQI_API_KEY: str
    
    # AI Provider API
    NVIDIA_QWEN_API_KEY: str

    # Security & Configuration
    SECRET_KEY: str = "default_insecure_secret_key"
    JWT_SECRET_KEY: str = "default_insecure_jwt_key"
    DATABASE_URL: str = "sqlite:///./aeroguard.db"
    
    # CORS Origins
    CORS_ORIGINS: List[str] = ["*"]
    
    # Operational Settings
    MODEL_CACHE_TIMEOUT: int = 3600
    LOG_LEVEL: str = "INFO"
    MAX_REQUEST_SIZE: int = 1048576  # 1MB default

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
