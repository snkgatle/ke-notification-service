import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from google.cloud import secretmanager

class Settings(BaseSettings):
    # App Settings
    PROJECT_ID: str = "kgatle-empire-services"
    ENVIRONMENT: str = "development"
    APP_NAME: str = "NotificationService"
    
    # Firestore Settings
    OTP_COLLECTION: str = "otps"
    OTP_TTL_MINUTES: int = 5
    
    # Pub/Sub Settings
    PUB_SUB_TOPIC: str = "notifications-topic"
    
    # Secrets (to be fetched from Secret Manager in production)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    BREVO_API_KEY: Optional[str] = None
    BREVO_FROM_EMAIL: Optional[str] = "notifications@example.com"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def fetch_secrets(self):
        """Fetch secrets from Google Secret Manager if in production."""
        if self.ENVIRONMENT == "production":
            client = secretmanager.SecretManagerServiceClient()
            
            # Helper to fetch secret
            def get_secret(secret_id: str) -> str:
                name = f"projects/{self.PROJECT_ID}/secrets/{secret_id}/versions/latest"
                response = client.access_secret_version(request={"name": name})
                return response.payload.data.decode("UTF-8")

            try:
                self.TWILIO_ACCOUNT_SID = get_secret("TWILIO_ACCOUNT_SID")
                self.TWILIO_AUTH_TOKEN = get_secret("TWILIO_AUTH_TOKEN")
                self.TWILIO_PHONE_NUMBER = get_secret("TWILIO_PHONE_NUMBER")
                self.BREVO_API_KEY = get_secret("BREVO_API_KEY")
            except Exception as e:
                # Log error in real application
                print(f"Error fetching secrets: {e}")

@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.fetch_secrets()
    return settings
