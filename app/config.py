from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "PlayOracle API"
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    database_url: str = "sqlite:///./playoracle.db"
    
    stripe_api_key: str = "sk_test_your_stripe_key"
    stripe_webhook_secret: str = "whsec_your_webhook_secret"
    
    thesportsdb_api_key: str = "3"
    footballdata_api_key: str = ""
    
    redis_url: str = "redis://localhost:6379"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
