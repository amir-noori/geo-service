from fastapi import FastAPI
import os

from api.APIHandler import APIHandler
from common.ApplicationContext import ApplicationContext
from data.db_helper import get_db_connection_pool


"""
    TODO: exception db log
    TODO: authentication

"""


app = FastAPI()

app_mode = os.environ["app_mode"]

if app_mode == "app":
    ApplicationContext.connection_pool = get_db_connection_pool()

ApplicationContext.app = app
APIHandler(app)

if app_mode == "dispatcher":
    from api.parcels_api import load_states_polygons_list
    load_states_polygons_list()
