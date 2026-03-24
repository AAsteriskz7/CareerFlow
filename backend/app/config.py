"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All runtime settings for CareerFlow backend."""

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # LangSmith observability
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "CareerFlow"

    # Storage
    llama_index_storage_dir: str = "./storage"
    data_dir: str = "../data"

    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000


settings = Settings()
