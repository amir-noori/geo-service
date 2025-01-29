from fastapi import APIRouter, Request, Depends

from geoservice.api.common import find_state_for_dispatch_by_header
from geoservice.api.common import handle_response
from geoservice.api.route import route
from geoservice.dispatcher.dispatcher import dispatch
from geoservice.event.Event import Event
from geoservice.model.dto.ParcelReqLog import *
from geoservice.service.parcel_request_log_service import find_parcel_req_log_list
from log.logger import logger

router = APIRouter()
log = logger()


@route(router=router, method="post", path="/find_parcel_request", response_model=ParcelReqLogResponse)
@dispatch(dispatch_event=Event(find_state_for_dispatch_by_header))
def find_parcel_info_by_centroid_api_post(request: Request,
                                          parcel_req_log_request: ParcelReqLogRequest = Depends()):
    body: ParcelRequestDetail = parcel_req_log_request.body

    # TODO: support jalali date
    parcel_request_log_list = find_parcel_req_log_list(body)

    parcel_req_log_list: list[ParcelReqLog] = []
    for parcel_request_log in parcel_request_log_list:
        parcel_req_log = ParcelReqLog(
            first_name=parcel_request_log.first_name,
            last_name=parcel_request_log.last_name,
            national_id=parcel_request_log.national_id,
            request_time=parcel_request_log.request_time,
            search_point=parcel_request_log.search_point.wkt
        )

        parcel_req_log_list.append(parcel_req_log)

    parcel_req_logs = ParcelReqLogs(request_list=parcel_req_log_list)

    response = ParcelReqLogResponse(body=parcel_req_logs)
    return handle_response(request, response)
