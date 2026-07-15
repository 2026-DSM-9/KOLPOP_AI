from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    anthropic_api_key: str = Field(default="", validation_alias=AliasChoices("ANTHROPIC_API_KEY", "CLAUDE_API_KEY"))
    claude_model: str = Field(default="", alias="CLAUDE_MODEL")
    claude_max_tokens: int = Field(default=1800, alias="CLAUDE_MAX_TOKENS")
    claude_temperature: float = Field(default=0.35, alias="CLAUDE_TEMPERATURE")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")


settings = Settings()
