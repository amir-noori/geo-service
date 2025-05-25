from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict
from pydantic import field_validator
from pydantic.alias_generators import to_camel

from geoservice.common.states import states
from geoservice.exception.common import ErrorCodes
from geoservice.exception.service_exception import ValidationException
from geoservice.model.dto.BaseDTO import RequestHeader, partial_model
from geoservice.model.dto.PersonDTO import PersonDTO
from geoservice.model.dto.common import PointDTO


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


@partial_model
class RegisterNewClaimRequestDTO(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True
    )

    request_id: str
    cms: str
    surveyor: PersonDTO
    claimant: PersonDTO
    neighborhood_point: PointDTO
    postal_code: str
    area: float


class RegisterNewClaimRequest(BaseModel):
    body: RegisterNewClaimRequestDTO
    header: RequestHeader

    @field_validator('body')
    @classmethod
    def validate_body(cls, b: Any):
        if not b.request_id:
            raise ValidationException(ErrorCodes.VALIDATION_EMPTY_REQUEST_FIELDS,
                                      error_message="request_id is required!")

        if not b.claimant:
            raise ValidationException(ErrorCodes.VALIDATION_EMPTY_REQUEST_FIELDS,
                                      error_message="claimant is required!")

        else:
            if not b.claimant.first_name or not b.claimant.last_name or not b.claimant.national_id \
                    or not b.claimant.mobile_number:
                raise ValidationException(ErrorCodes.VALIDATION_EMPTY_REQUEST_FIELDS,
                                          error_message="claimant fields is required (first_name, last_name, national_id, mobile_number)!")

        return b

    def get_service_key(self):
        if self.body:
            return self.body.request_id
        else:
            return None


@partial_model
class SurveyParcelEdgeMetadataDTO(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True
    )

    lineIndex: int
    length: float
    orientation: int
    boundary: str
    is_adjacent_to_plate_number: bool
    is_adjacent_to_passage: bool
    passage_name: str
    passage_width: float
    starting_point: PointDTO
    ending_point: PointDTO


@partial_model
class SurveyParcelAttachmentPropertiesDTO(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True
    )

    attachmentCode: str
    title: str
    area: float
    description: str


@partial_model
class ParcelMetadataDTO(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True
    )

    beneficiary_rights: str
    accommodation_rights: str
    is_apartment: bool
    floor_number: float
    unit_number: float
    orientation: int


@partial_model
class SurveyParcelMetadataDTO(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True
    )

    metadata: ParcelMetadataDTO
    edge_metadata: List[SurveyParcelEdgeMetadataDTO]
    attachment_properties: List[SurveyParcelAttachmentPropertiesDTO]


@partial_model
class RegisterNewClaimCallbackRequestDTO(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True
    )

    request_id: str
    claim_tracing_id: str
    status: int
    cms: str
    area: float
    county: str
    state_code: str
    main_plate_number: str
    subsidiary_plate_number: str
    section: str
    district: str
    survey_parcel: str
    survey_parcel_metadata: SurveyParcelMetadataDTO
    survey_apartment_parcel: str
    survey_apartment_parcel_metadata: SurveyParcelMetadataDTO


class RegisterNewClaimCallbackRequest(BaseModel):
    body: RegisterNewClaimCallbackRequestDTO
    header: RequestHeader

    @field_validator('body')
    @classmethod
    def validate_body(cls, b: Any):
        return b

    def get_service_key(self):
        if self.body:
            if self.body.claim_tracing_id:
                return f"traceId:{self.body.claim_tracing_id}"
            else:
                return f"reqId:{self.body.request_id}"
        else:
            return None


class ClaimParcelSurveyQueryRequestDTO(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True
    )

    request_id: Optional[str] = None
    claim_tracing_id: Optional[str] = None


class ClaimParcelSurveyQueryRequest(BaseModel):
    body: ClaimParcelSurveyQueryRequestDTO
    header: RequestHeader

    @field_validator('body')
    @classmethod
    def validate_body(cls, b: Any):
        if not b.request_id and not b.claim_tracing_id:
            raise ValidationException(ErrorCodes.VALIDATION_EMPTY_REQUEST_FIELDS,
                                      error_message="request_id or claim_tracing_id is required!")
        return b

    def get_service_key(self):
        if self.body:
            if self.body.claim_tracing_id:
                return f"traceId:{self.body.claim_tracing_id}"
            else:
                return f"reqId:{self.body.request_id}"
        else:
            return None
