
from geoservice.data.db import get_connection, get_connection_pool
from geoservice.data.DBResult import DBResult
from common.ApplicationContext import ApplicationContext
from geoservice.config import db
from log.logger import logger

log = logger()

def get_db_connection():
    connection = get_connection(db['username'], db['password'], db['url'])
    connection.current_schema = db['schema']
    return connection

def get_db_connection_pool():
    connection = get_connection_pool(db['username'], db['password'], db['url'])
    connection.current_schema = db['schema']
    return connection

def execute_query(query, func):
    log.debug(query)
    connection = ApplicationContext.connection_pool.acquire()
    connection.current_schema = db['schema']
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    results = [dict(zip(columns, row)) for row in rows]
    row_count = cursor.rowcount
    db_result = DBResult(row_count, results)
    function_return = func(db_result)
    cursor.close()
    connection.close()
    return function_return

def execute_insert(query, params):
    log.debug(query)
    connection = ApplicationContext.connection_pool.acquire()
    cursor = connection.cursor()
    cursor.execute(query, params)
    connection.commit()
    cursor.close()
    connection.close()