import os

from zeep import Client

from geoservice.exception.common import ErrorCodes
from geoservice.exception.service_exception import ServiceException
from geoservice.model.dto.PersonDTO import PersonDTO
from geoservice.model.entity.Claim import ParcelClaim


def call_tom_assign_surveyor(parcel_claim: ParcelClaim,
                             claimant: PersonDTO,
                             surveyor: PersonDTO):
    wsdl_url = os.environ.get("TOM_SERVICE_URL", "http://localhost:7979/RequestWS.asmx?WSDL")

    # Create a client
    client = Client(wsdl_url)

    # Prepare the request data
    request_data = {
        "nationalCode": claimant.national_id,
        "firstName": claimant.first_name,
        "lastName": claimant.last_name,
        "fatherName": claimant.father_name,
        "isOrganization": False,  # TODO: for now it is not
        "mobile": claimant.mobile_number,
        "address": claimant.address,
        "PostalCode": "",  # TODO
        "cms": parcel_claim.cms,
        "area": 0.0,  # TODO
        "requestNum": parcel_claim.request_id,
        "descriptions": "",  # TODO
        "tag": "",  # TODO
        "surveyNationalCode": surveyor.national_id
    }

    try:
        response = client.service.CreateElzamRequset(**request_data)

        if not response.successful:
            raise ServiceException(ErrorCodes.INTEGRATION_EXTERNAL_SERVICE_ERROR,
                                   f"cannot call TOM assign surveyor service, error: {response.errorMessage}, sms message: {response.SmsMessage}")

        assigned_surveyor: PersonDTO = PersonDTO()
        if response:
            assigned_surveyor.first_name = response.SurveyName
            assigned_surveyor.last_name = response.SurveyLastname
            assigned_surveyor.national_id = response.SurveyNationalCode
            assigned_surveyor.address = response.SurveyName
            assigned_surveyor.mobile_number = response.SurveyName
        else:
            raise ServiceException(ErrorCodes.INTEGRATION_EXTERNAL_SERVICE_ERROR,
                                   "cannot call TOM assign surveyor service, error: No response received")

        return assigned_surveyor, response.FollowCode, response.SmsMessage

    except Exception as e:
        raise ServiceException(ErrorCodes.INTEGRATION_EXTERNAL_SERVICE_ERROR,
                               f"cannot call TOM assign surveyor service, error: {e}")
