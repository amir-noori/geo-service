import base64
import hashlib

from fastapi import Request
from fastapi import status
from fastapi.responses import JSONResponse

from integration.service.api_description_service import find_api_description
from integration.service.channel_service import find_channel
from log.logger import logger


class AuthenticationMiddleware:
    log = logger()

    def __init__(self):
        pass

    def retrieve_auth_header(self, request: Request):
        headers = request.headers
        self.log.debug("headers are " + f"{headers}")

        auth_header = None
        channel_id = None
        auth_key = None
        try:
            # if the credentials is passed as clear text Authorization header (Basic aaa:123)
            auth_header = headers['Authorization']
            if auth_header:
                if auth_header.lower().startswith("basic"):
                    auth_header = auth_header[5:len(auth_header)].strip()

            auth_header_split = auth_header.split(":")
            channel_id = auth_header_split[0]
            auth_key = auth_header_split[1]
        except (KeyError, IndexError):
            try:
                # if the credentials is passed as base64 Authorization header (Basic YWFhOjEyMw==)
                channel_id, auth_key = base64.b64decode(auth_header).decode().split(":")
            except (UnicodeDecodeError, IndexError, TypeError):
                pass

        request.scope["channel_id"] = channel_id

        return auth_header, channel_id, auth_key

    async def __call__(self, request: Request, call_next):
        self.log.debug("auth middleware called")

        auth_header, channel_id, auth_key = self.retrieve_auth_header(request)

        api_key = request.url.path
        if api_key.endswith("/"):
            api_key = api_key[:-1]

        api_desc = find_api_description(api_key)

        if not api_desc or not api_desc.is_enabled:
            self.log.debug(
                f"service is not available with api_key: {api_key}, api_desc: {api_desc}")
            return JSONResponse(content={'status': 'service is not available (enabled)'},
                                status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

        if api_desc.bypass_auth:
            return await call_next(request)

        else:
            self.log.debug("trying to authenticate")
            try:
                channel_id = int(channel_id)
            except ValueError:
                channel_id = None
            except TypeError:
                channel_id = None

            channel = find_channel(channel_id)
            if not auth_header or \
                    not auth_key or \
                    not channel or \
                    channel.auth_key != hashlib.md5(f"[{channel_id}:{auth_key.strip()}]".encode()).hexdigest():
                self.log.debug(
                    f"authentication failed for auth_header: {auth_header}, channel_id: {channel_id}, channel: {channel}")
                response = {
                    "header": {
                        "result_code": status.HTTP_401_UNAUTHORIZED,
                        "result_message": 'not authorized'
                    }
                }
                return JSONResponse(content=response,
                                    status_code=status.HTTP_401_UNAUTHORIZED)

        return await call_next(request)
