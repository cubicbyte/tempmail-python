"""tempmail-python is a Python library for generating and managing temporary email addresses using the 1secmail service.

Example usage:
```python
import py_tempmail

email = py_tempmail.get_email()
print(f"Your email address is {email}")

print("Waiting for a message...")
message = py_tempmail.wait_for_message(email)
print(f"New message received: {message['subject']}")```
"""

import time
import random
from functools import cache

import requests

from . import utils

__all__ = ('get_email', 'get_inbox', 'get_message', 'wait_for_message', 'DOMAINS')

DOMAINS = [
    '1secmail.com',
    '1secmail.org',
    '1secmail.net',
    'kzccv.com',
    'qiott.com',
    'wuuvo.com',
    'icznn.com',
    'ezztt.com',
    ]
"""List of allowed email domains"""


@cache
def _check_message(email: str, id: int, filter: callable) -> tuple[bool, dict[str, any]]:
    """Check if a message matches the filter"""
    message = get_message(email, id)
    return filter(message), message


def get_email(username: str | None = None, domain: str | None = None) -> str:
    """Generate an email address"""
    if username is None:
        username = utils.random_string(10)
    if domain is None:
        domain = random.choice(DOMAINS)
    return f'{username}@{domain}'


def get_inbox(email: str) -> list[dict[str, any]]:
    """Get the inbox of the email address"""
    username, domain = email.split('@')

    if domain not in DOMAINS:
        raise ValueError(f'Invalid domain: {domain}')

    resp = requests.get(f'https://www.1secmail.com/api/v1/?action=getMessages&login={username}&domain={domain}')
    return resp.json()


def get_message(email: str, id: int) -> dict[str, any]:
    """Get a message from the inbox"""
    username, domain = email.split('@')

    if domain not in DOMAINS:
        raise ValueError(f'Invalid domain: {domain}')

    resp = requests.get(f'https://www.1secmail.com/api/v1/?action=readMessage&login={username}&domain={domain}&id={id}')
    return resp.json()


def wait_for_message(email: str, timeout: int | None = 60, filter: callable = lambda _: True) -> dict[str, any]:
    """Wait for a message to arrive in the inbox"""
    username, domain = email.split('@')

    if domain not in DOMAINS:
        raise ValueError(f'Invalid domain: {domain}')

    timeout_time = time.time() + timeout if timeout else None
    while timeout is None or time.time() < timeout_time:
        resp = requests.get(f'https://www.1secmail.com/api/v1/?action=getMessages&login={username}&domain={domain}').json()

        if resp:
            for msg_info in resp:
                status, msg = _check_message(email, msg_info['id'], filter)
                if status:
                    return msg

        time.sleep(1)

    raise TimeoutError('Timed out waiting for message')
