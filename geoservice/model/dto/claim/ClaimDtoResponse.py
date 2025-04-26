from typing import Any

from geoservice.model.dto.BaseDTO import BaseDTO, BaseResponse, partial_model
from geoservice.model.dto.ParcelDtoResponse import OverlappingResponseDTO
from geoservice.model.dto.PersonDTO import PersonDTO
from geoservice.model.dto.common import PointDTO


@partial_model
class ClaimResponseDTO(BaseDTO):
    overlapping_parcels: list[OverlappingResponseDTO]

    def __init__(self, overlapping_parcels: list[OverlappingResponseDTO]) -> None:
        super().__init__()
        self.overlapping_parcels = overlapping_parcels


@partial_model
class ClaimResponse(BaseResponse):
    body: ClaimResponseDTO

    def __init__(self, body: ClaimResponseDTO = None, header=None) -> None:
        super().__init__(header=header)
        self.body = body


@partial_model
class ClaimParcelQueryResponseDTO(BaseDTO):
    claim_trace_id: str
    polygon: str

    def __init__(self, claim_trace_id, polygon) -> None:
        super().__init__()
        self.claim_trace_id = claim_trace_id
        self.polygon = polygon


@partial_model
class ClaimParcelQueryResponse(BaseResponse):
    body: ClaimParcelQueryResponseDTO

    def __init__(self, body: ClaimParcelQueryResponseDTO = None, header=None) -> None:
        super().__init__(header=header)
        self.body = body


@partial_model
class RegisterNewClaimResponseDTO(BaseDTO):
    request_id: str

    def __init__(self, request_id: str) -> None:
        super().__init__()
        self.request_id = request_id


@partial_model
class RegisterNewClaimResponse(BaseResponse):
    body: RegisterNewClaimResponseDTO

    def __init__(self, body: RegisterNewClaimResponseDTO = None, header=None) -> None:
        super().__init__(header=header)
        self.body = body


@partial_model
class RegisterNewClaimCallbackResponseDTO(BaseDTO):
    request_id: str

    def __init__(self, request_id: str) -> None:
        super().__init__()
        self.request_id = request_id


@partial_model
class RegisterNewClaimCallbackResponse(BaseResponse):
    body: RegisterNewClaimCallbackResponseDTO

    def __init__(self, body: RegisterNewClaimCallbackResponseDTO = None, header=None) -> None:
        super().__init__(header=header)
        self.body = body


@partial_model
class ClaimParcelSurveyQueryResponseDTO(BaseDTO):
    request_id: str
    claim_tracing_id: str
    cms: str
    area: float
    state_code: str
    county: str
    main_plate_number: str
    subsidiary_plate_number: str
    section: str
    district: str
    status: int  # 1: OK, -1: Failed
    neighborhood_point: PointDTO
    surveyor: PersonDTO
    claimant: PersonDTO
    parcel: Any  # geojson

    def __init__(self, request_id: str = None, claim_tracing_id: str = None, cms: str = None,
                 area: float = 0.0, state_code: str = None, county: str = None, main_plate_number: str = None,
                 subsidiary_plate_number: str = None, section: str = None, district: str = None,
                 status: int = None, neighborhood_point: PointDTO = None, surveyor: PersonDTO = None,
                 claimant: PersonDTO = None, parcel: Any = None) -> None:
        super().__init__()
        self.request_id = request_id
        self.claim_tracing_id = claim_tracing_id
        self.cms = cms
        self.area = area
        self.state_code = state_code
        self.county = county
        self.main_plate_number = main_plate_number
        self.subsidiary_plate_number = subsidiary_plate_number
        self.section = section
        self.district = district
        self.status = status
        self.neighborhood_point = neighborhood_point
        self.surveyor = surveyor
        self.claimant = claimant
        self.parcel = parcel


@partial_model
class ClaimParcelSurveyQueryResponse(BaseResponse):
    body: ClaimParcelSurveyQueryResponseDTO

    def __init__(self, body: ClaimParcelSurveyQueryResponseDTO = None, header=None) -> None:
        super().__init__(header=header)
        self.body = body
