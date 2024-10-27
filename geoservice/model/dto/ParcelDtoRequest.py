from typing_extensions import Unpack
from pydantic import ConfigDict, Field, BaseModel

class ParcelInfoRequestDTO(BaseModel):
    longtitude: float = Field(...)
    latitude: float = Field(...)
    srid: str = Field("4326")
    distance: float = Field(10, ge=0, description="Distance maximum default is 200")

    def get_service_key(self):
        return f"({self.longtitude},{self.latitude})"
