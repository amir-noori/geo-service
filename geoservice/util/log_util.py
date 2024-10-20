import os
from geoservice.log.logger import Handler
def logger():
    level = os.getenv('LOG_LEVEL', 'INFO')
    logFormat = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    return Handler(level=level,format=logFormat)