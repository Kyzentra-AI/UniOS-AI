import os
from pathlib import Path
from dotenv import load_dotenv

# Locate and load the project root .env file
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE)


class Settings:
    """Centralized configuration for AI/ML-2 Learning Intelligence."""

    APP_NAME: str = os.getenv("APP_NAME", "UniOS Learning Intelligence")
    APP_ENV: str = os.getenv("APP_ENV", "development")

    # Local LLM provider settings (AI/ML-2 capability scope only)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq" if os.getenv("GROQ_API_KEY") else "mock").strip()
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen/qwen3.8-27b").strip()
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "").strip()
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))


# Singleton instance for import throughout the app
settings = Settings()
