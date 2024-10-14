from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from common.localization import Localization
from model.dto.BaseDTO import Header, BaseResponse


class ResponseCode:

    def __init__(self, code, message_key) -> None:
        self.code = code
        self.message_key = message_key


class ResponseCodes:

    SUCCESS = ResponseCode(0, Localization().translate("result_code_0"))


def handle_response(response, exclude_unset=True, exclude_none=True):
    header = Header(
        result_code=ResponseCodes.SUCCESS.code,
        result_message=ResponseCodes.SUCCESS.message_key
    )
    #response.Header = header
    BaseResponse.header = header
    content = jsonable_encoder(
        response, exclude_unset=exclude_unset, exclude_none=exclude_none)
    return JSONResponse(content=content)
