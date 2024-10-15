from common.lang import *


def fa_to_gibberish(text):
    for key, value in gibberish_to_fa_mapping.items():
        text = text.replace(key, value)
    return text

def gibberish_to_fa(text):
    if text:
        for key, value in gibberish_to_fa_mapping.items():
            text = text.replace(key, value)
    return text
    
