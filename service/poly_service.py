
from shapely import wkt

from data.db_helper import execute_query
from data.DBResult import DBResult
from common.constants import *
from gis.model.models import Point_T

from exception.common import ErrorCodes
from exception.service_exception import ServiceException

def find_polygon_by_centroid(centroid: Point_T):
    
    query_centroid = f"""
        SELECT SDO_UTIL.TO_WKTGEOMETRY(c.POLY) as POLY
        FROM gis.CENTROID c
        WHERE 
        DEL_USER is null and DEL_USER is null and
        TXT_LABLE like '%*' and
        SDO_CONTAINS(c.POLY,
                sdo_geometry('POINT ({centroid.y} {centroid.x})', {centroid.srid})
        ) = 'TRUE'
    """
    
    query_shape = f"""
        SELECT SDO_UTIL.TO_WKTGEOMETRY(s.POLY) as POLY
        FROM gis.SHAPE s
        WHERE 
            DEL_USER is null and DEL_USER is null and
            LABLE1 like '%*' and
            SDO_CONTAINS(s.POLY,
                    sdo_geometry('POINT ({centroid.x} {centroid.y})', {centroid.srid})
            ) = 'TRUE'
    """

    def run(db_result: DBResult):
        row_count = db_result.row_count
        results = db_result.results
        if row_count == 0:
            return ""
        elif row_count > 1:
            raise ServiceException(ErrorCodes.MULTIPLE_PARCEL_FOUND)
        
        geometry_wkt = ""
        for result in results:
            geometry_wkt = wkt.loads(str(result['POLY']))
            
        return geometry_wkt

    centroid_polygon = ""
    shape_polygon = ""
    centroid_polygon = execute_query(query_centroid, run)
    shape_polygon = execute_query(query_shape, run)
    
    if centroid_polygon == "" and shape_polygon == "":
        raise ServiceException(ErrorCodes.NO_PARCEL_FOUND)
    elif centroid_polygon and shape_polygon:
        raise ServiceException(ErrorCodes.MULTIPLE_PARCEL_FOUND)
    else:
        if shape_polygon:
            return shape_polygon
        elif centroid_polygon:
            return centroid_polygon


    
    