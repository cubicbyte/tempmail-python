import time
import random
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict

import requests

from . import utils

__all__ = ('OneSecMail',)


class OneSecMail:
    """1secmail.com API wrapper"""

    inbox_update_interval = 0.5
    """How often to update the inbox in seconds"""

    def __init__(self, address: Optional[str] = None, username: Optional[str] = None, domain: Optional[str] = None) -> None:
        """Create a new 1secmail.com email address

        :param address: The full email address (username@domain)
        :param username: The username of the email address (before the @)
        :param domain: The domain of the email address (after the @)
        """

        if address is not None:
            username, domain = address.split('@')

        if domain is not None and domain not in self.get_domains():
            raise ValueError(f'Invalid domain: {domain}')

        self._session = requests.Session()
        self.username = username or utils.random_string(10)
        """The username of the email address (before the @)"""
        self.domain = domain or random.choice(self.get_domains())
        """The domain of the email address (after the @)"""

    def get_inbox(self) -> List['OneSecMail.MessageInfo']:
        """Get the inbox of the email address"""
        resp = self._session.get(f'https://www.1secmail.com/api/v1/?action=getMessages&login={self.username}&domain={self.domain}')
        resp.raise_for_status()
        return [OneSecMail.MessageInfo.from_dict(self, msg_info) for msg_info in resp.json()]

    @utils.cache
    def get_message(self, id: int) -> 'OneSecMail.Message':
        """Get a message from the inbox"""
        resp = self._session.get(f'https://www.1secmail.com/api/v1/?action=readMessage&login={self.username}&domain={self.domain}&id={id}')
        resp.raise_for_status()
        return OneSecMail.Message.from_dict(self, resp.json())

    @utils.cache
    def download_attachment(self, id: int, file: str) -> bytes:
        """Download an attachment from a message as bytes"""
        resp = self._session.get(f'https://www.1secmail.com/api/v1/?action=download&login={self.username}&domain={self.domain}&id={id}&file={file}')
        resp.raise_for_status()
        return resp.content

    def wait_for_message(self, timeout: Optional[int] = 60, filter: callable = lambda _: True) -> 'OneSecMail.Message':
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
            time.sleep(OneSecMail.inbox_update_interval)

        raise TimeoutError('Timed out waiting for message')

    @staticmethod
    @utils.cache
    def get_domains() -> Tuple[str, ...]:
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
        """Information about a message in the inbox"""

        id: int
        "Message ID"
        from_addr: str
        "Sender email address"
        subject: str
        "Subject of the message"
        date_str: str
        "Date the message was received in format YYYY-MM-DD HH:MM:SS"
        _mail_instance: 'OneSecMail'

        @property
        def date(self) -> datetime:
            """Date the message was received"""
            return datetime.fromisoformat(self.date_str)

        @property
        def message(self) -> 'OneSecMail.Message':
            """The full message"""
            return self._mail_instance.get_message(self.id)

        @classmethod
        def from_dict(cls, mail_instance: 'OneSecMail', msg_info: Dict[str, any]) -> 'OneSecMail.MessageInfo':
            """Create a MessageInfo from a raw api response"""
            return cls(
                _mail_instance=mail_instance,
                id=msg_info['id'],
                from_addr=msg_info['from'],
                subject=msg_info['subject'],
                date_str=msg_info['date'],
                )

    @dataclass
    class Message:
        """Email message"""

        id: int
        "Message ID"
        from_addr: str
        "Sender email address"
        subject: str
        "Subject of the message"
        date_str: str
        "Date the message was received in format YYYY-MM-DD HH:MM:SS"
        body: str
        "Message body (html if exists, text otherwise)"
        text_body: str
        "Message body (text format)"
        html_body: str
        "Message body (html format)"
        _mail_instance: 'OneSecMail'
        _attachments: list[dict[str, any]]

        @property
        def date(self) -> datetime:
            """Date the message was received"""
            return datetime.fromisoformat(self.date_str)

        @property
        def attachments(self) -> List['OneSecMail.Attachment']:
            """List of attachments in the message (files)"""
            return [OneSecMail.Attachment.from_dict(self._mail_instance, self.id, attachment) for attachment in self._attachments]

        @classmethod
        def from_dict(cls, mail_instance: 'OneSecMail', msg: Dict[str, any]) -> 'OneSecMail.Message':
            """Create a Message from a raw api response"""
            return cls(
                _mail_instance=mail_instance,
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
        """Email attachment"""

        filename: str
        "Name of the file of the attachment"
        content_type: str
        "MIME type of the attachment"
        size: int
        "Size of the attachment in bytes"
        _mail_instance: 'OneSecMail'
        _message_id: int

        def download(self) -> bytes:
            """Download the attachment as bytes"""
            return self._mail_instance.download_attachment(self._message_id, self.filename)

        @classmethod
        def from_dict(cls, mail_instance: 'OneSecMail', message_id: int, attachment: Dict[str, any]) -> 'OneSecMail.Attachment':
            """Create an Attachment from a raw api response"""
            return cls(
                _mail_instance=mail_instance,
                _message_id=message_id,
                filename=attachment['filename'],
                content_type=attachment['contentType'],
                size=attachment['size'],
                )
