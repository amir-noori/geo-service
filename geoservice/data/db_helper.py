
from geoservice.data.db import get_connection, get_connection_pool
from geoservice.data.DBResult import DBResult
from geoservice.common.ApplicationContext import ApplicationContext
from geoservice.config import db
from log.logger import logger


def get_db_connection():
    return get_connection(db['username'], db['password'], db['url'])    

def get_db_connection_pool():
    return get_connection_pool(db['username'], db['password'], db['url'])    

def execute_query(query, func):
    logger().error(query)
    connection = ApplicationContext.connection_pool.acquire()
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
    logger().error(query)
    connection = ApplicationContext.connection_pool.acquire()
    cursor = connection.cursor()
    cursor.execute(query, params)
    connection.commit()
    cursor.close()
    connection.close()