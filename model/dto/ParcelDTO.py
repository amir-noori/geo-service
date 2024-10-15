from .BaseDTO import BaseDTO, BaseResponse, partial_model
from gis.model.models import GeomType
from common.constants import GLOBAL_SRID


@partial_model
class ParcelGeomDTO(BaseDTO):
    geom: str
    type: str
    crs: str

    def __init__(self, geom: str=None, type: GeomType=GeomType.POLYGON, crs: str=GLOBAL_SRID) -> None:
        super().__init__()
        self.geom = geom
        self.type = type
        self.crs = crs


@partial_model
class ParcelMetadataDTO(BaseDTO):

    state: str
    state_code: str
    cms: str
    section: str
    district: str
    main_plate_number: str
    subsidiary_plate_number: str
    partitioned: str
    segment: str
    area: str

    def __init__(self, state=None, state_code=None, cms=None, section=None,
                 district=None, main_plate_number=None, subsidiary_plate_number=None,
                 partitioned=None, segment=None, area=None) -> None:
        super().__init__()

        self.state = state
        self.state_code = state_code
        self.cms = cms
        self.section = section
        self.district = district
        self.main_plate_number = main_plate_number
        self.subsidiary_plate_number = subsidiary_plate_number
        self.segment = segment
        self.area = area
        self.partitioned = partitioned


@partial_model
class ParcelGroundDTO(BaseDTO):

    parcel_geom: ParcelGeomDTO
    metadata: ParcelMetadataDTO

    def __init__(self, parcel_geom: ParcelGeomDTO, metadata: ParcelMetadataDTO) -> None:
        super().__init__()
        self.parcel_geom = parcel_geom
        self.metadata = metadata


@partial_model
class ParcelInfoDTO(BaseDTO):

    common_metadata: ParcelMetadataDTO
    ground: ParcelGroundDTO
    apartments: list[ParcelMetadataDTO]

    def __init__(self, common_metadata: ParcelMetadataDTO, ground: ParcelGroundDTO,
                 apartments) -> None:
        super().__init__()

        self.common_metadata = common_metadata
        self.ground = ground
        self.apartments = apartments


@partial_model
class ParcelInfoResponse(BaseResponse):
    
    body: ParcelInfoDTO

    def __init__(self, body=None) -> None:
        super().__init__()
        self.body = body