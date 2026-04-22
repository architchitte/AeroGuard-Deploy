from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union

class Settings(BaseSettings):
    # Air Quality API
    REALTIME_AQI_API_KEY: str
    
    # AI Provider API
    NVIDIA_QWEN_API_KEY: str

    # Security & Configuration
    SECRET_KEY: str = "default_insecure_secret_key"
    JWT_SECRET_KEY: str = "default_insecure_jwt_key"
    DATABASE_URL: str = "sqlite:///./aeroguard.db"
    
    # CORS Origins (Handles both JSON lists and comma-separated strings)
    CORS_ORIGINS: Union[List[str], str] = ["*"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        return v
    
    # Operational Settings
    MODEL_CACHE_TIMEOUT: int = 3600
    LOG_LEVEL: str = "INFO"
    MAX_REQUEST_SIZE: int = 1048576  # 1MB default

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        protected_namespaces=()
    )

settings = Settings()
