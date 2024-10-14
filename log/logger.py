import logging
import os

def setup_logger(name: str) -> logging.Logger:
    level = os.getenv('LOG_LEVEL', 'INFO')  # Set default log level
    logger = logging.getLogger(name)
    
    if not logger.hasHandlers():  # Avoid adding multiple handlers
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))

        ch = logging.StreamHandler()
        ch.setLevel(getattr(logging, level.upper(), logging.INFO))

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        logger.addHandler(ch)

    return logger