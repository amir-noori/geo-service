
class ResponseCode:

    def __init__(self, code, message_key) -> None:
        self.code = code
        self.message_key = message_key


class ResponseCodes:

    SUCCESS = ResponseCode(0, "SUCCESS")


def handle_response(body):
    return {
        "status": ResponseCodes.SUCCESS.code,
        "body": body
    }
