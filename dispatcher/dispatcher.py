
import types
from functools import wraps
import requests
import json
import os
from util.common_util import get_state_ip_by_code
from common.ApplicationContext import ApplicationContext


app_mode = os.environ["app_mode"]


def dispatch(dispatch_event):
    def decorator(fn):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            if app_mode == "dispatcher":
                request = kwargs['request']
                request_url = request.url
                state_code = dispatch_event.fire({"data": kwargs})
                print(f"dispatch key: {state_code}")
                service_ip = get_state_ip_by_code(state_code)
                service_port = os.environ["service_provider_port"]
                redirect_url = f"http://{service_ip}:{service_port}/{request.url.path}/?{request.query_params}"
                print(f"redirecting from url: {request_url} to {redirect_url}")
                # return call_service_provider(str(request_url))
                return {}
            else:
                return fn(*args, **kwargs)

        return wrapper
    return decorator


def call_service_provider(url):
    response = requests.get(url)
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))


def decorate_api_functions(module):
    for name in dir(module):
        obj = getattr(module, name)
        if name.endswith("_api") and isinstance(obj, types.FunctionType):
            print(
                f"decorating api functions in {name} and obj {obj} for dispatch")
            setattr(module, name, dispatch(obj))
