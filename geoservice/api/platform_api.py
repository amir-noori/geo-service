import os

from fastapi import APIRouter, Request

from common.cache import clear_all_cache
from geoservice.api.common import handle_response
from geoservice.dispatcher.dispatcher import call_all_service_providers
from geoservice.model.dto.ParcelReqLog import *
from log.logger import logger

router = APIRouter()
log = logger()


@router.get(path="/clear_all_cache", response_model=BaseResponse)
def clear_all_cache_api(request: Request):
    app_mode = os.environ["app_mode"]

    if app_mode == "dispatcher":

        def clear_cache_callback(resp):
            if resp:
                if resp.status_code == 200:
                    log.debug(f"cleared cache successfully")
                else:
                    log.debug(f"{resp.status_code} , {resp.content}")
            else:
                log.error("there is no response from ")

        call_all_service_providers(url_path="/platform/clear_all_cache", get_callback=clear_cache_callback)

    # if app is in dispatcher mode or not we should clear the cache
    clear_all_cache()

    response = BaseResponse()
    return handle_response(request, response)
