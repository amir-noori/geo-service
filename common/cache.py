
from functools import wraps
from log.logger import logger
from common.ApplicationContext import ApplicationContext

def cached():
    """
        cache function return
    """
    log = logger()
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not hasattr(fn, "return_cached_value"):
                log.debug("setting empty cache attribute")
                fn.return_cached_value = {}
                ApplicationContext.cached_functions[id(fn)] = fn
                                
            if not fn.return_cached_value:
                log.debug("setting cache value")
                value = fn(*args, **kwargs)
                fn.return_cached_value = value
            
            return fn.return_cached_value

        return wrapper
    return decorator

def clear_all_cache():
    for function_id, function in ApplicationContext.cached_functions.items():
        function.return_cached_value = None