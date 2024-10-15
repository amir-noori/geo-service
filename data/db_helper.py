
from data.db import get_connection, get_connection_pool
from .DBResult import DBResult
from common.ApplicationContext import ApplicationContext

from config import db

def get_db_connection():
    return get_connection(db['username'], db['password'], db['url'])    

def get_db_connection_pool():
    return get_connection_pool(db['username'], db['password'], db['url'])    

def execute_query(query, func):
    print(query)
    connection = ApplicationContext.connection_pool.acquire()
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    results = [dict(zip(columns, row)) for row in rows]
    row_count = cursor.rowcount
    db_result = DBResult(row_count, results)
    function_return = func(db_result)
    connection.close()
    return function_return