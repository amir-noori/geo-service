from geoservice.model.dto.BaseDTO import BaseDTO, BaseResponse, partial_model
from geoservice.model.dto.ParcelDtoResponse import OverlappingResponseDTO


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
