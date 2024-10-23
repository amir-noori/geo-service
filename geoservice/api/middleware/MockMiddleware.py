from fastapi import Request
from fastapi.responses import JSONResponse
from integration.service.api_description_service import find_api_description
from log.logger import logger


class MockMiddleware():
    def __init__(self):
        pass

    async def __call__(self, request: Request, call_next):
        logger().error("mock middleware called")

        api_key = request.url.path
        if api_key.endswith("/"):
            api_key = api_key[:-1]

        api_desc = find_api_description(api_key)

        if api_desc.is_enabled and api_desc.is_mocked:
            return JSONResponse(content=api_desc.mocked_response, status_code=200)
        else:
            return await call_next(request)
