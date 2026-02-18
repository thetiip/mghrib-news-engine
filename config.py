"""Configuration management for Maghrib News Aggregator."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = "sqlite:///./news.db"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # Scraping Configuration
    scraping_interval: int = 3600  # 1 hour
    max_articles_per_source: int = 50
    
    # Sentiment Analysis
    sentiment_model: str = "CAMeL-Lab/bert-base-arabic-camelbert-msa-sentiment"
    use_gpu: bool = False
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
