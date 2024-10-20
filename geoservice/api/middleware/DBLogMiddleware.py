from fastapi import Request
from starlette.concurrency import iterate_in_threadpool

from integration.service.message_log_service import save_db_message_log
from integration.model.entity.DbMessageLog import DbMessageLog
from datetime import datetime
import traceback


class DBLogMiddleware:
    def __init__(self):
        pass

    async def __call__(self, request: Request, call_next):
        print("db log middleware called.")

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
        db_message_log = DbMessageLog.create_message_log(request, response_txt)
        if exception:
            exception_txt = repr(exception) + " ---> " + ''.join(
                traceback.TracebackException.from_exception(exception).format())
            db_message_log.exception = exception_txt
            print(exception_txt)
            
        db_message_log.request_time = request_time
        db_message_log.response_time = response_time
        save_db_message_log(db_message_log)
        print("insert service log to DB.")
        return response
