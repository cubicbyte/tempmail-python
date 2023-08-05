# Python Temp Email Library
**tempmail-python** is a Python library for generating and managing temporary email addresses using the 1secmail service. It provides functions for creating email addresses, checking for new messages, and retrieving message contents.

## Installation
You can install tempmail-python using pip:
```bash
pip install tempmail-python
```

Or you can install it from source:
```bash
pip install git+https://github.com/cubicbyte/tempmail-python.git
```

## Usage example

```python
import tempmail

# Create a new email address
email = tempmail.get_email()
print(email)

# Wait for a new message
msg = tempmail.wait_for_message(email)
print(msg['body'])

```
Output:
```python
# vhpeptbsne@1secmail.com
# Hello World!
```

Using message filters:
```python
import tempmail

email = tempmail.get_email()
print(email)

# Wait for a new message from a specific sender
msg = tempmail.wait_for_message(email, filter=lambda m: m['from'] == 'no-reply@example.com')
print(msg['body'])
```

## API

- `tempmail.get_email(username=None, domain=None)`: Generate a new email address.
- `tempmail.get_inbox(email)`: Retrieve a list of message IDs for the specified email address.
- `tempmail.get_message(email, id)`: Retrieve the contents of a message with the specified ID.
- `tempmail.wait_for_message(email, timeout=None, filter=None)`: Wait for a new message to arrive at the specified email address. You can optionally provide a timeout (in seconds) and a filter function to check the contents of the message.
- `tempmail.DOMAINS`: List of available email domains.

## License
tempmail-python is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
