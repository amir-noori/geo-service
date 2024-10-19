
class ResponseCode:

    def __init__(self, code, message_key) -> None:
        self.code = code
        self.messsage_key = message_key

    def __eq__(self, value: object) -> bool:
        return self.code == value.code


class CustomException(Exception):

    def __init__(self, error_code: ResponseCode, error_message="") -> None:
        super().__init__()
        self.error_message = error_message
        self.error_code = error_code


class ResponseCodes:
    
    SUCCESS = ResponseCode(200, "SUCCESS")
    SERVER_ERROR = ResponseCode(500, "SERVER_ERROR")

    NO_PARCEL_FOUND = ResponseCode(10000, "NO_PARCEL_FOUND")
    MULTIPLE_PARCEL_FOUND = ResponseCode(10001, "MULTIPLE_PARCEL_FOUND")
    NO_STATE_FOUND = ResponseCode(10002, "NO_STATE_FOUND")
