from datetime import datetime
from typing import List

from common.str_util import parse_to_int, parse_to_float
from geoservice.data.DBResult import DBResult
from geoservice.data.db_helper import execute_insert, execute_query, execute_update
from geoservice.exception.common import ErrorCodes
from geoservice.exception.persist_exception import CustomerExistsException
from geoservice.exception.service_exception import ServiceException
from geoservice.model.dto.PersonDTO import PersonDTO
from geoservice.model.dto.claim.ClaimDtoReq import ClaimParcelQueryRequestDTO
from geoservice.model.entity.Claim import Claim, ParcelClaim, RegisteredClaim
from geoservice.model.entity.Person import Person
from geoservice.service.person_service import create_person
from log.logger import logger

log = logger()

QUERIES = {
    "insert_claim": """
        insert into TBL_LAND_CLAIM
        (ID, claim_trace_id, request_timestamp, claimed_file_content_type, claimed_file_content, claimed_polygon)
        values (TBL_LAND_CLAIM_SEQ.NEXTVAL, 
            :CLAIM_TRACE_ID, 
            :REQUEST_TIMESTAMP, 
            :CLAIMED_FILE_CONTENT_TYPE,
            :CLAIMED_POLYGON, 
            SDO_UTIL.FROM_WKTGEOMETRY('{polygon}'))
    """,

    "query_claim_by_trace_id": """
        select 
            CLAIM_TRACE_ID, REQUEST_TIMESTAMP, SDO_UTIL.TO_WKTGEOMETRY(CLAIMED_POLYGON) as CLAIMED_POLYGON
        from
            TBL_LAND_CLAIM
        where 
            claim_trace_id = {claim_trace_id}
    """,

    "query_claim_count_by_trace_id": """
        select 
            count(*) as CLAIM_COUNT
        from
            TBL_LAND_CLAIM
        where 
            claim_trace_id = '{claim_trace_id}'
    """,

    "insert_parcel_claim": """
        insert into TBL_PARCEL_CLAIM
        (ID, REQUEST_ID, SURVEYOR_ID, CLAIMANT_ID, NEIGHBOURING_POINT, REQUEST_TIMESTAMP, MODIFY_TIMESTAMP, CMS, PROCESS_INSTANCE_ID)
        values (
            TBL_PARCEL_CLAIM_SEQ.NEXTVAL, 
            :REQUEST_ID, 
            :SURVEYOR_ID, 
            :CLAIMANT_ID,
            :NEIGHBOURING_POINT, 
            :REQUEST_TIMESTAMP, 
            null, -- MODIFY_TIMESTAMP
            :CMS,
            :PROCESS_INSTANCE_ID
            )
    """,

    "query_parcel_claim": """
        SELECT
            ID, REQUEST_ID, SURVEYOR_ID, CLAIMANT_ID, NEIGHBOURING_POINT, REQUEST_TIMESTAMP, MODIFY_TIMESTAMP, CMS, PROCESS_INSTANCE_ID
        FROM TBL_PARCEL_CLAIM
        WHERE 1=1
        
    """,

    "update_parcel_claim": """
        UPDATE TBL_PARCEL_CLAIM SET 
            SURVEYOR_ID = '{SURVEYOR_ID}', CLAIMANT_ID = '{CLAIMANT_ID}', MODIFY_TIMESTAMP = '{MODIFY_TIMESTAMP}'
        WHERE
            1=1
            
    """,

    "insert_registered_claim": """
        INSERT INTO TBL_REGISTERED_CLAIM  
            (
                ID, 
                REQUEST_ID,
                CLAIM_TRACING_ID,
                SURVEYOR_ID, 
                CREATE_TIMESTAMP, 
                MODIFY_TIMESTAMP, 
                STATUS, 
                CMS, 
                AREA, 
                COUNTY, 
                STATE_CODE, 
                MAIN_PLATE_NUMBER, 
                SUBSIDIARY_PLATE_NUMBER, 
                SECTION, 
                DISTRICT, 
                POLYGON, 
                EDGES, 
                BENEFICIARY_RIGHTS, 
                ACCOMMODATION_RIGHTS, 
                IS_APARTMENT, 
                FLOOR_NUMBER, 
                UNIT_NUMBER, 
                ORIENTATION
            )
        VALUES
            (
                TBL_REGISTERED_CLAIM_SEQ.NEXTVAL, 
                :REQUEST_ID, 
                :CLAIM_TRACING_ID,
                :SURVEYOR_ID, 
                :CREATE_TIMESTAMP, 
                :MODIFY_TIMESTAMP, 
                :STATUS, 
                :CMS, 
                :AREA, 
                :COUNTY, 
                :STATE_CODE, 
                :MAIN_PLATE_NUMBER, 
                :SUBSIDIARY_PLATE_NUMBER, 
                :SECTION, 
                :DISTRICT, 
                :POLYGON, 
                :EDGES, 
                :BENEFICIARY_RIGHTS, 
                :ACCOMMODATION_RIGHTS, 
                :IS_APARTMENT, 
                :FLOOR_NUMBER, 
                :UNIT_NUMBER, 
                :ORIENTATION
            )
    """,

    "query_registered_claim": """
        SELECT 
            ID, 
            REQUEST_ID,
            CLAIM_TRACING_ID,
            SURVEYOR_ID, 
            CREATE_TIMESTAMP, 
            MODIFY_TIMESTAMP, 
            STATUS, 
            CMS, 
            AREA, 
            COUNTY, 
            STATE_CODE, 
            MAIN_PLATE_NUMBER, 
            SUBSIDIARY_PLATE_NUMBER, 
            SECTION, 
            DISTRICT, 
            POLYGON, 
            EDGES, 
            BENEFICIARY_RIGHTS, 
            ACCOMMODATION_RIGHTS, 
            IS_APARTMENT, 
            FLOOR_NUMBER, 
            UNIT_NUMBER, 
            ORIENTATION
        FROM TBL_REGISTERED_CLAIM
        WHERE
            REQUEST_ID = '{REQUEST_ID}'
    """

}


def query_claim_parcel(claim_query_request: ClaimParcelQueryRequestDTO) -> Claim:
    def run(db_result: DBResult):
        results = db_result.results

        for result in results:
            trace_id = str(result['CLAIM_TRACE_ID'])
            polygon_wkt = str(result['CLAIMED_POLYGON'])
            request_timestamp = str(result['REQUEST_TIMESTAMP'])

            return Claim(claim_trace_id=trace_id, claimed_polygon=polygon_wkt,
                         request_timestamp=request_timestamp)

        return None

    claim_trace_id = claim_query_request.claim_trace_id
    query_claim = QUERIES['query_claim_by_trace_id'].format(
        claim_trace_id=claim_trace_id
    )

    claim = execute_query(query_claim, run)
    if not claim:
        raise ServiceException(ErrorCodes.NO_CLAIM_FOUND)
    else:
        return claim


def query_claim_parcel_count(claim_trace_id: str) -> int:
    def run(db_result: DBResult):
        results = db_result.results

        for result in results:
            count = str(result['CLAIM_COUNT'])
            return int(count)

        return None

    query_claim = QUERIES['query_claim_count_by_trace_id'].format(
        claim_trace_id=claim_trace_id
    )

    return execute_query(query_claim, run)


def create_new_claim_request(content, content_type, polygon, claim_trace_id):
    params = [claim_trace_id, datetime.now(), content_type, content]
    insert_claim_sql = QUERIES['insert_claim'].format(
        polygon=polygon
    )
    check_trace_id_exists(claim_trace_id)
    execute_insert(insert_claim_sql, params)


def check_trace_id_exists(claim_trace_id):
    claim_count = query_claim_parcel_count(claim_trace_id)

    if claim_count > 0:
        raise ServiceException(ErrorCodes.VALIDATION_CLAIM_TRACE_ID_EXISTS)


### parcel claim services:

def save_new_claim_parcel_request(request_id: str, claimant: PersonDTO, surveyor: PersonDTO,
                                  cms: str, neighbouring_point_wkt: str, process_instance_id: str):
    claimant_person = None
    surveyor_person = None
    try:
        claimant_person = create_person(person_dto_to_person(claimant))
    except CustomerExistsException:
        pass
    try:
        surveyor_person = create_person(person_dto_to_person(surveyor))
    except CustomerExistsException:
        pass

    params = [request_id, claimant_person.id, surveyor_person.id, neighbouring_point_wkt,
              datetime.now(), None, cms, process_instance_id]
    execute_insert(QUERIES['insert_parcel_claim'], params)
    raise Exception("fake error")


def person_dto_to_person(person: PersonDTO) -> Person:
    return Person(
        first_name=person.first_name,
        last_name=person.last_name,
        national_id=person.national_id,
        father_name=person.father_name,
        birthday=person.birthday,
        address=person.address,
        mobile_number=person.mobile_number,
        phone_number=person.phone_number)


def query_parcel_claim_request(request_id: str = None, surveyor_id: str = None, claimant_id: str = None) -> List[
    ParcelClaim]:
    def run(db_result: DBResult):
        results = db_result.results

        parcel_claim_list: list[ParcelClaim] = []
        for result in results:
            id = int(result['ID'])
            queried_request_id = str(result['REQUEST_ID'])
            queried_surveyor_id = str(result['SURVEYOR_ID'])
            queried_claimant_id = str(result['CLAIMANT_ID'])
            neighbouring_point = str(result['NEIGHBOURING_POINT'])
            request_timestamp = str(result['REQUEST_TIMESTAMP'])
            modify_timestamp = str(result['MODIFY_TIMESTAMP'])
            cms = str(result['CMS'])
            process_instance_id = str(result['PROCESS_INSTANCE_ID'])
            parcel_claim = ParcelClaim(
                id=id,
                request_id=queried_request_id,
                surveyor_id=queried_surveyor_id,
                claimant_id=queried_claimant_id,
                neighbouring_point=neighbouring_point,
                request_timestamp=request_timestamp,
                modify_timestamp=modify_timestamp,
                cms=cms,
                process_instance_id=process_instance_id,
            )
            parcel_claim_list.append(parcel_claim)

        return parcel_claim_list

    query = QUERIES['query_parcel_claim']
    if request_id:
        query = query + f" AND REQUEST_ID = '{request_id}' "
    if surveyor_id:
        query = query + f" AND SURVEYOR_ID = '{surveyor_id}' "
    if surveyor_id:
        query = query + f" AND CLAIMANT_ID = '{claimant_id}' "

    result_claims = execute_query(query, run)
    log.debug(result_claims)
    return result_claims


def update_parcel_claim_request(parcel_claim: ParcelClaim):
    if not parcel_claim.request_id:
        raise ServiceException(ErrorCodes.METHOD_INPUT_ERROR, "parcel_claim request_id cannot be null")

    query = QUERIES['update_parcel_claim'].format(
        SURVEYOR_ID=parcel_claim.surveyor_id,
        CLAIMANT_ID=parcel_claim.claimant_id,
        MODIFY_TIMESTAMP=datetime.now()
    )

    query = query + f" AND REQUEST_ID = {parcel_claim.request_id} "
    execute_update(query)


def save_new_registered_parcel_claim_request(registered_claim: RegisteredClaim) -> RegisteredClaim:
    params = [registered_claim.request_id, registered_claim.claim_tracing_id, registered_claim.surveyor_id,
              datetime.now(), None,
              registered_claim.status, registered_claim.cms, registered_claim.area,
              registered_claim.county, registered_claim.state_code,
              registered_claim.main_plate_number, registered_claim.subsidiary_plate_number,
              registered_claim.section, registered_claim.district, registered_claim.polygon,
              registered_claim.edges, registered_claim.beneficiary_rights, registered_claim.accommodation_rights,
              registered_claim.is_apartment, registered_claim.floor_number, registered_claim.unit_number,
              registered_claim.orientation]
    query = QUERIES['insert_registered_claim']
    execute_insert(query, params)

    return RegisteredClaim()


def query_registered_parcel_claim_request(registered_claim: RegisteredClaim) -> RegisteredClaim | None:
    def run(db_result: DBResult):
        results = db_result.results

        registered_claim_list: list[RegisteredClaim] = []
        for result in results:
            id = int(result['ID'])
            request_id = str(result['REQUEST_ID'])
            claim_tracing_id = str(result['CLAIM_TRACING_ID'])
            surveyor_id = str(result['SURVEYOR_ID'])
            create_timestamp = str(result['CREATE_TIMESTAMP'])
            modify_timestamp = str(result['MODIFY_TIMESTAMP'])
            status = str(result['STATUS'])
            cms = str(result['CMS'])
            area = str(result['AREA'])
            county = str(result['COUNTY'])
            state_code = str(result['STATE_CODE'])
            main_plate_number = str(result['MAIN_PLATE_NUMBER'])
            subsidiary_plate_number = str(result['SUBSIDIARY_PLATE_NUMBER'])
            section = str(result['SECTION'])
            district = str(result['DISTRICT'])
            edges = str(result['EDGES'])
            beneficiary_rights = str(result['BENEFICIARY_RIGHTS'])
            accommodation_rights = str(result['ACCOMMODATION_RIGHTS'])
            is_apartment = bool(result['IS_APARTMENT'])
            floor_number = str(result['FLOOR_NUMBER'])
            unit_number = str(result['UNIT_NUMBER'])
            orientation = str(result['ORIENTATION'])

            result_registered_claim = RegisteredClaim(
                id=id,
                request_id=request_id,
                claim_tracing_id=claim_tracing_id,
                surveyor_id=surveyor_id,
                create_timestamp=create_timestamp,
                modify_timestamp=modify_timestamp,
                status=parse_to_int(status),
                cms=cms,
                area=parse_to_float(area),
                county=county,
                state_code=state_code,
                main_plate_number=main_plate_number,
                subsidiary_plate_number=subsidiary_plate_number,
                section=section,
                district=district,
                edges=edges,
                beneficiary_rights=beneficiary_rights,
                accommodation_rights=accommodation_rights,
                is_apartment=is_apartment,
                floor_number=parse_to_float(floor_number),
                unit_number=parse_to_float(unit_number),
                orientation=parse_to_int(orientation, 8),
            )
            registered_claim_list.append(result_registered_claim)

        return registered_claim_list

    query = QUERIES['query_registered_claim'].format(
        REQUEST_ID=registered_claim.request_id)

    registered_claims = execute_query(query, run)
    log.debug(registered_claims)
    if registered_claims:
        return registered_claims[0]
    else:
        return None
