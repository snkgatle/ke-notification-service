from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseNotifier(ABC):
    @abstractmethod
    async def send(self, recipient: str, message: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Abstract method to send a notification.
        :param recipient: Recipient identifier (phone number or email).
        :param message: The content of the notification.
        :param kwargs: Additional metadata (subject, template_id, etc.)
        :return: Result dictionary with status and message_id.
        """
        pass
