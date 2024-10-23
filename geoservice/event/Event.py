
from log.logger import logger

class Event:
    def __init__(self, handler):
        self.handlers = set()
        self.handler = handler

    def fire(self, *args, **kargs):
        logger().error("fire: ", self.handler)
        return self.handler(*args, **kargs)

    __call__ = fire
