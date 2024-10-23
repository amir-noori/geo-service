from abc import ABC, ABCMeta, abstractmethod
import logging
import os
import datetime
import threading

class SingletonMeta(metaclass=ABCMeta):
    _instances = {}
    # Initialize a lock to ensure thread-safe Singleton instantiation
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        # Acquire the lock to ensure thread safety
        with cls._lock:
            print('<SingletonMeta> in the _call_...')
            if cls not in cls._instances:
                cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class BaseLogger(SingletonMeta):
    @abstractmethod
    def debug(cls, message: str):
        pass
    @abstractmethod
    def info(cls, message: str):
        pass
    @abstractmethod
    def warning(cls, message: str):
        pass
    @abstractmethod
    def error(cls, message: str):
        pass
    @abstractmethod
    def critical(cls, message: str):
        pass

class SimpleLogger(BaseLogger):

    def __init__(self, level,format):
        # Create a logger object with the specified name
        self._logger = logging.getLogger('my_logger')
        # Set the logging level to input level
        self._logger.setLevel(level)

        # Create a console handler to log messages to the console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        log_dir=os.path.join(os.path.dirname(__file__), 'logs', 'debug.log')
        file_handler = logging.FileHandler(log_dir)
        file_handler.setLevel(level)
        # Define the log message format
        formatter = logging.Formatter(fmt=format)
        # Set the formatter for console/file handlers
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add the console/file handlers to the logger
        self._logger.addHandler(console_handler)
        self._logger.addHandler(file_handler)

    def debug(self, message: str):
        self._logger.debug(message)

    def info(self, message: str):
        self._logger.info(message)

    def warning(self, message: str):
        self._logger.warning(message)

    def error(self, message: str):
        self._logger.error(message)

    def critical(self, message: str):
        self._logger.critical(message)
