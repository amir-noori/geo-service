from fastapi import FastAPI
import os

from api.APIHandler import APIHandler
from common.ApplicationContext import ApplicationContext
from data.db_helper import get_db_connection_pool


from common.states import state_polygon_mapping
from gis.model.models import Poly_T
from common.constants import GLOBAL_SRID

def load_states_polygons():
    states_polygon_shape_map = {}
    for state_code, state_polygon in state_polygon_mapping.items():
        poly = Poly_T(wkt=state_polygon, srid=GLOBAL_SRID)
        states_polygon_shape_map[state_code] = poly.to_shapely()
    
    ApplicationContext.states_polygon_shape_map = states_polygon_shape_map

app = FastAPI()


app_mode = os.environ["app_mode"]

if app_mode != "dispatcher":
    ApplicationContext.connection_pool = get_db_connection_pool()
else:
    load_states_polygons()

ApplicationContext.app = app
APIHandler(app)

