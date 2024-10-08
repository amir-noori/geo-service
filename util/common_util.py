from common.states import states
from common.states import state_to_db_mapping


def get_state_code_by_name(name):
    for state_code, state_name in states.items():
        if name == state_name:
            return state_code

    return None


def get_state_ip_by_code(code):
    for state_code, ip in state_to_db_mapping.items():
        if state_code == code:
            return ip

    return None
