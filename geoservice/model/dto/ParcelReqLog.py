from geoservice.model.dto.BaseDTO import BaseDTO, RequestHeader, partial_model
from geoservice.model.dto.BaseDTO import BaseResponse
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from geoservice.exception.service_exception import ValidationException
from geoservice.exception.common import ErrorCodes
from pydantic import BaseModel, field_validator
from typing import Optional, Any
from datetime import datetime


class ParcelRequestDetail(BaseModel):

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    national_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None


class ParcelReqLogRequest(BaseModel):

    header: RequestHeader
    body: ParcelRequestDetail

    def get_service_key(self):
        return None

    @field_validator('body')
    @classmethod
    def validate_header_params(cls, pracel_request_detail: Any):

        if not pracel_request_detail.first_name \
                and not pracel_request_detail.last_name \
                and not pracel_request_detail.national_id:
            raise ValidationException(
                ErrorCodes.VALIDATION_EMPTY_REQUEST_FIELDS)

        return pracel_request_detail


@partial_model
class ParcelReqLog(BaseDTO):

    national_id: str
    first_name: str
    last_name: str
    request_time: str
    search_point: str  # in wkt format

    def __init__(self, national_id: str = None, first_name: str = None, request_time: str = None,
                 last_name: str = None, search_point: str = None) -> None:
        super().__init__()

        self.national_id = national_id
        self.first_name = first_name
        self.last_name = last_name
        self.request_time = request_time
        self.search_point = search_point


@partial_model
class ParcelReqLogs(BaseDTO):

    request_list: list[ParcelReqLog]

    def __init__(self, request_list: list[ParcelReqLog] = []) -> None:
        super().__init__()

        self.request_list = request_list


@partial_model
class ParcelReqLogResponse(BaseResponse):

    body: ParcelReqLogs

    def __init__(self, body=None, header=None) -> None:
        super().__init__(header=header)
        self.body = body
