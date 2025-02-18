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
    """
        Error Codes and related message keys
    """

    """
        Basic Errors
    """

    SERVER_ERROR = ErrorCode(500, "SERVER_ERROR")
    SERVER_UNAVAILABLE = ErrorCode(503, "SERVER_UNAVAILABLE")

    """
        Basic Geo Errors
    """

    NO_PARCEL_FOUND = ErrorCode(10000, "NO_PARCEL_FOUND")
    MULTIPLE_PARCEL_FOUND = ErrorCode(10001, "MULTIPLE_PARCEL_FOUND")
    NO_STATE_FOUND = ErrorCode(10002, "NO_STATE_FOUND")
    MULTIPLE_FEATURE_FOUND = ErrorCode(10003, "MULTIPLE_FEATURE_FOUND")
    NO_FEATURE_FOUND = ErrorCode(10004, "NO_FEATURE_FOUND")
    INVALID_FEATURE_FOUND = ErrorCode(10004, "INVALID_FEATURE_FOUND")
    INVALID_POLYGON_FOUND = ErrorCode(10005, "INVALID_POLYGON_FOUND")
    NO_GEOMETRY_FOUND = ErrorCode(10006, "NO_GEOMETRY_FOUND")
    NO_CONTAINING_CMS_FOUND = ErrorCode(10007, "NO_CONTAINING_CMS_FOUND")

    NO_UNIT_FOUND = ErrorCode(20002, "NO_UNIT_FOUND")

    """
        Request Validations
    """

    VALIDATION_NATIONAL_ID_REQUIRED = ErrorCode(30000, "VALIDATION_NATIONAL_ID_REQUIRED")
    VALIDATION_FIRST_NAME_REQUIRED = ErrorCode(30001, "VALIDATION_FIRST_NAME_REQUIRED")
    VALIDATION_LAST_NAME_REQUIRED = ErrorCode(30002, "VALIDATION_LAST_NAME_REQUIRED")
    VALIDATION_EMPTY_REQUEST_FIELDS = ErrorCode(30003, "VALIDATION_EMPTY_REQUEST_FIELDS")
    VALIDATION_INVALID_REQUEST_FIELDS = ErrorCode(30004, "VALIDATION_INVALID_REQUEST_FIELDS")

    VALIDATION_NO_STATE_CODE_IN_HEADER = ErrorCode(40000, "VALIDATION_NO_STATE_CODE_IN_HEADER")

    # claim validations
    VALIDATION_CLAIM_TRACE_ID_EXISTS = ErrorCode(40100, "VALIDATION_CLAIM_TRACE_ID_EXISTS")
    NO_CLAIM_FOUND = ErrorCode(40101, "NO_CLAIM_FOUND")
    CLAIM_POLYGON_NOT_FOUND_IN_STATES_CMS = ErrorCode(40102, "CLAIM_POLYGON_NOT_FOUND_IN_STATES_CMS")
    CLAIM_POLYGON_HAS_OVERLAP_WITH_DOCUMENTED_PARCEL = ErrorCode(40103, "CLAIM_POLYGON_HAS_OVERLAP_WITH_DOCUMENTED_PARCEL")