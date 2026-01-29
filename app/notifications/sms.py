from typing import Any, Dict
from twilio.rest import Client
from app.notifications.base import BaseNotifier
from app.core.config import get_settings

settings = get_settings()

class TwilioSMSAdapter(BaseNotifier):
    def __init__(self):
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        else:
            self.client = None

    async def send(self, recipient: str, message: str, **kwargs: Any) -> Dict[str, Any]:
        if not self.client:
            return {"status": "error", "message": "Twilio client not initialized"}
        
        try:
            # Twilio's client.messages.create is a blocking call, 
            # in a high-throughput environment we'd use a thread pool or an async alternative
            # for the sake of this implementation, we simulate the logic.
            result = self.client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=recipient
            )
            return {"status": "success", "message_id": result.sid}
        except Exception as e:
            return {"status": "error", "message": str(e)}
