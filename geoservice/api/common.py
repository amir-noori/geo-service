import os

import requests
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from geoservice.common.states import state_to_db_mapping
from geoservice.exception.common import ErrorCodes
from geoservice.exception.service_exception import ValidationException
from geoservice.model.dto.BaseDTO import Header, BaseResponse
from geoservice.model.dto.BaseDTO import RequestHeader
from i18n.locale import get_locale
from log.logger import logger

log = logger()


class ResponseCode:

    def __init__(self, code, message_key) -> None:
        self.code = code
        self.message_key = message_key


class ResponseCodes:
    SUCCESS = ResponseCode(200, "SUCCESS")


def handle_response(request: Request, response: BaseResponse, exclude_unset=True, exclude_none=True):
    lang = request.scope["lang"]
    response_message = get_locale(ResponseCodes.SUCCESS.message_key, lang)

    header = Header(
        result_code=ResponseCodes.SUCCESS.code,
        result_message=response_message
    )

    response.header = header
    content = jsonable_encoder(
        response, exclude_unset=exclude_unset, exclude_none=exclude_none)

    return JSONResponse(content=content)


def find_state_for_dispatch_by_header(event):
    log.debug(f"event data for dispatch {event['data']}")
    state_code = None

    if event["data"]:
        for k, v in event["data"].items():
            if isinstance(v, BaseModel):
                header: RequestHeader = v.header
                try:
                    if header.params and header.params["stateCode"]:
                        state_code = header.params["stateCode"]
                except KeyError as e:
                    log.error(f"cannot find state code based on header: {e}")

    if not state_code:
        raise ValidationException(
            ErrorCodes.VALIDATION_NO_STATE_CODE_IN_HEADER)

    return state_code


