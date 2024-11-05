from fastapi import FastAPI
import os

from geoservice.api.APIHandler import APIHandler
from common.ApplicationContext import ApplicationContext
from geoservice.data.db_helper import get_db_connection_pool


"""
    TODO: authentication
"""


app = FastAPI()

app_mode = os.environ["app_mode"]
enable_api_mock = os.environ["enable_api_mock"]

if app_mode == "app":
    ApplicationContext.connection_pool = get_db_connection_pool()

ApplicationContext.app = app
APIHandler(app)

if app_mode == "dispatcher":
    if enable_api_mock == "false":
        from geoservice.api.parcels_api import load_states_polygons_list
        load_states_polygons_list()
