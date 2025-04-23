import base64
import binascii

from geoservice.exception.common import CustomException, ErrorCodes


def stringToBase64(s):
    return base64.b64encode(s.encode('utf-8'))


def base64ToString(b):
    return base64.b64decode(b).decode('utf-8')

def base64Binary(b):
    return base64.b64decode(b)

def parse_to_int(text, default=0):
    try:
        return int(text)
    except (ValueError, TypeError):
        return default

def parse_to_float(text, default=0.0):
    try:
        return float(text)
    except (ValueError, TypeError):
        return default