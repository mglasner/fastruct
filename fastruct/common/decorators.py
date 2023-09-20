"""Common Decorators."""
import time
from collections.abc import Callable
from functools import wraps
from typing import Any


def timer(func: Callable) -> Callable:
    """Decorator for measuring function execution time.

    Args:
        func (Callable): The function to be measured.

    Returns:
        Callable: The decorated function.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"{func.__name__} took {elapsed_time:.5f} seconds to run.")
        return result

    return wrapper
