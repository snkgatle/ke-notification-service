from typing import Any, Dict
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.notifications.base import BaseNotifier
from app.core.config import get_settings

settings = get_settings()

class SendGridEmailAdapter(BaseNotifier):
    def __init__(self):
        if settings.SENDGRID_API_KEY:
            self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)
        else:
            self.client = None

    async def send(self, recipient: str, message: str, **kwargs: Any) -> Dict[str, Any]:
        if not self.client:
            return {"status": "error", "message": "SendGrid client not initialized"}
        
        subject = kwargs.get("subject", "Notification")
        message_obj = Mail(
            from_email=settings.SENDGRID_FROM_EMAIL,
            to_emails=recipient,
            subject=subject,
            plain_text_content=message
        )
        
        try:
            response = self.client.send(message_obj)
            return {"status": "success", "message_id": response.headers.get("X-Message-Id", "N/A")}
        except Exception as e:
            return {"status": "error", "message": str(e)}
