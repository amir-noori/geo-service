
from functools import wraps
from log.logger import logger

log = logger()

def cached():
    """
        cache function return
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not hasattr(fn, "return_cached_value"):
                log.debug("setting empty cache attribute")
                fn.return_cached_value = {}
                                
            if not fn.return_cached_value:
                log.debug("getting cache value")
                value = fn(*args, **kwargs)
                log.debug("setting cache value")
                fn.return_cached_value = value
            
            return fn.return_cached_value

        return wrapper
    return decorator