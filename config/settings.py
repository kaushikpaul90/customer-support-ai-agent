"""
Configuration management for Customer Support AI Agent.

This module loads and validates environment variables and provides
centralized configuration access throughout the application.

GitHub Copilot Prompt Used:
"Create a Pydantic settings manager that loads Azure credentials,
LLM config, RAG settings, and API config from environment variables
with proper validation and type checking"
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class AzureOpenAISettings(BaseSettings):
    """Azure OpenAI configuration."""
    
    api_key: str
    endpoint: str
    deployment_name: str = "gpt-4"
    api_version: str = "2024-02-15-preview"
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.95
    
    class Config:
        env_prefix = "AZURE_OPENAI_"


class AzureSearchSettings(BaseSettings):
    """Azure Cognitive Search configuration."""
    
    endpoint: str
    key: str
    index_name: str = "customer-support-docs"
    top_k_retrieval: int = 5
    min_similarity_score: float = 0.5
    timeout_seconds: int = 10
    
    class Config:
        env_prefix = "AZURE_SEARCH_"


class RAGSettings(BaseSettings):
    """RAG pipeline configuration."""
    
    chunk_size: int = 1000
    chunk_overlap: int = 200
    min_similarity_score: float = 0.5
    top_k_retrieval: int = 5
    
    class Config:
        env_prefix = "RAG_"


class APISettings(BaseSettings):
    """FastAPI configuration."""
    
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    reload: bool = False
    title: str = "Customer Support AI Agent"
    description: str = "Production-grade AI agent for intelligent customer support"
    version: str = "1.0.0"
    
    class Config:
        env_prefix = "API_"


class EvaluationSettings(BaseSettings):
    """Evaluation framework configuration."""
    
    threshold_faithfulness: float = 0.85
    threshold_context_precision: float = 0.80
    threshold_answer_relevance: float = 0.75
    threshold_context_recall: float = 0.75
    
    class Config:
        env_prefix = "EVAL_"


class ObservabilitySettings(BaseSettings):
    """Logging and monitoring configuration."""
    
    log_level: str = "INFO"
    log_format: str = "json"
    jaeger_enabled: bool = False
    jaeger_agent_host: str = "localhost"
    jaeger_agent_port: int = 6831
    prometheus_enabled: bool = True
    
    class Config:
        env_prefix = ""


class Settings(BaseSettings):
    """Main application settings."""
    
    # Environment
    app_env: str = "development"
    app_name: str = "customer-support-ai-agent"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    allowed_origins: List[str] = ["http://localhost:3000"]
    
    # Rate limiting
    rate_limit_calls: int = 100
    rate_limit_period: int = 60
    
    # Timeouts
    request_timeout_seconds: int = 30
    llm_timeout_seconds: int = 60
    search_timeout_seconds: int = 10
    
    # Subsettings
    azure_openai: AzureOpenAISettings
    azure_search: AzureSearchSettings
    rag: RAGSettings
    api: APISettings
    evaluation: EvaluationSettings
    observability: ObservabilitySettings
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.app_env == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.app_env == "development"


# Lazy load settings
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get application settings singleton.
    
    Returns:
        Settings: Application configuration
    """
    global _settings
    if _settings is None:
        try:
            _settings = Settings()
            logger.info(
                f"Settings loaded successfully for {_settings.app_env} environment"
            )
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            raise
    return _settings


# For direct import
settings = get_settings()

__all__ = [
    "Settings",
    "AzureOpenAISettings",
    "AzureSearchSettings",
    "RAGSettings",
    "APISettings",
    "EvaluationSettings",
    "ObservabilitySettings",
    "get_settings",
    "settings",
]
