
from geoservice.api.common import handle_response
from fastapi import APIRouter, Request
from geoservice.common.units import units
from geoservice.model.dto.UnitDTO import *


router = APIRouter()


@router.get("/find_unit_by_cmd", response_model=UnitResponse)
def find_unit_by_cmd_api(request: Request, cms: str):

    unit_dto = UnitDTO()
    for unit_cms, unit_info in units.items():
        if cms == unit_cms:
            unit_dto.cms = cms
            unit_dto.unit_id = unit_info["unitId"]
            unit_dto.unit_name = unit_info["unitName"]

    response = UnitResponse(body=unit_dto)
    return handle_response(response)

