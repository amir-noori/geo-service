
from geoservice.model.entity.ParcelRequestLog import *
from geoservice.data.db_helper import execute_insert, execute_query
from geoservice.data.DBResult import DBResult
from geoservice.gis.model.models import Point_T
from geoservice.model.dto.ParcelReqLog import ParcelRequestDetail
from log.logger import logger
import json


log = logger()

QUERIES = {
    "insert_db_parcel_req_log": """
        insert into GIS.TBL_PARCEL_REQ_LOG
        (NATIONAL_ID, FIRST_NAME, LAST_NAME, REQUEST_TIMESTAMP, search_point, PARAMS)
        values (:NATIONAL_ID, :FIRST_NAME, :LAST_NAME, :REQUEST_TIMESTAMP, 
            SDO_UTIL.FROM_WKTGEOMETRY('POINT ({x} {y})'), :PARAMS)
    """,
    
    "query_parcel_req_log": """
        select 
            SDO_UTIL.TO_WKTGEOMETRY(SEARCH_POINT) as SEARCH_POINT,
            NATIONAL_ID,
            FIRST_NAME,
            LAST_NAME,
            REQUEST_TIMESTAMP
        from gis.TBL_PARCEL_REQ_LOG
        where 
            1 = 1
    """
}


def save_parcel_req_log(parcel_req_log: ParcelRequestLog) -> None:

    log_params = parcel_req_log.params
    if parcel_req_log.params and type(parcel_req_log.params) == dict:
        log_params = json.dumps(parcel_req_log.params)


    params = [parcel_req_log.national_id, parcel_req_log.first_name,
              parcel_req_log.last_name, parcel_req_log.request_time,
              str(log_params)]

    query = QUERIES['insert_db_parcel_req_log'].format(
        x=parcel_req_log.search_point.x,
        y=parcel_req_log.search_point.y
    )
    
    execute_insert(query, params)


def find_parcel_req_log_list(parcel_request_detail: ParcelRequestDetail) -> list[ParcelRequestLog]:

    def run(db_result: DBResult):
        results = db_result.results

        parcel_request_log_list: list[ParcelRequestLog] = []
        for result in results:
            search_point_wkt = str(result['SEARCH_POINT'])
            national_id = str(result['NATIONAL_ID'])
            first_name = str(result['FIRST_NAME'])
            last_name = str(result['LAST_NAME'])
            request_timestamp = str(result['REQUEST_TIMESTAMP'])
            parcel_request_log = ParcelRequestLog(
                first_name=first_name,
                last_name=last_name,
                national_id=national_id,
                request_time=request_timestamp,
                search_point=Point_T(x=None, y=None, wkt=search_point_wkt)
            )
            parcel_request_log_list.append(parcel_request_log)

        return parcel_request_log_list

    query_parcel_req_log = QUERIES['query_parcel_req_log']

    if parcel_request_detail.first_name:
        query_parcel_req_log = query_parcel_req_log + \
            f" and first_name like '%{parcel_request_detail.first_name}%' "
            
    if parcel_request_detail.last_name:
        query_parcel_req_log = query_parcel_req_log + \
            f" and last_name like '%{parcel_request_detail.last_name}%' "
            
    if parcel_request_detail.national_id:
        query_parcel_req_log = query_parcel_req_log + \
            f" and national_id = '{parcel_request_detail.national_id}' "
                        
    if parcel_request_detail.from_date:
        query_parcel_req_log = query_parcel_req_log + \
            f" and REQUEST_TIMESTAMP >= TO_DATE('{parcel_request_detail.from_date.strftime("%Y-%m-%d")}', 'YYYY-MM-DD') "          

    if parcel_request_detail.to_date:
        query_parcel_req_log = query_parcel_req_log + \
            f" and REQUEST_TIMESTAMP <= TO_DATE('{parcel_request_detail.to_date.strftime("%Y-%m-%d")}', 'YYYY-MM-DD') "          


    parcel_request_log_list = execute_query(query_parcel_req_log, run)
    return parcel_request_log_list
