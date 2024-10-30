
from geoservice.util.object_util import toJSON


class BaseEntity:
    
    def toJSON(self):
        return toJSON(self)
    
    def __str__(self) -> str:
        return self.toJSON()