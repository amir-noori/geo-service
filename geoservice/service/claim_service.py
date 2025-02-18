from datetime import datetime

from geoservice.data.DBResult import DBResult
from geoservice.data.db_helper import execute_insert, execute_query
from geoservice.exception.common import ErrorCodes
from geoservice.exception.service_exception import ServiceException
from geoservice.model.dto.claim.ClaimDtoReq import ClaimParcelQueryRequestDTO
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
    """,

    "query_claim_count_by_trace_id": """
        select 
            count(*) as CLAIM_COUNT
        from
            TBL_LAND_CLAIM
        where 
            claim_trace_id = '{claim_trace_id}'
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

    claim = execute_query(query_claim, run)
    if not claim:
        raise ServiceException(ErrorCodes.NO_CLAIM_FOUND)
    else:
        return claim


def query_claim_parcel_count(claim_trace_id: str) -> int:
    def run(db_result: DBResult):
        results = db_result.results

        for result in results:
            count = str(result['CLAIM_COUNT'])
            return int(count)

        return None

    query_claim = QUERIES['query_claim_count_by_trace_id'].format(
        claim_trace_id=claim_trace_id
    )

    return execute_query(query_claim, run)


def create_new_claim_request(content, content_type, polygon, claim_trace_id):
    params = [claim_trace_id, datetime.now(), content_type, content]
    insert_claim_sql = QUERIES['insert_claim'].format(
        polygon=polygon
    )

    claim_count = query_claim_parcel_count(claim_trace_id)

    if claim_count > 0:
        raise ServiceException(ErrorCodes.VALIDATION_CLAIM_TRACE_ID_EXISTS)

    execute_insert(insert_claim_sql, params)
