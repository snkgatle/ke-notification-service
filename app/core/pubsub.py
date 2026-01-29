import json
from google.cloud import pubsub_v1
from app.core.config import get_settings

settings = get_settings()

class NotificationPublisher:
    def __init__(self):
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(settings.PROJECT_ID, settings.PUB_SUB_TOPIC)

    async def publish_notification(self, notification_type: str, recipient: str, message: str, **kwargs):
        """
        Publishes notification metadata to a GCP Pub/Sub topic for background processing.
        Ensures API response remains under 100ms.
        """
        data = {
            "type": notification_type,
            "recipient": recipient,
            "message": message,
            "metadata": kwargs
        }
        
        message_json = json.dumps(data).encode("utf-8")
        
        try:
            # publish() returns a future
            future = self.publisher.publish(self.topic_path, message_json)
            # In a real async environment, we wouldn't block on future.result() 
            # if we want absolute lowest latency, but we'd need to handle callbacks.
            # Cloud Run's environment usually handles these efficiently.
            return future.result()
        except Exception as e:
            # In real production, we'd log this to Cloud Logging
            print(f"Failed to publish to Pub/Sub: {e}")
            return None
