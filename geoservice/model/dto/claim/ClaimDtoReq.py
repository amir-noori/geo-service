from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic import field_validator
from pydantic.alias_generators import to_camel

from geoservice.common.states import states
from geoservice.exception.common import ErrorCodes
from geoservice.exception.service_exception import ValidationException
from geoservice.model.dto.BaseDTO import RequestHeader


class ClaimRequestDTO(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True
    )

    claim_trace_id: str
    claimed_content_type: str
    claimed_content: str
    state_code: str
    srid: str


class ClaimRequest(BaseModel):
    body: ClaimRequestDTO
    header: RequestHeader

    def get_service_key(self):
        if self.body:
            return f"{self.body.claim_trace_id}"
        else:
            return None

    @field_validator('body')
    @classmethod
    def validate_body(cls, b: Any):
        if not b.claim_trace_id:
            raise ValidationException(ErrorCodes.VALIDATION_EMPTY_REQUEST_FIELDS,
                                      error_message="claim_trace_id is required!")

        if not b.claimed_content_type:
            raise ValidationException(ErrorCodes.VALIDATION_EMPTY_REQUEST_FIELDS,
                                      error_message="claimed_content_type is required!")

        if not b.claimed_content:
            raise ValidationException(ErrorCodes.VALIDATION_EMPTY_REQUEST_FIELDS,
                                      error_message="claimed_content is required!")

        if b.claimed_content_type.upper() not in ("KML", "GEOJSON", "SHP"):
            raise ValidationException(ErrorCodes.VALIDATION_EMPTY_REQUEST_FIELDS,
                                      error_message="no a valid claimed_content_type!")

        if b.state_code.upper() not in states:
            raise ValidationException(ErrorCodes.VALIDATION_INVALID_REQUEST_FIELDS,
                                      error_message="no a valid state code!")

        return b


class ClaimParcelQueryRequestDTO(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True
    )

    claim_trace_id: str


class ClaimParcelQueryRequest(BaseModel):
    body: ClaimParcelQueryRequestDTO
    header: RequestHeader

    @field_validator('body')
    @classmethod
    def validate_body(cls, b: Any):
        if not b.claim_trace_id:
            raise ValidationException(ErrorCodes.VALIDATION_EMPTY_REQUEST_FIELDS,
                                      error_message="claim_trace_id is required!")

        return b

    def get_service_key(self):
        if self.body:
            return self.body.claim_trace_id
        else:
            return None
