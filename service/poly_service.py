
from shapely import wkt

from data.db_helper import execute_query
from data.DBResult import DBResult
from common.constants import *
from gis.model.models import Point_T

from exception.common import ErrorCodes
from exception.service_exception import ServiceException

def find_polygon_by_centroid(centroid: Point_T):
    
    query = f"""
        SELECT SDO_UTIL.TO_WKTGEOMETRY(c.POLY) as POLY
        FROM gis.CENTROID c
        WHERE SDO_CONTAINS(c.POLY,
                        sdo_geometry('POINT ({centroid.x} {centroid.y})', {centroid.srid})
                ) = 'TRUE'
    """

    def run(db_result: DBResult):
        row_count = db_result.row_count
        results = db_result.results
        if row_count == 0:
            raise ServiceException(ErrorCodes.NO_PARCEL_FOUND)
        elif row_count > 1:
            raise ServiceException(ErrorCodes.MULTIPLE_PARCEL_FOUND)
        
        geometry_wkt = ""
        for result in results:
            geometry_wkt = wkt.loads(str(result['POLY']))
            
        return geometry_wkt

    return execute_query(query, run)


    
    