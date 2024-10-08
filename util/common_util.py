from common.states import states


def get_state_code_by_name(name): 
    for state_code, state_name in states.items():
        if name == state_name:
            return state_code
    
    return None

