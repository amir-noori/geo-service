import uuid


class DbMessageLog():

    def __init__(self, request=None, response=None, request_url=None,
                 service_key=None, exception=None, request_time=None,
                 response_time=None, method=None, source_ip=None,
                 destination_ip=None) -> None:
        self.tracking_id = str(uuid.uuid1())
        self.request = request
        self.response = response
        self.request_url = request_url
        self.service_key = service_key
        self.exception = exception
        self.request_time = request_time
        self.response_time = response_time
        self.method = method
        self.source_ip = source_ip
        self.destination_ip = destination_ip

    @staticmethod
    def create_message_log(request, response_body):
          
        return DbMessageLog(request=str(request.json()), 
                            response=response_body, 
                            method=request.method, 
                            request_url=str(request.url), 
                            source_ip=str(request.client.host))
