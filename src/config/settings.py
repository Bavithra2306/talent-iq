
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TalentIQ Auth"
    app_env: str = "development"
    debug: bool = True
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
