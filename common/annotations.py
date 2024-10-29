
from functools import wraps
from log.logger import logger


def deprecated(reason=""):

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            logger.warning(f"""
                    *********************************************
                                        Depricated
                    *********************************************
                        
                    using depricated function {fn}
                    reason: {reason}
                    """)
            return fn(*args, **kwargs)

        return wrapper
    return decorator
