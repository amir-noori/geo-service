from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import Request
from geoservice.model.dto.BaseDTO import Header, BaseResponse
from i18n.locale import get_locale

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
