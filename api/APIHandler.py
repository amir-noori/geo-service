from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from .parcels_api import router as parcel_router
from exception.service_exception import ServiceException
from exception.common import ResponseCodes
from model.dto.BaseDTO import Header, BaseResponse
from api.middleware.MockMiddleware import MockMiddleware
from api.middleware.DBLogMiddleware import DBLogMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import os


class APIHandler:

    def __init__(self, app) -> None:
        self.app = app
        self.app_mode = os.environ['app_mode']

        self.handle_routes()
        self.handle_exceptions()
        self.handle_middleware()

    def handle_routes(self):
        self.app.include_router(
            parcel_router,
            prefix="/parcels",
            tags=["parcels"],
        )

    def handle_exceptions(self):

        @self.app.exception_handler(ServiceException)
        def service_exception_handler(request: Request, ex: ServiceException):

            # TODO: messsage_key must be translated
            error_message = ""
            if ex.error_message:
                error_message = ex.error_message
            else:
                error_message = ex.error_code.messsage_key

            header = Header(result_code=ex.error_code.code,
                            result_message=error_message)
            response = BaseResponse(header=header)

            return JSONResponse(
                status_code=ResponseCodes.SUCCESS.code,
                content=jsonable_encoder(response),
            )

    def handle_middleware(self):
        enable_db_log = os.environ['enable_db_log']
        if self.app_mode == "app" and enable_db_log == "true":
            db_log_middleware = DBLogMiddleware()
            self.app.add_middleware(
                BaseHTTPMiddleware, dispatch=db_log_middleware)

        enable_api_mock = os.environ['enable_api_mock']
        if enable_api_mock == "true":
            mock_middleware = MockMiddleware()
            self.app.add_middleware(
                BaseHTTPMiddleware, dispatch=mock_middleware)
