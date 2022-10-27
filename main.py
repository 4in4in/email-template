

from src.schemas import EmailType
from src.message import EmailMessage
import asyncio


recipient = "my_lovely_recipient@example.net"


message = EmailMessage(
    recipient=recipient,
    email_type=EmailType.EXAMPLE_TYPE,
    subject_payload={
        "capital": "London",
        "country": "Great Britain"
    },
    body_payload={
        "example-body": {
            "my-body-variable": "Hello from template!"
        }
    }
)

asyncio.run(message.send())