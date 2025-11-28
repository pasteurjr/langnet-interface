"""
Application configuration using Pydantic Settings
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    api_title: str = "LangNet API"
    api_version: str = "1.0.0"
    api_description: str = "REST API for LangNet Multi-Agent System Interface"
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_reload: bool = Field(default=True, env="API_RELOAD")

    # Database Configuration
    db_host: str = Field(default="camerascasas.no-ip.info", env="DB_HOST")
    db_port: int = Field(default=3308, env="DB_PORT")
    db_user: str = Field(default="producao", env="DB_USER")
    db_password: str = Field(default="112358123", env="DB_PASSWORD")
    db_name: str = Field(default="langnet", env="DB_NAME")

    # Security
    secret_key: str = Field(default="langnet-secret-key-change-this", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    # CORS Configuration
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:3001", env="CORS_ORIGINS")

    # Redis Configuration (optional)
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")

    # LLM Configuration
    llm_provider: str = Field(default="openai", env="LLM_PROVIDER")  # lmstudio, openai, deepseek, anthropic, google, claude_code

    # Claude Code (local API)
    claude_code_api_base: str = Field(default="http://localhost:8807", env="CLAUDE_CODE_API_BASE")
    claude_code_model_name: str = Field(default="claude-code", env="CLAUDE_CODE_MODEL_NAME")

    # LM Studio (local)
    lmstudio_api_base: str = Field(default="http://localhost:1234/v1", env="LMSTUDIO_API_BASE")
    lmstudio_model_name: str = Field(default="qwen2.5-coder-32b-instruct", env="LMSTUDIO_MODEL_NAME")

    # OpenAI
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_model_name: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL_NAME")

    # DeepSeek
    deepseek_api_key: str = Field(default="", env="DEEPSEEK_API_KEY")
    deepseek_api_base: str = Field(default="https://api.deepseek.com/v1", env="DEEPSEEK_API_BASE")
    deepseek_model_name: str = Field(default="deepseek/deepseek-chat", env="DEEPSEEK_MODEL_NAME")

    # Anthropic Claude
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    anthropic_model_name: str = Field(default="claude-3-5-sonnet-20241022", env="ANTHROPIC_MODEL_NAME")

    # Google Gemini
    google_api_key: str = Field(default="", env="GOOGLE_API_KEY")
    google_model_name: str = Field(default="gemini-1.5-pro", env="GOOGLE_MODEL_NAME")

    # Other APIs
    serper_api_key: str = Field(default="", env="SERPER_API_KEY")
    serpapi_api_key: str = Field(default="", env="SERPAPI_API_KEY")
    tavily_api_key: str = Field(default="", env="TAVILY_API_KEY")
    amadeus_api_key: str = Field(default="", env="AMADEUS_API_KEY")
    amadeus_api_secret: str = Field(default="", env="AMADEUS_API_SECRET")

    # File Upload Configuration
    upload_dir: str = Field(default="uploads", env="UPLOAD_DIR")
    max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB")
    allowed_extensions: str = Field(default="pdf,docx,doc,txt,md", env="ALLOWED_EXTENSIONS")

    @property
    def allowed_extensions_list(self) -> List[str]:
        """Parse allowed extensions string to list"""
        return [ext.strip() for ext in self.allowed_extensions.split(',')]

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string to list"""
        return [origin.strip() for origin in self.cors_origins.split(',')]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings
