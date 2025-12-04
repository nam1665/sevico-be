from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # FastAPI Configuration
    fastapi_env: str = "development"
    debug: bool = True
    secret_key: str = "your-secret-key-change-in-production"
    
    # Server Configuration
    app_host: str = "0.0.0.0"
    app_port: int = 8002
    
    # MongoDB Configuration
    mongodb_host: str = "localhost"
    mongodb_port: int = 27017
    mongodb_username: str = "your-username"
    mongodb_password: str = "your-password"
    mongodb_db_name: str = "sevico_db"
    mongodb_auth_source: str = "admin"
    
    # JWT Configuration
    jwt_secret_key: str = "your-jwt-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    refresh_token_expiration_days: int = 7
    
    # Email Configuration (SMTP)
    smtp_host: str = "email-smtp.us-east-1.amazonaws.com"
    smtp_port: int = 587
    smtp_username: str = "your-username"
    smtp_password: str = "your-password"
    smtp_tls: bool = True
    sender_email: str = "your-email@example.com"
    sender_name: str = "Your Name"
    aws_ses_configuration_set: str = ""  # Optional: AWS SES Configuration Set name
    
    # Documentation Authentication (HTTP Basic Auth)
    docs_username: str = "admin"
    docs_password: str = "admin"
    
    # Password Reset Configuration
    password_reset_expiration_hours: int = 1
    verification_code_expiration_minutes: int = 15
    
    # Password Reset Configuration
    password_reset_expiration_hours: int = 1
    verification_code_expiration_minutes: int = 15
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
