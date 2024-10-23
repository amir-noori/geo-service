
from functools import wraps
from log.logger import logger

def cached():
    """
        cache function return
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not hasattr(fn, "return_cached_value"):
                logger().error("setting empty cache attribute")
                fn.return_cached_value = {}
                                
            if not fn.return_cached_value:
                logger().error("getting cache value")
                value = fn(*args, **kwargs)
                logger().error("setting cache value")
                fn.return_cached_value = value
            
            return fn.return_cached_value

        return wrapper
    return decorator