"""tempmail-python is a Python library for generating and managing temporary email addresses using the 1secmail service.

## Example usage:
```python
from tempmail import EMail

email = EMail()

# ... request some email ...

msg = email.wait_for_message()
print(msg.body)  # Hello World!\n
```
"""

from .providers import OneSecMail as EMail

__all__ = ('EMail',)
