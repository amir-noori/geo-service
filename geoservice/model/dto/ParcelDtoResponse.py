from pydantic import ConfigDict
from pydantic.alias_generators import to_camel

from geoservice.common.constants import GLOBAL_SRID
from geoservice.gis.model.models import GeomType
from geoservice.model.dto.BaseDTO import BaseDTO, BaseResponse, partial_model


@partial_model
class ParcelGeomDTO(BaseDTO):
    geom: str
    type: str
    crs: str

    def __init__(self, geom: str = None, type: GeomType = GeomType.POLYGON, crs: str = GLOBAL_SRID) -> None:
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

    def __init__(self, body=None, header=None) -> None:
        super().__init__(header=header)
        self.body = body


@partial_model
class ParcelListDTO(BaseDTO):
    parcel_geom_list: list[ParcelGeomDTO]
    buffer_geom: ParcelGeomDTO

    def __init__(self, parcel_geom_list: list[ParcelGeomDTO] = [], buffer_geom: ParcelGeomDTO = None) -> None:
        super().__init__()
        self.parcel_geom_list = parcel_geom_list
        self.buffer_geom = buffer_geom


@partial_model
class ParcelListResponse(BaseResponse):
    body: ParcelListDTO

    def __init__(self, body: ParcelListDTO = None, header=None) -> None:
        super().__init__(header=header)
        self.body = body


@partial_model
class StatePolygonResponse(BaseResponse):
    body: ParcelGeomDTO

    def __init__(self, body: ParcelGeomDTO = None, header=None) -> None:
        super().__init__(header=header)
        self.body = body


### wrapper cms

@partial_model
class WrapperCmsResponseDTO(BaseDTO):
    cms: str
    cms_polygon_wkt: str

    def __init__(self, cms_polygon_wkt: str = None, cms: str = None) -> None:
        super().__init__()
        self.cms = cms
        self.cms_polygon_wkt = cms_polygon_wkt


@partial_model
class WrapperCmsResponse(BaseResponse):
    body: WrapperCmsResponseDTO

    def __init__(self, body: WrapperCmsResponseDTO = None, header=None) -> None:
        super().__init__(header=header)
        self.body = body


### overlapping parcels


@partial_model
class OverlappingResponseDTO(BaseDTO):

    polygon_wkt: str
    cms: str
    layer_id: str
    layer_name: str
    is_documented: bool

    def __init__(self, polygon_wkt: str = None, cms: str = None, layer_id: str = None, layer_name: str = None,
                 is_documented: bool = False) -> None:
        super().__init__()
        self.cms = cms
        self.polygon_wkt = polygon_wkt
        self.layer_id = layer_id
        self.layer_name = layer_name
        self.is_documented = is_documented


@partial_model
class OverlappingResponse(BaseResponse):
    body: list[OverlappingResponseDTO]

    def __init__(self, body: list[OverlappingResponseDTO] = None, header=None) -> None:
        super().__init__(header=header)
        self.body = body
