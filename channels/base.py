from abc import ABC, abstractmethod


class BaseChannel(ABC):
    @abstractmethod
    def notify(self, critical_emails: list[dict]) -> None:
        """Send notification for critical emails."""
