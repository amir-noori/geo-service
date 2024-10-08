
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional, Type, Any, Tuple
from copy import deepcopy
from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo
from util.object_util import toJSON



def partial_model(model: Type[BaseModel]):
    """
        making DTO class fields optional
    """
    def make_field_optional(field: FieldInfo, default: Any = None) -> Tuple[Any, FieldInfo]:
        new = deepcopy(field)
        new.default = default
        new.annotation = Optional[field.annotation]  # type: ignore
        return new.annotation, new
    return create_model(
        f'Partial{model.__name__}',
        __base__=model,
        __module__=model.__module__,
        **{
            field_name: make_field_optional(field_info)
            for field_name, field_info in model.__fields__.items()
        }
    )


class BaseDTO(BaseModel):
    
    def toJSON(self):
        return toJSON(self)

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    def set_service_key(self, value):
        """
            each service call should be logged in a database or file and must be 
            traced through a service key.
        """
        pass

    def get_service_key(self):
        pass


@partial_model
class Header(BaseDTO):
    
    result_code: str
    result_message: str

    def __init__(self, result_code=None, result_message=None) -> None:
        super().__init__()
        self.result_code = result_code
        self.result_message = result_message



@partial_model
class BaseResponse(BaseModel):
    
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
    
    header: Header

    def __init__(self, header=None) -> None:
        super().__init__()
        self.header = header
    