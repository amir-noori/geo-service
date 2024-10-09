from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from .parcels_api import router as parcel_router
from exception.service_exception import ServiceException
from exception.common import ErrorCodes
from model.dto.BaseDTO import Header, BaseResponse


class APIHandler:

    def __init__(self, app) -> None:
        self.app = app

        self.handle_routes()
        self.handle_exceptions()

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
                status_code=ErrorCodes.SERVER_ERROR.code,
                content=jsonable_encoder(response),
            )
