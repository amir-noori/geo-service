from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from geoservice.model.dto.BaseDTO import partial_model


@partial_model
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

    @classmethod
    def from_dict(cls, person_dict):
        person_dto = PersonDTO()
        person_dto.first_name = person_dict.get('first_name', person_dict.get('firstName'))
        person_dto.last_name = person_dict.get('last_name', person_dict.get('lastName'))
        person_dto.national_id = person_dict.get('national_id', person_dict.get('nationalId'))
        person_dto.phone_number = person_dict.get('phone_number', person_dict.get('phoneNumber'))
        person_dto.mobile_number = person_dict.get('mobile_number', person_dict.get('mobileNumber'))
        person_dto.birthday = person_dict['birthday']
        person_dto.address = person_dict['address']
        person_dto.father_name = person_dict.get('father_name', person_dict.get('fatherName'))
        return person_dto

