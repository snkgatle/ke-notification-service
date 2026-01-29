from typing import Any, Dict
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from app.notifications.base import BaseNotifier
from app.core.config import get_settings

settings = get_settings()

class BrevoEmailAdapter(BaseNotifier):
    def __init__(self):
        if settings.BREVO_API_KEY:
            self.configuration = sib_api_v3_sdk.Configuration()
            self.configuration.api_key['api-key'] = settings.BREVO_API_KEY
            self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(self.configuration))
        else:
            self.api_instance = None

    async def send(self, recipient: str, message: str, **kwargs: Any) -> Dict[str, Any]:
        if not self.api_instance:
            return {"status": "error", "message": "Brevo client not initialized"}
        
        subject = kwargs.get("subject", "Notification")
        sender = {"name": "Notification Service", "email": settings.BREVO_FROM_EMAIL}
        to = [{"email": recipient}]
        
        # Brevo supports HTML and text content
        html_content = kwargs.get("html_content", f"<html><body><p>{message}</p></body></html>")
        
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=to,
            sender=sender,
            subject=subject,
            html_content=html_content,
            text_content=message
        )
        
        try:
            api_response = self.api_instance.send_transac_email(send_smtp_email)
            return {"status": "success", "message_id": getattr(api_response, 'message_id', 'N/A')}
        except ApiException as e:
            return {"status": "error", "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
