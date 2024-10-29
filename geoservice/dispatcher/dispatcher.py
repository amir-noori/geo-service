
import types
from functools import wraps
import requests
import json
import os
from geoservice.util.common_util import get_state_ip_by_code
from fastapi.responses import JSONResponse
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
                    print("type -> ", type(body))
                    print("body -> ", body)

                request_url = request.url
                headers_binary = dict(request["headers"])
                authorization_header = ""
                try:
                    authorization_header = headers_binary["authorization".encode(
                    )].decode()
                except KeyError as e:
                    print("KeyError: ", e)

                state_code = dispatch_event.fire({"data": kwargs})
                log.debug(f"dispatch key: {state_code}")
                service_ip = get_state_ip_by_code(state_code)
                redirect_url = f"http://{service_ip}{request.url.path}"
                if request.query_params:
                    redirect_url = redirect_url + f"/?{request.query_params}"
                log.debug(
                    f"redirecting from url: {request_url} to {redirect_url}")
                result = call_service_provider(url=str(redirect_url),
                                               headers={
                                                   "Authorization": authorization_header},
                                               body=body)
                return result
            else:
                return fn(*args, **kwargs)

        return wrapper
    return decorator


def call_service_provider(url, headers=None, body=None):
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


def decorate_api_functions(module):
    for name in dir(module):
        obj = getattr(module, name)
        if name.endswith("_api") and isinstance(obj, types.FunctionType):
            log.debug(
                f"decorating api functions in {name} and obj {obj} for dispatch")
            setattr(module, name, dispatch(obj))
