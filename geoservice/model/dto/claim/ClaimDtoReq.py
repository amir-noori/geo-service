from typing import Any

from pydantic import BaseModel, field_validator

from geoservice.exception.common import ErrorCodes
from geoservice.exception.service_exception import ValidationException
from geoservice.model.dto.BaseDTO import BaseDTO, RequestHeader, partial_model


@partial_model
class ClaimRequestDTO(BaseDTO):
    claim_trace_id: str
    claimed_content_type: str
    claimed_content: str

    def __init__(self, claim_trace_id: str = None, claimed_content_type: str = None,
                 claimed_content: str = None) -> None:
        super().__init__()
        self.claim_trace_id = claim_trace_id
        self.claimed_content_type = claimed_content_type
        self.claimed_content = claimed_content

    def get_service_key(self):
        return f"{self.claim_trace_id}"


class ClaimRequest(BaseModel):
    body: ClaimRequestDTO
    header: RequestHeader

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

        return b


@partial_model
class ClaimParcelQueryRequestDTO(BaseDTO):
    claim_trace_id: str

    def __init__(self, claim_trace_id: str = None) -> None:
        super().__init__()
        self.claim_trace_id = claim_trace_id

    def get_service_key(self):
        return f"{self.claim_trace_id}"


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
