from typing import List

from common.date_util import str_to_date
from geoservice.data.DBResult import DBResult
from geoservice.data.db_helper import execute_query, execute_insert, next_seq
from geoservice.exception.persist_exception import CustomerExistsException
from geoservice.model.dto.PersonDTO import PersonDTO
from geoservice.model.entity.Person import Person
from log.logger import logger

log = logger()

QUERIES = {
    "query_person": """
        SELECT ID, FIRST_NAME, LAST_NAME, NATIONAL_ID, PHONE_NUMBER, MOBILE_NUMBER, FATHER_NAME, BIRTHDAY, ADDRESS FROM TBL_PERSON
        WHERE
            1 = 1
    """,

    "insert_person": """
        INSERT INTO TBL_PERSON (ID, FIRST_NAME, LAST_NAME, NATIONAL_ID, PHONE_NUMBER, MOBILE_NUMBER, FATHER_NAME, BIRTHDAY, ADDRESS)
        VALUES(:ID, :FIRST_NAME, :LAST_NAME, :NATIONAL_ID, :PHONE_NUMBER, :MOBILE_NUMBER, :FATHER_NAME, :BIRTHDAY, :ADDRESS)
    """
}


def query_person(person: Person) -> List[Person]:
    def run(db_result: DBResult):
        results = db_result.results
        people = []

        for result in results:
            retrieved_person = Person(
                id=str(result['ID']),
                first_name=str(result['FIRST_NAME']),
                last_name=str(result['LAST_NAME']),
                national_id=str(result['NATIONAL_ID']),
                phone_number=str(result['PHONE_NUMBER']),
                mobile_number=str(result['MOBILE_NUMBER']),
                father_name=str(result['FATHER_NAME']),
                birthday=str(result['BIRTHDAY']),
                address=str(result['ADDRESS'])
            )
            log.debug(f"retrieved person: {retrieved_person}")
            people.append(retrieved_person)

        return people

    query = QUERIES['query_person']
    if person.id:
        query = query + f" AND ID = '{person.id}' "
    if person.first_name:
        query = query + f" AND FIRST_NAME = '{person.first_name}' "
    if person.last_name:
        query = query + f" AND LAST_NAME = '{person.last_name}' "
    if person.national_id:
        query = query + f" AND NATIONAL_ID = '{person.national_id}' "

    return execute_query(query, run)


def create_person(person: Person) -> Person:
    queried_person: List[Person] = query_person(Person(national_id=person.national_id))

    if queried_person and queried_person[0].id:
        raise CustomerExistsException(queried_person[0])

    id = next_seq("TBL_PERSON_SEQ")

    query = QUERIES['insert_person']
    birthday = str_to_date(person.birthday) if person.birthday else None
    params = {
        'FIRST_NAME': person.first_name,
        'LAST_NAME': person.last_name,
        'NATIONAL_ID': person.national_id,
        'PHONE_NUMBER': person.phone_number,
        'MOBILE_NUMBER': person.mobile_number,
        'FATHER_NAME': person.father_name,
        'BIRTHDAY': birthday,
        'ADDRESS': person.address,
        'ID': id
    }
    execute_insert(query, params)
    person.id = id
    return person
