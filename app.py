from fastapi import FastAPI
import os

from api.APIHandler import APIHandler
from common.ApplicationContext import ApplicationContext
from data.db_helper import get_db_connection_pool
from dispatcher.dispatcher import decorate_api_functions
import api.parcels_api

app = FastAPI()

app_mode = os.environ["app_mode"]

if app_mode != "dispatcher":
    ApplicationContext.connection_pool = get_db_connection_pool()

ApplicationContext.app = app
APIHandler(app)

