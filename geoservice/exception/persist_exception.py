from geoservice.model.entity.Person import Person


class CustomerExistsException(Exception):

    person: Person

    def __init__(self, person):
        self.person = person

