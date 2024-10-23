 
class Channel:

    id: int
    auth_key: str
    channel_id: str
    channel_name: bool
    description: bool

    def __init__(self, id: int = None, auth_key: str = None, channel_id: int = None,
                 channel_name: str = None, description: str = None) -> None:
        self.id = id
        self.auth_key = auth_key
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.description = description
