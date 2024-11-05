import json
import os
from functools import wraps

import requests
from fastapi.responses import JSONResponse

from geoservice.common.states import state_to_db_mapping
from geoservice.util.common_util import get_state_ip_by_code
from log.logger import logger

app_mode = os.environ["app_mode"]
log = logger()


def dispatch(dispatch_event):
    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            if app_mode == "dispatcher":
                request = kwargs['request']
                method = request.method
                body = None
                if method and str(method).upper() == "POST":
                    body = await request.json()

                request_url = request.url
                headers_binary = dict(request["headers"])
                authorization_header = ""
                try:
                    authorization_header = headers_binary["authorization".encode()].decode()
                except KeyError as e:
                    log.debug(f"KeyError: {e}")

                state_code = dispatch_event.fire({"data": kwargs})
                log.debug(f"dispatch key: {state_code}")
                redirect_url = get_service_provider_url(request, state_code)
                log.debug(
                    f"redirecting from url: {request_url} to {redirect_url}")
                result = do_call_service_provider(url=str(redirect_url),
                                                  headers={
                                                      "Authorization": authorization_header},
                                                  body=body)
                return result
            else:
                return fn(*args, **kwargs)

        return wrapper

    return decorator


def get_service_provider_url(request, state_code: str) -> str:
    service_ip = get_state_ip_by_code(state_code)
    redirect_url = f"http://{service_ip}{request.url.path}"
    if request.query_params:
        redirect_url = redirect_url + f"/?{request.query_params}"
    return redirect_url


def do_call_service_provider(url, headers=None, body=None):
    response = None
    if body:
        log.debug(f"call service begin [POST]")
        print(headers, body)
        response = requests.post(url, headers=headers, json=body)
    else:
        log.debug(f"call service begin [GET]")
        response = requests.get(url, headers=headers)

    log.debug(f"service called, status code: {response.status_code}")
    return JSONResponse(content=json.loads(response.content.decode('utf-8')), status_code=response.status_code)


def get_header_for_dispatcher():
    dispatcher_http_channel = os.environ['dispatcher_http_channel']
    dispatcher_http_password = os.environ['dispatcher_http_password']
    return {"Authorization": f"{dispatcher_http_channel}:{dispatcher_http_password}"}


def call_all_service_providers(url_path: str, get_callback=None, post_callback=None):
    header = get_header_for_dispatcher()

    for state_code, address in state_to_db_mapping.items():
        if address:
            address_split = address.split(":")
            ip = address_split[0]
            port = address_split[1]
            url = f"http://{ip}:{port}{url_path}"
            log.debug(f"calling URL: {url} to clear cache.")
            try:
                if get_callback:
                    response = requests.get(url, headers=header)
                    get_callback(response)
                elif post_callback:
                    pass  # TODO

            except Exception as e:
                log.error_bold(f"""
                                error connecting to server {url}
                                Exception: {e}
                              """)
