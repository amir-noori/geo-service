
class ErrorCode:

    def __init__(self, code, message_key) -> None:
        self.code = code
        self.messsage_key = message_key

    def __eq__(self, value: object) -> bool:
        return self.code == value.code


class CustomException(Exception):

    def __init__(self, error_code: ErrorCode, error_message="") -> None:
        self.error_message = error_message
        self.error_code = error_code


class ErrorCodes:

    SERVER_ERROR = ErrorCode(500, "SERVER_ERROR")

    NO_PARCEL_FOUND = ErrorCode(10000, "NO_PARCEL_FOUND")
    MULTIPLE_PARCEL_FOUND = ErrorCode(10001, "MULTIPLE_PARCEL_FOUND")
    NO_STATE_FOUND = ErrorCode(10002, "NO_STATE_FOUND")
