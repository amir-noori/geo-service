import oracledb

def get_connection(uname, pwd, url):
    connection = oracledb.connect(user=uname, password=pwd, dsn=url)
    return connection

def get_connection_pool(uname, pwd, url):
    pool = oracledb.create_pool(user=uname, password=pwd, dsn=url,
                            min=2, max=5, increment=1,
                            getmode=oracledb.POOL_GETMODE_NOWAIT)
    return pool
