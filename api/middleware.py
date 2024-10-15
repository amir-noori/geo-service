from fastapi import Request
from starlette.concurrency import iterate_in_threadpool

from service.integration_service import save_db_message_log
from model.entity.DbMessageLog import DbMessageLog
from datetime import datetime
import traceback


class DBLogMiddleware:
    def __init__(self):
        pass

    async def __call__(self, request: Request, call_next):
        print("db log middleware called.", str(request.headers))
        traceback.print_stack()

        request_time = datetime.now()
        response = await call_next(request)
        response_time = datetime.now()

        # once the response body is read it cannot be read again, the following code is to overcome that
        response_body = [chunk async for chunk in response.body_iterator]
        response.body_iterator = iterate_in_threadpool(iter(response_body))

        response_txt = None
        if response_body:
            response_txt = str(response_body[0].decode())
        db_message_log = DbMessageLog.create_message_log(request, response_txt)
        db_message_log.request_time = request_time
        db_message_log.response_time = response_time
        save_db_message_log(db_message_log)
        print("insert service log to DB.")
        return response
