import base64
import os
import json

import requests
from fastapi.encoders import jsonable_encoder
from fastapi import status
from pydantic import BaseModel

from geoservice.exception.common import ErrorCodes
from geoservice.exception.service_exception import ServiceException
from log.logger import logger

log = logger()


def get_cadastre_url():
    cadastre_host = os.getenv('cadastre_host', '')
    cadastre_port = os.getenv('cadastre_port', '')
    cadastre_protocol = os.getenv('cadastre_protocol', 'http')
    cadastre_base_path = os.getenv('cadastre_base_path', '')
    base_url = f"{cadastre_protocol}://{cadastre_host}:{cadastre_port}/{cadastre_base_path}"
    return base_url


def get_request_headers():
    channel_id = os.getenv('saghar_channel_id', '200')
    password = os.getenv('saghar_channel_password', '123')
    credentials = base64.b64encode(f"{channel_id}:{password}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    return headers


def call_cadastre_api(request_model: BaseModel, response_class, service_path: str):
    url = get_cadastre_url() + service_path
    headers = get_request_headers()
    response = requests.post(url, headers=headers, json=jsonable_encoder(request_model))
    if response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        log.error(response.text)
        raise ServiceException(ErrorCodes.SERVER_UNAVAILABLE)

    json_response =  response.json()
    response_model = response_class.model_validate_json(json.dumps(json_response))
    return response_model

