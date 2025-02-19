import os

from shapely import wkt

from geoservice.common.constants import UTM_ZONE_38_SRID
from geoservice.common.layer import Layers
from geoservice.data.DBResult import DBResult
from geoservice.data.db_helper import execute_query
from geoservice.exception.common import ErrorCodes
from geoservice.exception.service_exception import ServiceException
from geoservice.model.entity.Parcel import *
from geoservice.model.entity.cms import CmsUnit
from geoservice.service.deed_service import find_deed
from geoservice.service.util import process_label
from geoservice.util.common_util import get_state_name_by_code
from geoservice.util.gis_util import union_polygons_by_wkt
from log.logger import logger

log = logger()

# noinspection SqlNoDataSourceInspection
QUERIES = {
    "query_centroid_by_point": """
        SELECT SDO_UTIL.TO_WKTGEOMETRY(c.POLY) as POLY,
        TXT_LABLE as LABEL,
        nvl(
               SUBSTR(substr(TXT_LABLE, 8), INSTR(substr(TXT_LABLE, 8), 'BB') + 2,
                      INSTR(substr(TXT_LABLE, 8), 'EE') - INSTR(substr(TXT_LABLE, 8), 'BB') - 2), 0
           ) AS AREA
        from CENTROID c
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
        from SHAPE s
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
        from shape
        where cms = lable1
            and area > 0
            and LEVEL1 || COLOR1 || STYLE1 || WEIGHT1 = '41503'
            and DEL_USER is null
            and poly is not null
    """,

    "query_all_cms_polygon": """
        select SDO_UTIL.TO_WKTGEOMETRY(poly) as CMS_POLY, cms as CMS
        from shape
        where cms = lable1
            and area > 0
            and LEVEL1 || COLOR1 || STYLE1 || WEIGHT1 = '41503'
            and DEL_USER is null
            and poly is not null
    """,

    "query_cms_polygon": """
        select SDO_UTIL.TO_WKTGEOMETRY(poly) as CMS_POLY, cms as CMS
        from shape
        where cms = lable1
            and cms = '{TARGET_CMS}'
            and area > 0
            and LEVEL1 || COLOR1 || STYLE1 || WEIGHT1 = '41503'
            and DEL_USER is null
            and poly is not null
    """,

    "query_centroid_polygon_list_by_point": """
        select SDO_UTIL.TO_WKTGEOMETRY(c.POLY) as POLY
        from CENTROID c
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
        from SHAPE c
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
    """,

    "query_containing_cms_polygon": """
        SELECT SDO_UTIL.TO_WKTGEOMETRY(poly) as CMS_POLY, cms as CMS
        FROM shape
        where cms = lable1
            and area > 0
            and LEVEL1 || COLOR1 || STYLE1 || WEIGHT1 = '41503'
            and DEL_USER is null
            and poly is not null
            AND SDO_RELATE(
                    poly, 
                    SDO_GEOMETRY('{TARGET_POLY}', {srid}), 
                    'mask=inside+touch+OVERLAPBDYINTERSECT+coveredby+CONTAINS'
                ) = 'TRUE'
    """,

    "query_overlapping_polygons_by_polygon": """
        SELECT 
            SDO_UTIL.TO_WKTGEOMETRY(poly) as OVERLAPPING_POLY,
            cms as CMS,
            LABLE1 as LABEL,
            to_char(LEVEL1) as LEVEL1,
            to_char(COLOR1) as COLOR1,
            to_char(STYLE1) as STYLE1,
            to_char(WEIGHT1) as WEIGHT1
        FROM shape
        where
            DEL_USER is null and DEL_DATE is null and
            LABLE1 like '%DD%' and -- exclude malformed labels
            VALIDATE1 = '1' and
            SDO_RELATE(
                poly, 
                SDO_GEOMETRY('{TARGET_POLY}', {srid}), 
                'mask=inside+touch+OVERLAPBDYINTERSECT+coveredby+CONTAINS'
            ) = 'TRUE'
            
        UNION ALL
        
        SELECT 
            SDO_UTIL.TO_WKTGEOMETRY(poly) as OVERLAPPING_POLY,
            cms as CMS,
            TXT_LABLE as LABEL,
            '' as LEVEL1,
            '' as COLOR1,
            '' as STYLE1,
            '' as WEIGHT1
        FROM centroid
        where
            DEL_USER is null and DEL_DATE is null and
            TXT_LABLE like '%DD%' and -- exclude malformed labels
            VALIDATE1 = '1' and
            SDO_RELATE(
                poly, 
                SDO_GEOMETRY('{TARGET_POLY}', {srid}), 
                'mask=inside+touch+OVERLAPBDYINTERSECT+coveredby+CONTAINS'
            ) = 'TRUE'
        
    """
}


def find_state_polygon(state_code: str) -> Parcel:
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


def find_cms_polygon(cms: str) -> Parcel:
    def run(db_result: DBResult):
        results = db_result.results
        wkt_str = None
        for result in results:
            wkt_str = str(result['CMS_POLY'])

        return wkt_str

    query = QUERIES['query_cms_polygon'].format(cms=cms)
    geometry_wkt = execute_query(query, run)

    return Parcel(polygon=geometry_wkt)


def find_polygon_wrapper_cms(polygon_wkt, srid) -> CmsUnit:
    def run(db_result: DBResult):
        results = db_result.results
        wkt_str = None
        cms = None
        for result in results:
            wkt_str = str(result['CMS_POLY'])
            cms = str(result['CMS'])

        return CmsUnit(polygon_wkt=wkt_str, cms=cms)

    query = QUERIES['query_containing_cms_polygon'].format(TARGET_POLY=polygon_wkt, srid=srid)
    cms_unit = execute_query(query, run)

    return cms_unit


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

    if shape_parcel.polygon:
        return shape_parcel
    elif centroid_parcel.polygon:
        return centroid_parcel


def find_parcel_info_by_centroid(centroid: Point_T) -> Parcel:
    parcel = find_polygon_by_centroid(centroid)
    deed = find_deed(parcel.deed)
    if not deed:
        deed = Deed()  # let's have an empty deed if there is none

    # : must be set in find_deed
    parcel.deed.address_text = deed.address_text
    parcel.deed.legal_area = deed.legal_area
    parcel.deed.partitioned = deed.partitioned
    parcel.deed.segment = deed.segment

    if deed.state and deed.state is not None:
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

    query_centroid_polygon_list = QUERIES['query_centroid_polygon_list_by_point'].format(
        x=centroid.x, y=centroid.y, srid=centroid.srid, distance=distance)

    query_shape_polygon_list = QUERIES['query_shape_polygon_list_by_point'].format(
        x=centroid.x, y=centroid.y, srid=centroid.srid, distance=distance)

    query_buffer = QUERIES['query_point_buffer'].format(
        x=centroid.x, y=centroid.y, srid=centroid.srid, distance=distance)

    centroid_polygon_list = execute_query(query_centroid_polygon_list, run_poly)
    shape_polygon_list = execute_query(query_shape_polygon_list, run_poly)
    buffer = execute_query(query_buffer, run_buffer)

    return centroid_polygon_list + shape_polygon_list, buffer


def find_overlapping_parcels_by_polygon(target_polygon_wkt: str, srid=UTM_ZONE_38_SRID) -> list[Parcel]:
    def run(db_result: DBResult):
        results = db_result.results

        parcel_list = []
        for result in results:
            geometry = wkt.loads(str(result['OVERLAPPING_POLY']))
            label = str(result['LABEL'])
            cms = str(result['CMS'])
            level1 = str(result['LEVEL1'])
            color1 = str(result['COLOR1'])
            style1 = str(result['STYLE1'])
            weight1 = str(result['WEIGHT1'])
            is_documented = False
            if label is not None and label.endswith("*"):
                is_documented = True
            layer_name = Layers.get_layer(level1, color1, style1, weight1)
            layer_id = f"{level1}_{color1}_{style1}_{weight1}"
            parcel = Parcel(polygon=geometry, cms=cms, layer_id=layer_id,
                            layer_name=layer_name, is_documented=is_documented)
            parcel_list.append(parcel)

        return parcel_list

    query = QUERIES['query_overlapping_polygons_by_polygon'].format(TARGET_POLY=target_polygon_wkt, srid=srid)
    parcels = execute_query(query, run)
    return parcels
