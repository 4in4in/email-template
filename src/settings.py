
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    email_host = os.environ.get("email_host")
    email_port = os.environ.get("email_port")
    email_address = os.environ.get("email_address")
    email_username = os.environ.get("email_username")
    email_password = os.environ.get("email_password")
