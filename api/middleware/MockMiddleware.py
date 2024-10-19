from fastapi import Request
from fastapi.responses import JSONResponse


class MockMiddleware():
    def __init__(self):
        pass

    async def __call__(self, request: Request, call_next):
        print("mock middleware called")

        return JSONResponse(content={"mock": True}, status_code=200)
