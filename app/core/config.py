from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    APP_NAME: str = "PrepAlly Relay"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Security
    RELAY_API_KEY: str = "dev-insecure-key"  # Override in production .env

    # AI Provider Keys
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    MISTRAL_API_KEY: str = ""


settings = Settings()
