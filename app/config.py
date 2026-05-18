from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    port: int = 8000
    node_env: str = "development"
    mongo_uri: str
    jwt_secret: str
    
    smtp_host: str
    smtp_port: int
    smtp_mail: str
    smtp_password: str
    smtp_service: Optional[str] = None
    
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    aws_s3_bucket: str
    
    razorpay_key_id: Optional[str] = None
    razorpay_key_secret: Optional[str] = None
    gemini_api_key: Optional[str] = None
    
    zego_app_id: Optional[int] = None
    zego_app_sign: Optional[str] = None
    zego_callback_secret: Optional[str] = None

    # Pydantic settings config to load .env variables
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
