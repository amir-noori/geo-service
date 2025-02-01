import base64
import json
from datetime import datetime

from shapely.geometry import shape

from common.str_util import base64ToString
from geoservice.data.DBResult import DBResult
from geoservice.data.db_helper import execute_insert, execute_query
from geoservice.exception.common import ErrorCodes
from geoservice.exception.service_exception import ServiceException
from geoservice.model.dto.claim.ClaimDtoReq import ClaimRequestDTO, ClaimParcelQueryRequestDTO
from geoservice.model.entity.Claim import Claim
from geoservice.util.gis_util import is_polygon, load_shp_data, load_kml_data
from log.logger import logger

log = logger()

QUERIES = {
    "insert_claim": """
        insert into TBL_LAND_CLAIM
        (ID, claim_trace_id, request_timestamp, claimed_file_content_type, claimed_file_content, claimed_polygon)
        values (TBL_LAND_CLAIM_SEQ.NEXTVAL, 
            :CLAIM_TRACE_ID, 
            :REQUEST_TIMESTAMP, 
            :CLAIMED_FILE_CONTENT_TYPE,
            :CLAIMED_POLYGON, 
            SDO_UTIL.FROM_WKTGEOMETRY('{polygon}'))
    """,

    "query_claim_by_trace_id": """
        select 
            CLAIM_TRACE_ID, REQUEST_TIMESTAMP, SDO_UTIL.TO_WKTGEOMETRY(CLAIMED_POLYGON) as CLAIMED_POLYGON
        from
            TBL_LAND_CLAIM
        where 
            claim_trace_id = {claim_trace_id}
    """

}


def query_claim_parcel(claim_query_request: ClaimParcelQueryRequestDTO) -> Claim:
    def run(db_result: DBResult):
        results = db_result.results

        for result in results:
            trace_id = str(result['CLAIM_TRACE_ID'])
            polygon_wkt = str(result['CLAIMED_POLYGON'])
            request_timestamp = str(result['REQUEST_TIMESTAMP'])

            return Claim(claim_trace_id=trace_id, claimed_polygon=polygon_wkt,
                         request_timestamp=request_timestamp)

        return None

    claim_trace_id = claim_query_request.claim_trace_id
    query_claim = QUERIES['query_claim_by_trace_id'].format(
        claim_trace_id=claim_trace_id
    )

    return execute_query(query_claim, run)


def create_new_claim_request(claim_request: ClaimRequestDTO):
    def check_len(obj):
        if len(obj) < 1:
            raise ServiceException(ErrorCodes.NO_FEATURE_FOUND)
        if len(obj) > 1:
            raise ServiceException(ErrorCodes.MULTIPLE_FEATURE_FOUND)

    content_type = claim_request.claimed_content_type.upper()
    content = None
    polygon = ""
    geometry = None

    if content_type == "GEOJSON":
        content = base64ToString(claim_request.claimed_content)
        geo_json = json.loads(content)
        features = geo_json["features"]
        check_len(features)

        feature = features[0]
        try:
            geometry_str = feature["geometry"]
            geometry = shape(geometry_str)
            polygon = geometry.wkt
        except KeyError:
            raise ServiceException(ErrorCodes.NO_GEOMETRY_FOUND)

    elif content_type == "SHP":
        content = base64.b64decode(claim_request.claimed_content)
        data_map = load_shp_data(content)
        check_len(data_map)
        data_tuple = data_map[0]
        geometry = data_tuple[0]
        polygon = geometry.wkt

    elif content_type == "KML":
        content = base64ToString(claim_request.claimed_content)
        geometries = load_kml_data(content)
        check_len(geometries)
        geometry = shape(geometries[0])
        polygon = geometry.wkt

    if geometry:
        if not is_polygon(geometry):
            raise ServiceException(ErrorCodes.INVALID_POLYGON_FOUND)
    else:
        raise ServiceException(ErrorCodes.NO_GEOMETRY_FOUND)

    params = [claim_request.claim_trace_id, datetime.now(), content_type, content]
    insert_claim_sql = QUERIES['insert_claim'].format(
        polygon=polygon
    )

    execute_insert(insert_claim_sql, params)
