from functools import wraps
from geoservice.model.dto.BaseDTO import BaseDTO, BaseRequest
from fastapi.requests import Request
from fastapi import APIRouter
from log.logger import logger
from pydantic import BaseModel


def route(router: APIRouter, method: str, path: str, response_model=None):

    router_decorator = None
    method = method.upper()
    log = logger()

    if method == "GET":
        if response_model:
            router_decorator = router.get(path, response_model=response_model)
        else:
            router_decorator = router.get(path)

    elif method == "POST":
        if response_model:
            router_decorator = router.post(path, response_model=response_model)
        else:
            router_decorator = router.post(path)
    else:
        raise ValueError(f"http method {method} is not supported!")

    def decorator(fn):

        @wraps(fn)
        async def wrapper(*args, **kwargs):
            service_key = None

            for key, obj in kwargs.items():
                if isinstance(obj, BaseDTO):
                    log.debug("getting service key from request")
                    service_key = obj.get_service_key()

                if isinstance(obj, BaseModel):
                    log.debug("getting service key from request")
                    service_key = obj.get_service_key()

                if isinstance(obj, BaseRequest):
                    log.debug("getting service key from request")
                    obj = obj.get_service_key()

            # kwargs should be iterated second time to ensure service_key is already found before setting it in request scope
            for key, obj in kwargs.items():
                if isinstance(obj, Request):
                    log.debug("setting service key in scope.")
                    log.debug(f"service_key: {service_key}, service_name: {path}")
                    obj.scope["service_key"] = service_key
                    if path:
                        obj.scope["service_name"] = path.replace("/", "")

            return await fn(*args, **kwargs)

        return router_decorator(wrapper)
    return decorator
