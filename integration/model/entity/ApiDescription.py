

class ApiDescription:

    id: int
    api_name: str
    api_url: str
    is_enabled: bool
    is_log_enabled: bool
    is_mocked: bool
    bypass_auth: bool
    api_description: str
    mocked_response: str

    def __init__(self, id: int = None, api_name: str = None, api_url: str = None,
                 is_enabled: bool = True, is_mocked: bool = False, bypass_auth: bool = False,
                 is_log_enabled: bool = True, api_description: str = None, mocked_response: str = None) -> None:
        self.id = id
        self.api_name = api_name
        self.api_url = api_url
        self.is_enabled = is_enabled
        self.is_log_enabled = is_log_enabled
        self.is_mocked = is_mocked
        self.bypass_auth = bypass_auth
        self.api_description = api_description
        self.mocked_response = mocked_response
