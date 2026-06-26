from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Research-to-Product Advisor"
    debug: bool = False

    # Neon PostgreSQL
    database_url: str = "postgresql+psycopg://localhost/rtp"

    # Upstash Redis (optional)

    upstash_redis_rest_url: str = ""
    upstash_redis_rest_token: str = ""

    # LLM Keys
    gemini_api_key: str = ""
    groq_api_key: str = ""
    groq_api_base: str = "https://api.groq.com/openai/v1"

    # Legacy (unused but kept so old .env files don't break)
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    tavily_api_key: str = ""

    # Storage
    upload_dir: str = "uploads"
    chromadb_path: str = "chromadb"

    # Auth
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    class Config:
        env_file = ".env"
        extra = "ignore"   # ignore any extra keys in .env — prevents this error entirely


@lru_cache()
def get_settings() -> Settings:
    return Settings()