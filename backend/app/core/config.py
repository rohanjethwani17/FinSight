"""Configuration management for FinSight backend."""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-4o-mini"
    
    # Pinecone Configuration
    pinecone_api_key: str = ""
    pinecone_index_name: str = "finsight-index"
    pinecone_host: str = ""  # Optional, Pinecone client handles this for serverless
    
    # Retrieval Configuration
    top_k_results: int = 5
    
    # Supported Tickers
    supported_tickers: list[str] = ["AAPL", "MSFT", "GOOGL"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings(
        openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
        pinecone_api_key=os.environ.get("PINECONE_API_KEY", ""),
        pinecone_host=os.environ.get("PINECONE_HOST", ""),
    )
