import os
from log.SimpleLogger import SimpleLogger
def logger():
    level = os.getenv('LOG_LEVEL', 'INFO')
    logFormat = os.getenv('LOG_FORMAT', "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    return SimpleLogger(level=level,format=logFormat)