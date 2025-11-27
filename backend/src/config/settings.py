from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    # Database Configuration
    database_url: str

    # Redis Configuration
    redis_url: str

    # GitLab API Configuration
    gitlab_api_url: str = "https://gitlab.com/api/v4"
    gitlab_access_token: str = ""

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Application Settings
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # Celery Configuration
    celery_broker_url: str
    celery_result_backend: str

    # Daily Batch Schedule
    daily_batch_hour: int = 2
    daily_batch_minute: int = 0

    # Cache Settings
    cache_historical_data_ttl: int = 86400  # 24 hours
    cache_recent_data_ttl: int = 3600  # 1 hour

    # API Rate Limiting
    gitlab_api_rate_limit_per_minute: int = 60

    @property
    def cors_origins_list(self) -> list[str]:
        """Convert CORS origins string to list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"


# Global settings instance
settings = Settings()
