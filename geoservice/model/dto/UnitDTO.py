from geoservice.model.dto.BaseDTO import BaseResponse, BaseDTO, partial_model


@partial_model
class UnitDTO(BaseDTO):

    cms: str
    unit_id: str
    unit_name: str

    def __init__(self, cms=None, unit_id=None, unit_name=None) -> None:
        super().__init__()
        self.cms = cms
        self.unit_id = unit_id
        self.unit_name = unit_name

@partial_model
class UnitResponse(BaseResponse):

    body: UnitDTO

    def __init__(self, body: UnitDTO = None, header=None) -> None:
        super().__init__(header=header)
        self.body = body