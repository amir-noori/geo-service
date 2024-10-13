
from shapely import wkt

from data.db_helper import execute_query
from data.DBResult import DBResult
from common.constants import *
from gis.model.models import Point_T
from model.entity.Parcel import *
from service.util import process_label
from service.deed_service import find_deed

from exception.common import ErrorCodes
from exception.service_exception import ServiceException

QUERIES = {
    "query_centroid_by_point": """
        SELECT SDO_UTIL.TO_WKTGEOMETRY(c.POLY) as POLY, TXT_LABLE as LABEL, SDO_GEOM.SDO_AREA(c.POLY) as AREA
        FROM gis.CENTROID c
        WHERE 
        DEL_USER is null and DEL_DATE is null and
        TXT_LABLE like '%*' and
        SDO_CONTAINS(c.POLY,
                sdo_geometry('POINT ({y} {x})', {srid})
        ) = 'TRUE'
    """,

    "query_shape_by_point": """
        SELECT SDO_UTIL.TO_WKTGEOMETRY(s.POLY) as POLY, LABLE1 as LABEL , SDO_GEOM.SDO_AREA(s.POLY) as AREA
        FROM gis.SHAPE s
        WHERE 
            DEL_USER is null and DEL_DATE is null and
            LABLE1 like '%*' and
            SDO_CONTAINS(s.POLY,
                    sdo_geometry('POINT ({x} {y})', {srid})
            ) = 'TRUE'
    """
}


def find_polygon_by_centroid(centroid: Point_T) -> Parcel:

    def run(db_result: DBResult):
        row_count = db_result.row_count
        results = db_result.results
        if row_count > 1:
            raise ServiceException(ErrorCodes.MULTIPLE_PARCEL_FOUND)

        geometry_wkt = None
        deed = None
        cms = None
        area_wkt = None
        for result in results:
            geometry_wkt = wkt.loads(str(result['POLY']))
            area_wkt=str(result['AREA'])
            label = str(result['LABEL'])
            deed = process_label(label)
            cms = deed.cms

        return Parcel(polygon=geometry_wkt, deed=deed, cms=cms, area=area_wkt)

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

    # TODO: must be set in find_deed
    parcel.deed.address_text = deed.address_text
    parcel.deed.legal_area = deed.legal_area
    parcel.deed.partitioned = deed.partitioned
    parcel.deed.segment = deed.segment
    parcel.deed.state = deed.state

    return parcel
