from data.db import get_connection_pool
from config import db

class ApplicationContext:
    connection_pool = None

    @classmethod
    def initialize_connection_pool(cls):
        """Initialize the connection pool for the Oracle database."""
        if cls.connection_pool is None:
            cls.connection_pool = get_connection_pool(
                db['username'], db['password'], db['url']
            )
            print("Connection pool initialized.")

    @classmethod
    def get_connection_pool(cls):
        """Get the connection pool, initializing it if necessary."""
        if cls.connection_pool is None:
            cls.initialize_connection_pool()
        return cls.connection_pool