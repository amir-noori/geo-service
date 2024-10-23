from fastapi import Request
from starlette.concurrency import iterate_in_threadpool

from integration.service.message_log_service import save_db_message_log
from integration.model.entity.DbMessageLog import DbMessageLog
from datetime import datetime
import traceback
from log.logger import logger

class DBLogMiddleware:

    log = logger()
    def __init__(self):
        pass

    async def __call__(self, request: Request, call_next):
        
        self.log.debug("db log middleware called.")

        exception = None
        request_time = None
        response = None
        response_time = None
        response_body = None

        try:
            request_time = datetime.now()
            response = await call_next(request)
            response_time = datetime.now()
        except Exception as e:
            exception = e

        # once the response body is read it cannot be read again. the following code is to overcome that
        if not exception:
            response_body = [chunk async for chunk in response.body_iterator]
            response.body_iterator = iterate_in_threadpool(iter(response_body))

        response_txt = None
        if response_body:
            response_txt = str(response_body[0].decode())

        request_body = await request.body()
        db_message_log = DbMessageLog(request=request_body.decode("utf-8"),
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
        save_db_message_log(db_message_log)
        self.log.debug("insert service log to DB.")
        return response
