import random
import string


def random_string(length: int):
    return ''.join(random.choices(string.ascii_lowercase, k=length))
