from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import NotificationRequest, OTPRequest, OTPVerifyRequest, APIResponse, PubSubMessage
from app.core.pubsub import NotificationPublisher
from app.otp.service import OTPService
from app.notifications.email import SendGridEmailAdapter
from app.notifications.sms import TwilioSMSAdapter
import base64
import json
import structlog
from typing import Annotated

router = APIRouter()
logger = structlog.get_logger()

# Dependency providers
def get_notification_publisher():
    return NotificationPublisher()

def get_otp_service():
    return OTPService()

@router.post("/notify", response_model=APIResponse)
async def send_notification(
    request: NotificationRequest,
    publisher: Annotated[NotificationPublisher, Depends(get_notification_publisher)]
):
    """
    Asynchronously send a notification via Pub/Sub to ensure <100ms latency.
    """
    message_id = await publisher.publish_notification(
        notification_type=request.type,
        recipient=request.recipient,
        message=request.message,
        **(request.metadata or {})
    )
    
    if not message_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue notification"
        )
    
    return APIResponse(
        status="success",
        message="Notification queued successfully",
        data={"message_id": str(message_id)}
    )

@router.post("/otp/generate", response_model=APIResponse)
async def generate_otp(
    request: OTPRequest,
    otp_service: Annotated[OTPService, Depends(get_otp_service)]
):
    """Generate and store an OTP in Firestore."""
    otp = await otp_service.create_otp(request.identifier)
    # In a real app, this would be followed by sending an SMS/Email with the OTP
    return APIResponse(
        status="success",
        message="OTP generated and stored",
        data={"identifier": request.identifier} # Don't return the OTP in production!
    )

@router.post("/otp/verify", response_model=APIResponse)
async def verify_otp(
    request: OTPVerifyRequest,
    otp_service: Annotated[OTPService, Depends(get_otp_service)]
):
    """Verify and atomically consume an OTP from Firestore."""
    is_valid = await otp_service.validate_otp(request.identifier, request.otp)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    return APIResponse(
        status="success",
        message="OTP verified successfully"
    )

@router.post("/worker/process")
async def process_notification_worker(
    request: PubSubMessage
):
    """
    Pub/Sub Push endpoint. 
    This is triggered by Google Cloud Pub/Sub when a message is published to the topic.
    """
    try:
        # Pub/Sub data is base64 encoded
        decoded_data = base64.b64decode(request.message.data).decode("utf-8")
        data = json.loads(decoded_data)
        
        notification_type = data.get("type")
        recipient = data.get("recipient")
        message = data.get("message")
        metadata = data.get("metadata", {})

        logger.info("processing_worker_message", type=notification_type, recipient=recipient)

        if notification_type == "email":
            adapter = SendGridEmailAdapter()
        elif notification_type == "sms":
            adapter = TwilioSMSAdapter()
        else:
            logger.error("unsupported_notification_type", type=notification_type)
            return {"status": "error", "reason": "unsupported_type"}

        result = await adapter.send(recipient, message, **metadata)
        
        if result["status"] == "success":
            logger.info("notification_sent_successfully", message_id=result.get("message_id"))
        else:
            logger.error("notification_failed", error=result.get("message"))
            # In production, you might want to return a 500 here to trigger Pub/Sub retries
            # For now we return 200 to acknowledge receipt
            
        return {"status": "processed"}

    except Exception as e:
        logger.error("worker_error", error=str(e))
        # Return 200 to Pub/Sub to avoid infinite retry loops unless it's a transient error
        return {"status": "error", "detail": str(e)}
