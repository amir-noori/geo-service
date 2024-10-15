from log.logger import setup_logger

def get_logger(name: str):
    """Returns a logger with the specified name."""
    return setup_logger(name)