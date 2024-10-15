import logging
import os

def setup_logger(name: str) -> logging.Logger:
    level = os.getenv('LOG_LEVEL', 'INFO')  # Set default log level
    logger = logging.getLogger(name)
    
    if not logger.hasHandlers():  # Avoid adding multiple handlers
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))

        # Create console handler and set level
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(getattr(logging, level.upper(), logging.INFO))

        logFormat = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter(logFormat)
        consoleHandler.setFormatter(formatter)

        logger.addHandler(consoleHandler)

    return logger