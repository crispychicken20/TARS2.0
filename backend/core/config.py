import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global configuration for the TARS backend."""
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8081
    API_DEBUG: bool = True

    # Can be JSON list or comma-separated string in .env
    CORS_ALLOW_ORIGINS: List[str] | str = ["http://localhost:3000"]

    CHROMA_PERSIST_DIR: str = "./data/chroma"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 120

    # Default env file path; works even if running inside /backend
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", os.path.join(os.path.dirname(__file__), "..", ".env")),
        env_file_encoding="utf-8",
        extra='allow'
    )

    @property
    def cors_list(self) -> List[str]:
        """Normalize CORS origins (supports JSON or comma-separated)."""
        if isinstance(self.CORS_ALLOW_ORIGINS, str):
            # Strip brackets if user accidentally adds them
            raw = self.CORS_ALLOW_ORIGINS.strip().strip("[]")
            return [origin.strip().strip('"').strip("'") for origin in raw.split(",") if origin.strip()]
        return self.CORS_ALLOW_ORIGINS


# Global settings instance
settings = Settings()
