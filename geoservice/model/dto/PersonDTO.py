from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class PersonDTO(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True
    )

    first_name: str
    last_name: str
    national_id: str
    phone_number: str
    mobile_number: str
    birthday: str
    address: str
    father_name: str
