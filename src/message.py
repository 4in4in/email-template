
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict

import aiosmtplib
import yaml
from bs4 import BeautifulSoup

from src.schemas import EmailProperties, EmailType
from src.settings import Settings

settings = Settings()

email_type_map: Dict[str, EmailProperties] = dict()

with open("data/subjects.yml") as file:
    raw_subjects = yaml.load(file, yaml.SafeLoader)
    for email_type in EmailType:
        email_type_map[email_type] = EmailProperties(
            **raw_subjects[email_type]
        )


class EmailMessage:
    def __init__(
        self,
        recipient: str,
        email_type: EmailType,
        subject_payload: Dict[str, str] = None,
        body_payload: Dict[str, Dict[str, str]] = None
    ) -> None:
        if email_type not in email_type_map:
            raise Exception("no such type")

        self.__content_items = ["logo.png"]
        self.__templates_path = "templates"
        self.__content_items_path = "data/images"

        self.__recipient = recipient
        self.__email_props: EmailProperties = email_type_map[email_type]

        if subject_payload:
            self.__email_props.subject = \
                self.__email_props.subject.format(**subject_payload)

        self.__body_payload = body_payload or dict()

        self.multipart_message = self.__create_multipart_email()

    def __create_multipart_email(self) -> MIMEMultipart:
        message = MIMEMultipart("related")
        message["Subject"] = self.__email_props.subject
        message["From"] = settings.email_address
        message["To"] = self.__recipient
        message.preamble = "This is a multi-part message in MIME format."

        alternative = MIMEMultipart("alternative")
        message.attach(alternative)

        raw_html_content = self.__create_html()

        plain_text = MIMEText(
            self.__get_plain_text_from_html(raw_html_content)
        )
        alternative.attach(plain_text)

        html_content = MIMEText(raw_html_content, "html")
        alternative.attach(html_content)

        for filename in self.__content_items:
            fp = open(f"{self.__content_items_path}/{filename}", "rb")
            image = MIMEImage(fp.read())
            fp.close()
            image.add_header("Content-ID", f"<{filename}>")
            message.attach(image)

        return message

    def __create_section(self, section_name: str) -> BeautifulSoup:
        with open(f"{self.__templates_path}/{section_name}.html") as file:
            section = BeautifulSoup(file.read(), "html.parser")
            section_payload = self.__body_payload.get(section_name)
            if not section_payload:
                return section

            for tag_id in section_payload:
                element = section.find(id=tag_id)
                element.clear()
                element.append(section_payload[tag_id])

            return section

    def __get_plain_text_from_html(self, html: str) -> str:
        soup = BeautifulSoup(html, features="html.parser")
        lines = soup.get_text().split("\n")
        normailzed_lines = (line.strip() for line in lines if line != "")

        return "\n".join(normailzed_lines)

    def __create_html(self) -> str:
        soup = None

        with open(f"{self.__templates_path}/base.html") as file:
            soup = BeautifulSoup(file.read(), "html.parser")

        for section_name in self.__email_props.sections:
            section = self.__create_section(section_name)
            soup.main.insert(-1, section)

        return str(soup)

    async def send(self) -> None:
        await aiosmtplib.send(
            message=self.multipart_message,
            hostname=settings.email_host,
            port=settings.email_port,
            username=settings.email_address,
            password=settings.email_password,
            use_tls=True,
        )
