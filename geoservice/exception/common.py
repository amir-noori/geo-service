from fastapi import status


class ErrorCode:

    def __init__(self, code, message_key) -> None:
        self.code = code
        self.messsage_key = message_key

    def __eq__(self, value: object) -> bool:
        return self.code == value.code


class CustomException(Exception):

    def __init__(self, error_code: ErrorCode, error_message="") -> None:
        super().__init__()
        self.error_message = error_message
        self.error_code = error_code


class ErrorCodes:
    
    SERVER_ERROR = ErrorCode(500, "SERVER_ERROR")
    
    NO_PARCEL_FOUND = ErrorCode(10000, "NO_PARCEL_FOUND")
    MULTIPLE_PARCEL_FOUND = ErrorCode(10001, "MULTIPLE_PARCEL_FOUND")
    NO_STATE_FOUND = ErrorCode(10002, "NO_STATE_FOUND")
    
    NO_UNIT_FOUND = ErrorCode(20002, "NO_UNIT_FOUND")

    VALIDATION_NATIONAL_ID_REQUIRED = ErrorCode(3000, "VALIDATION_NATIONAL_ID_REQUIRED")
    VALIDATION_FIRST_NAME_REQUIRED = ErrorCode(3001, "VALIDATION_FIRST_NAME_REQUIRED")
    VALIDATION_LAST_NAME_REQUIRED = ErrorCode(3002, "VALIDATION_LAST_NAME_REQUIRED")
    VALIDATION_EMPTY_REQUEST_FIELDS = ErrorCode(3003, "VALIDATION_EMPTY_REQUEST_FIELDS")
    
    VALIDATION_NO_STATE_CODE_IN_HEADER = ErrorCode(4000, "VALIDATION_NO_STATE_CODE_IN_HEADER")
    
