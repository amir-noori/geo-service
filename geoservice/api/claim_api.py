from fastapi import APIRouter, Request, Depends

from geoservice.api.common import handle_response
from geoservice.api.route import route
from geoservice.dispatcher.dispatcher import dispatch
from geoservice.model.dto.claim.ClaimDtoReq import ClaimRequestDTO, ClaimRequest, ClaimParcelQueryRequest, \
    ClaimParcelQueryRequestDTO
from geoservice.model.dto.claim.ClaimDtoResponse import ClaimResponse, ClaimParcelQueryResponse, \
    ClaimParcelQueryResponseDTO
from geoservice.model.entity.Claim import Claim
from geoservice.service.claim_service import create_new_claim_request, query_claim_parcel
from log.logger import logger

router = APIRouter()
log = logger()


@route(router=router, method="post", path="/claim_parcel", response_model=ClaimResponse)
# @dispatch(dispatch_event=None)
async def claim_parcel_api(request: Request, parcel_request: ClaimRequest = Depends()):
    body: ClaimRequestDTO = parcel_request.body
    create_new_claim_request(body)
    return handle_response(request, ClaimResponse())


@route(router=router, method="post", path="/claim_parcel_query", response_model=ClaimParcelQueryResponse)
# @dispatch(dispatch_event=None)
async def claim_parcel_query_api(request: Request, claim_query_request: ClaimParcelQueryRequest = Depends()):
    body: ClaimParcelQueryRequestDTO = claim_query_request.body
    claim: Claim = query_claim_parcel(body)
    query_response_dto = ClaimParcelQueryResponseDTO(claim_trace_id=claim.claim_trace_id,
                                                     polygon=claim.claimed_polygon)
    response = ClaimParcelQueryResponse(body=query_response_dto)
    return handle_response(request, response)
