from typing import List

from geoservice.model.entity.common import BaseEntity


class Claim(BaseEntity):
    claim_trace_id: str
    claimed_content_type: str
    claimed_content: str
    claimed_polygon: str
    request_timestamp: str

    def __init__(self, claim_trace_id: str = None, claimed_content_type: str = None,
                 claimed_content: str = None, claimed_polygon: str = None, request_timestamp: str = None) -> None:
        super().__init__()
        self.claim_trace_id = claim_trace_id
        self.claimed_content_type = claimed_content_type
        self.claimed_content = claimed_content
        self.claimed_polygon = claimed_polygon
        self.request_timestamp = request_timestamp


class ClaimParcelAttachment(BaseEntity):
    """
        entry for each attachment piece (@finglish: monzam) for a claim parcel
    """

    id: int
    request_id: str
    title: str
    area: float
    description: str

    def __init__(self, id: int, request_id: str = None, title: str = None, area: float = None,
                 description: str = None) -> None:
        self.id = id
        self.request_id = request_id
        self.title = title
        self.area = area
        self.description = description


class ParcelClaim(BaseEntity):
    id: int
    request_id: str  # a Person id
    surveyor_id: str  # a Person id
    claimant_id: str  # a Person id
    neighbouring_point: str  # wkt
    request_timestamp: str
    modify_timestamp: str
    cms: str
    process_instance_id: str

    def __init__(self, id: int = None, request_id: str = None, surveyor_id: str = None,
                 claimant_id: str = None, neighbouring_point: str = None,
                 request_timestamp: str = None, modify_timestamp: str = None, cms: str = None,
                 process_instance_id: str = None) -> None:
        super().__init__()
        self.id = id
        self.request_id = request_id
        self.surveyor_id = surveyor_id
        self.claimant_id = claimant_id
        self.neighbouring_point = neighbouring_point
        self.request_timestamp = request_timestamp
        self.modify_timestamp = modify_timestamp
        self.cms = cms
        self.process_instance_id = process_instance_id


class RegisteredClaim(BaseEntity):
    id: int
    request_id: str  # a Person id
    surveyor_id: str  # a Person id
    claim_tracing_id: str  # a Person id
    create_timestamp: str
    modify_timestamp: str
    status: int
    cms: str
    area: float
    county: str
    state_code: str
    main_plate_number: str
    subsidiary_plate_number: str
    section: str
    district: str
    polygon: str  # parcel polygon which is geometry type in DB and WKT in code
    edges: str  # stored in JSON format in DB but also can be retrieved from ClaimEdge table by request_id
    beneficiary_rights: str
    accommodation_rights: str
    is_apartment: bool
    floor_number: float
    unit_number: float
    orientation: int  # refer to Parcel.Orientation enum
    attachments: List[ClaimParcelAttachment]

    def __init__(self, id: int = None, request_id: str = None, surveyor_id: str = None, claim_tracing_id: str = None,
                 create_timestamp: str = None, modify_timestamp: str = None, status: int = None,
                 cms: str = None, area: float = None, county: str = None, state_code: str = None,
                 main_plate_number: str = None, subsidiary_plate_number: str = None, section: str = None,
                 district: str = None, polygon: str = None, edges: str = None,
                 beneficiary_rights: str = None, accommodation_rights: str = None,
                 is_apartment: bool = None, floor_number: float = None,
                 unit_number: float = None, orientation: int = None, attachments=None) -> None:
        super().__init__()
        self.id = id
        self.request_id = request_id
        self.surveyor_id = surveyor_id
        self.claim_tracing_id = claim_tracing_id
        self.create_timestamp = create_timestamp
        self.modify_timestamp = modify_timestamp
        self.status = status
        self.cms = cms
        self.area = area
        self.county = county
        self.state_code = state_code
        self.main_plate_number = main_plate_number
        self.subsidiary_plate_number = subsidiary_plate_number
        self.section = section
        self.district = district
        self.polygon = polygon
        self.edges = edges
        self.beneficiary_rights = beneficiary_rights
        self.accommodation_rights = accommodation_rights
        self.is_apartment = is_apartment
        self.floor_number = floor_number
        self.unit_number = unit_number
        self.orientation = orientation
        self.attachments = attachments


class ClaimParcelEdge(BaseEntity):
    id: int
    request_id: str
    line_index: int
    length: float
    orientation: int  # refer to Parcel.Orientation enum
    starting_point: str  # line starting point which is geometry type in DB and WKT in code
    ending_point: str  # line ending point which is geometry type in DB and WKT in code
    is_adjacent_to_plate_number: bool
    is_adjacent_to_passage: bool
    passage_name: str
    passage_width: float
    boundary: str  # @finglish: hade fasel

    def __init__(self, id: int, request_id: str = None, line_index: int = None, length: float = None,
                 orientation: int = None, starting_point: str = None, ending_point: str = None,
                 is_adjacent_to_plate_number: bool = None, is_adjacent_to_passage: bool = None,
                 passage_name: str = None, passage_width: float = None, boundary: str = None) -> None:
        self.id = id
        self.request_id = request_id
        self.line_index = line_index
        self.length = length
        self.orientation = orientation
        self.starting_point = starting_point
        self.ending_point = ending_point
        self.is_adjacent_to_plate_number = is_adjacent_to_plate_number
        self.is_adjacent_to_passage = is_adjacent_to_passage
        self.passage_name = passage_name
        self.passage_width = passage_width
        self.boundary = boundary
