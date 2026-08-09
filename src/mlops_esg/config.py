from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MLOPS_ESG_", extra="ignore")

    redis_url: str = "redis://localhost:6379/0"
    queue_name: str = "default"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_base_url: str = "http://127.0.0.1:8000"
    model_id: str = "facebook/bart-large-mnli"
    stream_key: str = "esg:documents"
    stream_group: str = "esg-consumers"
    stream_consumer: str = "consumer-1"
    rss_feed_url: str = "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml"
    rss_poll_seconds: int = 300
    rss_once: bool = False
