
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TalentIQ Auth"
    app_env: str = "development"
    debug: bool = True

    # Server logs: JSON lines on stdout (see src/observability/logging).
    log_level: str = "INFO"
    log_json: bool = True

    # Requests per client IP per minute (0 = no limit). "Heavy" = sign-in and
    # password endpoints, kept low to slow down password guessing.
    rate_limit_per_minute: int = 600
    rate_limit_heavy_per_minute: int = 10
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    jwt_issuer: str = "talentiq-auth"
    jwt_audience: str = "talentiq-core"
    refresh_token_expire_days: int = 7
    
    
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str
    smtp_password: str
    smtp_from_email: str

    
    invite_accept_url: str = "http://localhost:3000/accept-invitation"


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
