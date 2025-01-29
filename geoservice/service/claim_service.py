import json
from datetime import datetime

from shapely.geometry import shape

from geoservice.data.DBResult import DBResult
from geoservice.data.db_helper import execute_insert, execute_query
from geoservice.exception.common import ErrorCodes
from geoservice.exception.service_exception import ServiceException
from geoservice.model.dto.claim.ClaimDtoReq import ClaimRequestDTO, ClaimParcelQueryRequestDTO
from geoservice.model.entity.Claim import Claim
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
    content_type = claim_request.claimed_content_type.upper()
    content = claim_request.claimed_content

    params = [claim_request.claim_trace_id, datetime.now(), content_type, content]

    polygon = ""

    if content_type == "GEOJSON":
        geo_json = json.loads(content)
        features = geo_json["features"]
        if len(features) < 1:
            raise ServiceException(ErrorCodes.NO_FEATURE_FOUND)
        if len(features) > 1:
            raise ServiceException(ErrorCodes.MULTIPLE_FEATURE_FOUND)

        feature = features[0]
        try:
            geometry_str = feature["geometry"]
            geometry = shape(geometry_str)
            polygon = geometry.wkt
            # TODO: check geometry type is polygon
        except KeyError:
            raise ServiceException(ErrorCodes.NO_GEOMETRY_FOUND)

    if content_type == "SHP":
        # TODO
        pass
    if content_type == "KML":
        # TODO
        pass

    insert_claim_sql = QUERIES['insert_claim'].format(
        polygon=polygon
    )

    execute_insert(insert_claim_sql, params)
