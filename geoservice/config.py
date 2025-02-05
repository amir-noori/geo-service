import os

db = {
    "oracle_version": os.environ['oracle_version'],
    "username": os.environ['db_username'],
    "password": os.environ['db_password'],
    "schema": os.environ['db_schema'],
    "url": f"{os.environ['db_ip']}:{os.environ['db_port']}/{os.environ['db_service']}"
}
