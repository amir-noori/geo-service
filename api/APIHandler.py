

from .parcels import router as parcel_router


class APIHandler:

    def __init__(self, app) -> None:
        self.app = app

        self.handle_routes()

    def handle_routes(self):
        self.app.include_router(
            parcel_router,
            prefix="/parcels",
            tags=["parcels"],
        )


