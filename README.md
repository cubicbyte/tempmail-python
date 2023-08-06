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

## Examples

Receive a message (e.g. activation code)
```python
from tempmail import EMail

email = EMail()

# ... request some email ...

msg = email.wait_for_message()
print(msg.body)  # Hello World!\n
```

Get all messages in the inbox
```python
from tempmail import EMail

email = EMail(username='example', domain='1secmail.com')
inbox = email.get_inbox()

for msg_info in inbox:
    print(msg_info.subject, msg_info.message.body)
```

Download an attachment
```python
from tempmail import EMail

email = EMail('example@1secmail.com')
msg = email.wait_for_message()

if msg.attachments:
    attachment = msg.attachments[0]
    data = attachment.download()

    # Print
    print(data)  # b'Hello World!\n'
    print(data.decode('utf-8'))  # Hello World!\n

    # Save to file
    with open(attachment.filename, 'wb') as f:
        f.write(data)
```

## License
tempmail-python is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
