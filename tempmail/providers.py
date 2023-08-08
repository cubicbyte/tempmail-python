import time
import random
from datetime import datetime
from dataclasses import dataclass

import requests

from . import utils

__all__ = ('OneSecMail',)


class OneSecMail:
    """1secmail.com API wrapper"""

    def __init__(self, email: str | None = None, username: str | None = None, domain: str | None = None) -> None:
        if email is not None:
            username, domain = email.split('@')

        if domain is not None and domain not in self.get_domains():
            raise ValueError(f'Invalid domain: {domain}')

        self.session = requests.Session()
        self.username = username or utils.random_string(10)
        self.domain = domain or random.choice(self.get_domains())

    def get_inbox(self) -> list['OneSecMail.MessageInfo']:
        """Get the inbox of the email address"""
        resp = self.session.get(f'https://www.1secmail.com/api/v1/?action=getMessages&login={self.username}&domain={self.domain}')
        resp.raise_for_status()
        return [OneSecMail.MessageInfo.from_dict(self, msg_info) for msg_info in resp.json()]

    @utils.cache
    def get_message(self, id: int) -> 'OneSecMail.Message':
        """Get a message from the inbox"""
        resp = self.session.get(f'https://www.1secmail.com/api/v1/?action=readMessage&login={self.username}&domain={self.domain}&id={id}')
        resp.raise_for_status()
        return OneSecMail.Message.from_dict(self, resp.json())

    @utils.cache
    def download_attachment(self, id: int, file: str) -> bytes:
        """Download an attachment from a message as bytes"""
        resp = self.session.get(f'https://www.1secmail.com/api/v1/?action=download&login={self.username}&domain={self.domain}&id={id}&file={file}')
        resp.raise_for_status()
        return resp.content

    def wait_for_message(self, timeout: int | None = 60, filter: callable = lambda _: True) -> 'OneSecMail.Message':
        """Wait for a message to arrive in the inbox
        
        :param timeout: How long to wait for a message to arrive, in seconds
        :param filter: A message filter function that takes a message and returns a boolean
        """

        timeout_time = time.time() + timeout if timeout is not None else None

        while timeout is None or time.time() < timeout_time:
            inbox = self.get_inbox()
            for msg_info in inbox:
                if filter(msg_info.message):
                    return msg_info.message
            time.sleep(1)

        raise TimeoutError('Timed out waiting for message')

    @staticmethod
    @utils.cache
    def get_domains() -> tuple[str, ...]:
        """List of allowed email domains"""
        resp = requests.get('https://www.1secmail.com/api/v1/?action=getDomainList')
        resp.raise_for_status()
        return tuple(resp.json())

    @property
    def address(self) -> str:
        """The full email address"""
        return f'{self.username}@{self.domain}'

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} address={self.address!r}>'

    def __str__(self) -> str:
        return self.address

    @dataclass
    class MessageInfo:
        id: int
        from_addr: str
        subject: str
        date_str: str
        _mail: 'OneSecMail'

        @property
        def date(self) -> datetime:
            return datetime.fromisoformat(self.date_str)

        @property
        def message(self) -> 'OneSecMail.Message':
            return self._mail.get_message(self.id)

        @classmethod
        def from_dict(cls, mail: 'OneSecMail', msg_info: dict[str, any]) -> 'OneSecMail.MessageInfo':
            return cls(
                _mail=mail,
                id=msg_info['id'],
                from_addr=msg_info['from'],
                subject=msg_info['subject'],
                date_str=msg_info['date'],
                )

    @dataclass
    class Message:
        id: int
        from_addr: str
        subject: str
        date_str: str
        body: str
        text_body: str
        html_body: str
        _mail: 'OneSecMail'
        _attachments: list[dict[str, any]]

        @property
        def date(self) -> datetime:
            return datetime.fromisoformat(self.date_str)

        @property
        def attachments(self) -> list['OneSecMail.Attachment']:
            return [OneSecMail.Attachment.from_dict(self._mail, self.id, attachment) for attachment in self._attachments]

        @classmethod
        def from_dict(cls, mail: 'OneSecMail', msg: dict[str, any]) -> 'OneSecMail.Message':
            return cls(
                _mail=mail,
                _attachments=msg['attachments'],
                id=msg['id'],
                from_addr=msg['from'],
                subject=msg['subject'],
                date_str=msg['date'],
                body=msg['body'],
                text_body=msg['textBody'],
                html_body=msg['htmlBody'],
                )

    @dataclass
    class Attachment:
        filename: str
        content_type: str
        size: int
        _mail: 'OneSecMail'
        _message_id: int

        def download(self) -> bytes:
            """Download the attachment as bytes"""
            return self._mail.download_attachment(self._message_id, self.filename)

        @classmethod
        def from_dict(cls, mail: 'OneSecMail', message_id: int, attachment: dict[str, any]) -> 'OneSecMail.Attachment':
            return cls(
                _mail=mail,
                _message_id=message_id,
                filename=attachment['filename'],
                content_type=attachment['contentType'],
                size=attachment['size'],
                )
