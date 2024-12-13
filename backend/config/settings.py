from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    # API Configuration
    API_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4"  # ou outro modelo de sua escolha
    
    # Security
    API_KEY_HEADER: str = "X-API-Key"
    API_KEY: Optional[str] = None
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30  # segundos
    
    # Storage
    STORAGE_PATH: str = "storage"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Uso: settings = get_settings()
