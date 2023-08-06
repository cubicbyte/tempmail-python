import random
import string
import functools

__all__ = ('random_string', 'cache')


def random_string(length: int):
    return ''.join(random.choices(string.ascii_lowercase, k=length))


def cache(func):
    """Cache the result of a function with saved type hints"""
    @functools.lru_cache
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
