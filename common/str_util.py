import base64
import binascii

from geoservice.exception.common import CustomException, ErrorCodes


def stringToBase64(s):
    return base64.b64encode(s.encode('utf-8'))


def base64ToString(b):
    return base64.b64decode(b).decode('utf-8')

def base64Binary(b):
    return base64.b64decode(b)