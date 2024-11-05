from fastapi import Request
from starlette.concurrency import iterate_in_threadpool

from integration.service.message_log_service import save_db_message_log
from integration.service.api_description_service import find_api_description
from integration.model.entity.DbMessageLog import DbMessageLog
from datetime import datetime
import traceback
import json
from log.logger import logger
from starlette.responses import Response


class DBLogMiddleware:

    log = logger()

    def __init__(self):
        pass

    async def __call__(self, request: Request, call_next):

        self.log.debug("db log middleware called.")

        method = request.method.upper()

        exception = None
        request_time = None
        response: Response = None
        response_time = None
        response_body = None
        request_body = None
        request_txt = None
        response_txt = None
        
        api_key = request.url.path
        if api_key.endswith("/"):
            api_key = api_key[:-1]

        api_desc = find_api_description(api_key)

        try:

            try:
                request_time = datetime.now()
                response = await call_next(request)
                if api_desc and not api_desc.is_log_enabled:
                    return response
                response_time = datetime.now()
            except Exception as e:
                exception = e

            # once the response body is read it cannot be read again. the following code is to overcome that
            if not exception:
                response_body = [chunk async for chunk in response.body_iterator]
                response.body_iterator = iterate_in_threadpool(
                    iter(response_body))


            if response_body:
                response_txt = str(response_body[0].decode())

            if method != "GET":
                try:
                    request_body = request.scope["request_body"]
                except KeyError as e:
                    """
                        cause for some reason (probably auth failure) request_body is not available
                        we can await the body in order to get the request json.
                        This might not be an issue (since the request can be read only once) cause 
                        DB log middleware must be tha last thing to be called on teh stack.
                    """
                    request_body = await request.json()

        except Exception as e:
            exception = e

        if request_body:
            request_txt = json.dumps(request_body)

        db_message_log = DbMessageLog(request=request_txt,
                                      response=response_txt,
                                      method=request.method,
                                      request_url=str(request.url),
                                      source_ip=str(request.client.host))
        # db_message_log = DbMessageLog.create_message_log(request, response_txt)
        if exception:
            exception_txt = repr(exception) + " ---> " + ''.join(
                traceback.TracebackException.from_exception(exception).format())
            db_message_log.exception = exception_txt
            self.log.error(exception_txt)

        service_key = None
        service_name = None
        channel_id = None
        try:
            service_key = request.scope["service_key"]
        except KeyError:
            pass

        try:
            service_name = request.scope["service_name"]
        except KeyError:
            pass

        try:
            channel_id = request.scope["channel_id"]
        except KeyError:
            pass

        db_message_log.service_key = service_key
        db_message_log.service_name = service_name
        db_message_log.channel_id = channel_id

        db_message_log.request_time = request_time
        db_message_log.response_time = response_time
        

        do_log = True
        try:        
            # to ignore db log for redirect requests
            if response and response.headers['content-length'] == '0' and not request_txt and not response_txt:
                do_log = False
        except KeyError:
            pass

        if do_log:
            save_db_message_log(db_message_log)
            self.log.debug("insert service log to DB.")        
        
        if exception:
            raise exception

        return response
