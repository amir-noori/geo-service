import os
from log.SimpleLogger import SimpleLogger


def logger():
    if not hasattr(logger, "log"):
        level = os.getenv('LOG_LEVEL', 'INFO')
        logFormat = os.getenv(
            'LOG_FORMAT', "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        logger.log = SimpleLogger(level=level, format=logFormat)

    return logger.log
