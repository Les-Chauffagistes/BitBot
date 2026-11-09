from typing import Literal
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    token: str
    port: int = 8085
    environment: Literal["development", "production"] = "development"
    bitcoin_api_url: str
    support_category_id: int
    force_sync: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    model_config = {"env_file": ".env", "extra": "allow", "secrets_dir": "/run/secrets"}


settings = Settings()