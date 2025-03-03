import functools
import time
from typing import Callable


def measure_time(func: Callable):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = round(end_time - start_time, 2)
        print(f"Function '{func.__name__}' took {execution_time} seconds to execute")
        return result

    return wrapper


def measure_async_time(func: Callable):

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        execution_time = round(end_time - start_time, 2)
        print(f"Async function '{func.__name__}' took {execution_time} seconds to execute")
        return result

    return wrapper
