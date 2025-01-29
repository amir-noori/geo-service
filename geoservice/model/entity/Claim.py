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
