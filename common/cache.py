import time
from functools import wraps

from common.ApplicationContext import ApplicationContext
from log.logger import logger

log = logger()


# def cached():
#     """
#         cache function return
#     """
#     log = logger()
#     def decorator(fn):
#         @wraps(fn)
#         def wrapper(*args, **kwargs):
#             if not hasattr(fn, "return_cached_value"):
#                 log.debug("setting empty cache attribute")
#                 fn.return_cached_value = {}
#                 ApplicationContext.cached_functions[id(fn)] = fn
#
#             if not fn.return_cached_value:
#                 log.debug("setting cache value")
#                 value = fn(*args, **kwargs)
#                 fn.return_cached_value = value
#
#             return fn.return_cached_value
#
#         return wrapper
#     return decorator


# def clear_all_cache():
#     for function_id, function in ApplicationContext.cached_functions.items():
#         function.return_cached_value = None


def cached(seconds=300):
    def decorator(func):
        cache = {}

        @wraps(func)
        def wrapper(*args, **kwargs):

            if not hasattr(func, "is_cached_by_wrapper"):
                log.debug(f"setting is_cached_by_wrapper to true for {func}")
                func.is_cached_by_wrapper = True
                ApplicationContext.cached_functions[id(func)] = func

            # Create a unique key based on function arguments
            key = (args, frozenset(kwargs.items()))

            # Check if cached result exists and is still valid
            if key in cache:
                result, timestamp = cache[key]
                if time.time() - timestamp < seconds:
                    return result

            # Call the function and cache the result
            result = func(*args, **kwargs)
            cache[key] = (result, time.time())
            return result

        # Clear cache when timeout expires (optional)
        def clear_cache():
            current_time = time.time()
            expired_keys = [k for k, (_, t) in cache.items()
                            if current_time - t >= seconds]
            for k in expired_keys:
                del cache[k]

        wrapper.clear_cache = clear_cache
        return wrapper

    return decorator


def clear_all_cache():
    for function_id, function in ApplicationContext.cached_functions.items():
        function.clear_cache()
