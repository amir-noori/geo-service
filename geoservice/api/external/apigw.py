import math
import os

import requests

from common.cache import cached
from geoservice.exception.common import ErrorCodes
from geoservice.exception.service_exception import ServiceException
from log.logger import logger

log = logger()

# token expire time is 300 hence the retrieved token should be expired in 300 * 0.9 = 270
token_expire_duration = math.floor(int(os.environ.get("TOKEN_EXPIRE_DURATION", 300)) * 0.9)


@cached(seconds=token_expire_duration)
def apigw_get_token() -> str:
    url = os.environ.get("API_GW_GET_TOKEN_URL", "http://localhost:7979/get-token")
    client_id = os.environ.get("CLIENT_ID", "100")
    client_secret = os.environ.get("CLIENT_SECRET", "123")
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentails',
        'client_id': client_id,
        'client_secret': client_secret
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        access_token = response.json()["access_token"]
        return access_token
    else:
        error_message = f"error calling api gateway get token: status_code: {response.status_code}, response: {response.text}"
        log.error(error_message)
        raise ServiceException(ErrorCodes.INTEGRATION_EXTERNAL_SERVICE_ERROR, error_message)


def call_downstream_service_post(service_url: str, headers: dict = None, payload: dict = None):
    if headers is None:
        headers = {}

    bypass_api_gw_auth = os.environ.get("BYPASS_API_GW_AUTH", "false")
    if bypass_api_gw_auth == "false":
        token: str = apigw_get_token()
        headers['Authorization'] = f'Bearer {token}'
        headers['Content-Type'] = 'application/json'
    try:
        response = requests.post(service_url, headers=headers, json=payload)  # Using POST as an example
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        error_message = f"error calling downstream service at {service_url}: {e}"
        log.error(error_message)
        raise ServiceException(ErrorCodes.INTEGRATION_EXTERNAL_SERVICE_ERROR, error_message)
