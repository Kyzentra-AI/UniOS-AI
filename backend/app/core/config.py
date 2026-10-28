from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str = "https://placeholder-project.supabase.co"
    SUPABASE_ANON_KEY: str = "placeholder-anon-key"
    SUPABASE_SERVICE_KEY: str = "placeholder-service-key"
    SUPABASE_JWT_SECRET: str = "placeholder-jwt-secret-at-least-32-chars-long-placeholder"
    FRONTEND_URL: str = "http://localhost:3000"
    KIE_BASE_URL: str = "http://localhost:8001" # Default placeholder for KIE
    KIE_AI2_BASE_URL: str = "http://localhost:8002" # Dedicated placeholder for KIE AI-2
    KIE_WEBHOOK_SECRET: str = "placeholder-kie-secret"
    ALLOWED_REDIRECT_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]

    # Cashfree Payment Gateway Settings
    CASHFREE_ENV: str = "sandbox"  # "sandbox" or "production"
    CASHFREE_PG_BASE_URL: str = "https://sandbox.cashfree.com/pg"
    CASHFREE_CLIENT_ID: str = ""
    CASHFREE_CLIENT_SECRET: str = ""
    CASHFREE_API_VERSION: str = "2023-08-01"
    CASHFREE_RETURN_URL: str = "http://localhost:3000/billing/return"
    CASHFREE_WEBHOOK_URL: str = "http://localhost:8000/api/v1/webhooks/cashfree"

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
