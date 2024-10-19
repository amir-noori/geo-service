import json


def serialize(obj):
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    else:
        return obj.__str__
    
    
def toJSON(object):
    return json.dumps(
        object,
        default=serialize, 
        sort_keys=True,
        indent=4)    
