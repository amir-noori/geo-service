import os

import oracledb

from geoservice.config import db


def init():
    # to support thick client for oracle version < 12
    if int(float(db['oracle_version'])) < 12:
        oracledb.init_oracle_client(os.environ['oracle_client_home'])

def init_session(connection, requestedTag):
    with connection.cursor() as cursor:
        cursor.execute("ALTER SESSION SET CURRENT_SCHEMA = " + db['schema'])


def get_connection(uname, pwd, url):
    init()
    connection = oracledb.connect(user=uname, password=pwd, dsn=url)
    init_session(connection, None)
    connection.current_schema = db['schema']
    return connection


def get_connection_pool(uname, pwd, url):
    init()
    pool = oracledb.create_pool(user=uname, password=pwd, dsn=url,
                                min=2, max=5, increment=1,
                                getmode=oracledb.POOL_GETMODE_NOWAIT,
                                session_callback=init_session)
    pool.current_schema = db['schema']
    return pool
