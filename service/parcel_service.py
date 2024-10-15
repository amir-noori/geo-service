
from shapely import wkt
import os

from data.db_helper import execute_query
from data.DBResult import DBResult
from common.constants import *
from gis.model.models import Point_T
from util.gis_util import union_polygons_by_wkt
from model.entity.Parcel import *
from service.util import process_label
from service.deed_service import find_deed
from util.common_util import get_state_name_by_code

from exception.common import ErrorCodes
from exception.service_exception import ServiceException


QUERIES = {
    "query_centroid_by_point": """
        SELECT SDO_UTIL.TO_WKTGEOMETRY(c.POLY) as POLY,
        TXT_LABLE as LABEL,
        nvl(
               SUBSTR(substr(TXT_LABLE, 8), INSTR(substr(TXT_LABLE, 8), 'BB') + 2,
                      INSTR(substr(TXT_LABLE, 8), 'EE') - INSTR(substr(TXT_LABLE, 8), 'BB') - 2), 0
           ) AS AREA
        FROM gis.CENTROID c
        WHERE 
        DEL_USER is null and DEL_DATE is null and
        TXT_LABLE like '%*' and
        SDO_CONTAINS(c.POLY,
                sdo_geometry('POINT ({x} {y})', {srid})
        ) = 'TRUE'
    """,

    "query_shape_by_point": """
        SELECT SDO_UTIL.TO_WKTGEOMETRY(s.POLY) as POLY,
        LABLE1 as LABEL,
        nvl(
               SUBSTR(substr(lable1, 8), INSTR(substr(lable1, 8), 'BB') + 2,
                      INSTR(substr(lable1, 8), 'EE') - INSTR(substr(lable1, 8), 'BB') - 2), 0
           ) AS AREA
        FROM gis.SHAPE s
        WHERE 
            DEL_USER is null and DEL_DATE is null and
            LABLE1 like '%*' and
            poly is not null and -- there might be multiple records for a shape but the one with poly is needed
            SDO_CONTAINS(s.POLY,
                    sdo_geometry('POINT ({x} {y})', {srid})
            ) = 'TRUE' and
            ROWNUM = 1 -- to limit to the one polygon which is surrounded (the polygon with ring scenario)
    """,

    "query_state_polygon": """
        select SDO_UTIL.TO_WKTGEOMETRY(poly) as STATE_POLY
        from gis.shape
        where cms = lable1
            and area > 0
            and LEVEL1 || COLOR1 || STYLE1 || WEIGHT1 = '41503'
            and DEL_USER is null
            and poly is not null
    """
}


def find_state_polygon(state_code: str) -> str:

    def run(db_result: DBResult):
        results = db_result.results
        geometry_wkt_list = []
        for result in results:
            geometry_wkt_list.append(str(result['STATE_POLY']))
        
        geometry_wkt = union_polygons_by_wkt(geometry_wkt_list)

        return str(geometry_wkt)
    
    geometry_wkt = execute_query(QUERIES['query_state_polygon'], run)

    # geometry_wkt = ""
    # try:
    #     geometry_wkt = execute_query(QUERIES['query_state_polygon'], run)
    # except DatabaseError as e:
    #     error_obj, = e.args
    #     if error_obj.full_code == "ORA-30625":
    #         print("ORA-30625 -> ignored") # TODO: investigate
                   
    return Parcel(polygon=geometry_wkt)


def find_polygon_by_centroid(centroid: Point_T) -> Parcel:

    def run(db_result: DBResult):
        row_count = db_result.row_count
        results = db_result.results
        if row_count > 1:
            raise ServiceException(ErrorCodes.MULTIPLE_PARCEL_FOUND)

        geometry_wkt = None
        deed = None
        cms = None
        for result in results:
            geometry_wkt = wkt.loads(str(result['POLY']))
            label = str(result['LABEL'])
            area = str(result['AREA'])
            deed = process_label(label)
            deed.legal_area = area
            cms = deed.cms

        return Parcel(polygon=geometry_wkt, deed=deed, cms=cms)

    query_centroid = QUERIES['query_centroid_by_point'].format(
        x=centroid.x, y=centroid.y, srid=centroid.srid)
    query_shape = QUERIES['query_shape_by_point'].format(
        x=centroid.x, y=centroid.y, srid=centroid.srid)

    centroid_parcel = execute_query(query_centroid, run)
    shape_parcel = execute_query(query_shape, run)

    if not centroid_parcel.polygon and not shape_parcel.polygon:
        raise ServiceException(ErrorCodes.NO_PARCEL_FOUND)
    elif centroid_parcel.polygon and shape_parcel.polygon:
        raise ServiceException(ErrorCodes.MULTIPLE_PARCEL_FOUND)
    else:
        if shape_parcel.polygon:
            return shape_parcel
        elif centroid_parcel.polygon:
            return centroid_parcel


def find_parcel_info_by_centroid(centroid: Point_T) -> Parcel:
    parcel = find_polygon_by_centroid(centroid)
    deed = find_deed(parcel.deed)

    # : must be set in find_deed
    parcel.deed.address_text = deed.address_text
    parcel.deed.legal_area = deed.legal_area
    parcel.deed.partitioned = deed.partitioned
    parcel.deed.segment = deed.segment
    
    if deed.state and deed.state != None:
        parcel.deed.state = deed.state
    else:
        current_state_code = os.environ["current_state_code"]
        parcel.deed.state = get_state_name_by_code(current_state_code)

    return parcel
