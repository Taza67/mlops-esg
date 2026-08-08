from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MLOPS_ESG_", extra="ignore")

    redis_url: str = "redis://localhost:6379/0"
    queue_name: str = "default"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    model_id: str = "facebook/bart-large-mnli"
