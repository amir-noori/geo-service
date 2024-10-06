import oracledb
from config import db
import os

def init():
    # to support thick client for oracle version < 12
    if int(float(db['oracle_version'])) < 12:
        oracledb.init_oracle_client(os.environ['oracle_client_home'])

def get_connection(uname, pwd, url):
    init()
    connection = oracledb.connect(user=uname, password=pwd, dsn=url)
    return connection

def get_connection_pool(uname, pwd, url):
    init()
    pool = oracledb.create_pool(user=uname, password=pwd, dsn=url,
                            min=2, max=5, increment=1,
                            getmode=oracledb.POOL_GETMODE_NOWAIT)
    return pool
