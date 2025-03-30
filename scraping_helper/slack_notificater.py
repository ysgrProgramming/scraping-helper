import requests
from pydantic import BaseModel
from requests.exceptions import RequestException


class SlackNotificater(BaseModel):
    webhook_url: str

    def notify(self, message: str) -> None:
        payload = {"text": message}
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=5)
            response.raise_for_status()
        except RequestException as e:
            print(f"Slack notification failed: {e}")
