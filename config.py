from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/torq_e"

    # API
    api_title: str = "TORQ-E (Medicaid Clarity System)"
    api_version: str = "1.0.0"
    api_description: str = "Card 1 (UMID) & Card 2 (UPID) - Member & Provider Unified Identification"

    # Anthropic Claude API
    anthropic_api_key: str = ""

    # River Path configuration
    river_path_timeout_seconds: int = 30
    river_path_max_retries: int = 3

    # Confidence scoring thresholds
    confidence_high: float = 0.85
    confidence_medium: float = 0.65
    confidence_low: float = 0.40

    # External API endpoints (placeholder - will integrate with real sources)
    state_medicaid_api_url: Optional[str] = None
    ssa_wage_records_api_url: Optional[str] = None
    federal_exclusions_api_url: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
