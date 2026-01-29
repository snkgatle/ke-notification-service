from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any

class NotificationRequest(BaseModel):
    recipient: str = Field(..., description="Phone number or Email address")
    message: str = Field(..., min_length=1)
    type: str = Field(..., pattern="^(sms|email)$")
    metadata: Optional[Dict[str, Any]] = None

class OTPRequest(BaseModel):
    identifier: str = Field(..., description="Unique identifier for the user (e.g., email or phone)")

class OTPVerifyRequest(BaseModel):
    identifier: str
    otp: str = Field(..., min_length=6, max_length=6)

class APIResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None

class PubSubMessage(BaseModel):
    """Schema for Google Cloud Pub/Sub Push messages."""
    message: Dict[str, Any] # Contains 'data' (base64) and 'attributes'
    subscription: str
