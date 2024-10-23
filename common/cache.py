
from functools import wraps



def cached():
    """
        cache function return
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not hasattr(fn, "return_cached_value"):
                print("setting empty cache attribute")
                fn.return_cached_value = {}
                                
            if not fn.return_cached_value:
                print("getting cache value")
                value = fn(*args, **kwargs)
                print("setting cache value")
                fn.return_cached_value = value
            
            return fn.return_cached_value

        return wrapper
    return decorator