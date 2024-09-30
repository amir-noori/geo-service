from fastapi import FastAPI

from api.APIHandler import APIHandler
from common.ApplicationContext import ApplicationContext
from data.db_helper import get_db_connection_pool

app = FastAPI()
ApplicationContext.connection_pool = get_db_connection_pool()
ApplicationContext.app = app

APIHandler(app)

