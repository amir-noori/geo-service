
from shapely import wkt
import os

from geoservice.data.db_helper import execute_query
from geoservice.data.DBResult import DBResult
from geoservice.common.constants import *
from geoservice.gis.model.models import Point_T
from geoservice.util.gis_util import union_polygons_by_wkt
from geoservice.model.entity.Parcel import *
from geoservice.service.util import process_label
from geoservice.service.deed_service import find_deed
from geoservice.util.common_util import get_state_name_by_code
from geoservice.exception.common import ErrorCodes
from geoservice.exception.service_exception import ServiceException
from log.logger import logger


log = logger()


QUERIES = {
    "query_centroid_by_point": """
        SELECT SDO_UTIL.TO_WKTGEOMETRY(c.POLY) as POLY,
        TXT_LABLE as LABEL,
        nvl(
               SUBSTR(substr(TXT_LABLE, 8), INSTR(substr(TXT_LABLE, 8), 'BB') + 2,
                      INSTR(substr(TXT_LABLE, 8), 'EE') - INSTR(substr(TXT_LABLE, 8), 'BB') - 2), 0
           ) AS AREA
        from gis.CENTROID c
        WHERE 
        DEL_USER is null and DEL_DATE is null and
        TXT_LABLE like '%*' and
        TXT_LABLE like '%DD%' and -- exclude malformed labels
        VALIDATE1 = '1' and
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
        from gis.SHAPE s
        WHERE 
            DEL_USER is null and DEL_DATE is null and
            LABLE1 like '%*' and
            LABLE1 like '%DD%' and -- exclude malformed labels
            LABLE1 not like '%TASBITED%' and
            poly is not null and -- there might be multiple records for a shape but the one with poly is needed
            SDO_CONTAINS(s.POLY,
                    sdo_geometry('POINT ({x} {y})', {srid})
            ) = 'TRUE' and
            VALIDATE1 = '1' and
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
    """,

    "query_centorid_polygon_list_by_point": """
        select SDO_UTIL.TO_WKTGEOMETRY(c.POLY) as POLY
        from gis.CENTROID c
        where SDO_RELATE(c.POLY,
                        SDO_GEOM.SDO_BUFFER(
                                SDO_GEOMETRY('POINT({x} {y})', {srid}),
                                SDO_DIM_ARRAY(
                                        SDO_DIM_ELEMENT('Longitude', -180, 180, 0.01),
                                        SDO_DIM_ELEMENT('Latitude', -180, 180, 0.01)
                                    ),
                                {distance}
                            )
                , 'mask=inside+touch+OVERLAPBDYINTERSECT+coveredby') = 'TRUE'
            and TXT_LABLE like '%*'
            and TXT_LABLE like '%DD%' -- exclude malformed labels
            and VALIDATE1 = '1'
            and DEL_USER is null and DEL_DATE is null
    """,

    "query_shape_polygon_list_by_point": """
        select SDO_UTIL.TO_WKTGEOMETRY(c.POLY) as POLY
        from gis.SHAPE c
        where SDO_RELATE(c.POLY,
                        SDO_GEOM.SDO_BUFFER(
                                SDO_GEOMETRY('POINT({x} {y})', {srid}),
                                SDO_DIM_ARRAY(
                                        SDO_DIM_ELEMENT('Longitude', -180, 180, 0.01),
                                        SDO_DIM_ELEMENT('Latitude', -180, 180, 0.01)
                                    ),
                                {distance}
                            )
                , 'mask=inside+touch+OVERLAPBDYINTERSECT+coveredby') = 'TRUE'
            and LABLE1 like '%*'
            and LABLE1 not like '%TASBITED%'
            and LABLE1 like '%DD%' -- exclude malformed labels
            and VALIDATE1 = '1'
            and DEL_USER is null and DEL_DATE is null
    """,
    
    "query_point_buffer": """
        select SDO_UTIL.TO_WKTGEOMETRY(SDO_GEOM.SDO_BUFFER(
                SDO_GEOMETRY('POINT({x} {y})', {srid}),
                SDO_DIM_ARRAY(
                        SDO_DIM_ELEMENT('Longitude', -180, 180, 0.01),
                        SDO_DIM_ELEMENT('Latitude', -180, 180, 0.01)
                    ),
                {distance}
            )) as BUFFER
        from dual
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
        """
         TODO: for some points (Tehran -> 35.756578727113194, 51.34700238704682) we have both shape and centorid polies
            it must be investigated further.
            for now lets not raise exception and return centroid poly which most probably is surrounded by shape poly
        """
        log.warning(f"multiple polygons found for centroid {centroid}. ignoring shape!")
        shape_parcel.polygon = None
        # raise ServiceException(ErrorCodes.MULTIPLE_PARCEL_FOUND)
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


def find_parcel_list_by_centroid(centroid: Point_T, distance: float):
    def run_poly(db_result: DBResult):
        results = db_result.results
        geometry_wkt_list = []
        for result in results:
            geometry_wkt = wkt.loads(str(result['POLY']))
            geometry_wkt_list.append(str(geometry_wkt))

        return geometry_wkt_list
    
    def run_buffer(db_result: DBResult):
        results = db_result.results
        buffer = None
        for result in results:
            geometry_wkt = wkt.loads(str(result['BUFFER']))
            buffer = str(geometry_wkt)

        return buffer

    query_centorid_polygon_list = QUERIES['query_centorid_polygon_list_by_point'].format(
        x=centroid.x, y=centroid.y, srid=centroid.srid, distance=distance)

    query_shape_polygon_list = QUERIES['query_shape_polygon_list_by_point'].format(
        x=centroid.x, y=centroid.y, srid=centroid.srid, distance=distance)
    
    query_buffer = QUERIES['query_point_buffer'].format(
        x=centroid.x, y=centroid.y, srid=centroid.srid, distance=distance)

    centroid_polygon_list = execute_query(query_centorid_polygon_list, run_poly)
    shape_polygon_list = execute_query(query_shape_polygon_list, run_poly)
    buffer = execute_query(query_buffer, run_buffer)

    return centroid_polygon_list + shape_polygon_list, buffer
