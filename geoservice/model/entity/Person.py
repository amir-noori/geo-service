from geoservice.model.entity.common import BaseEntity


class Person(BaseEntity):

    def __init__(self, id=None, first_name=None, last_name=None, national_id=None,
                 phone_number=None, mobile_number=None, birthday=None,
                 address=None, father_name=None) -> None:
                 super().__init__()
                 self.id = id
                 self.first_name = first_name
                 self.last_name = last_name
                 self.national_id = national_id
                 self.phone_number = phone_number
                 self.mobile_number = mobile_number
                 self.birthday = birthday
                 self.address = address
                 self.father_name = father_name