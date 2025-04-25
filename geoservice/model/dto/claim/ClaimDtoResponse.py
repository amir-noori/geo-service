from geoservice.model.dto.BaseDTO import BaseDTO, BaseResponse, partial_model
from geoservice.model.dto.ParcelDtoResponse import OverlappingResponseDTO
from geoservice.model.dto.common import PointDTO
from geoservice.model.dto.PersonDTO import PersonDTO


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
    status: int # 1: OK, -1: Failed
    neighborhood_point: PointDTO
    surveyor: PersonDTO
    claimant: PersonDTO
    parcel: str # geojson

    def __init__(self, request_id: str) -> None:
        super().__init__()
        self.request_id = request_id


@partial_model
class ClaimParcelSurveyQueryResponse(BaseResponse):
    body: ClaimParcelSurveyQueryResponseDTO

    def __init__(self, body: ClaimParcelSurveyQueryResponseDTO = None, header=None) -> None:
        super().__init__(header=header)
        self.body = body