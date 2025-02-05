from geoservice.data.db_helper import execute_query
from geoservice.data.DBResult import DBResult
from integration.model.entity.Channel import Channel
from common.cache import cached


QUERIES = {
    "query_channels": """
        select  
            ID, AUTH_KEY, CHANNEL_ID, CHANNEL_NAME, DESCRIPTION
        from TBL_CHANNEL
    """
}


@cached()
def get_all_channels() -> dict[Channel]:

    def run(db_result: DBResult):
        channel_map = {}
        results = db_result.results
        for result in results:
            id = int(result['ID'])
            auth_key = str(result['AUTH_KEY'])
            channel_id = int(result['CHANNEL_ID'])
            channel_name = str(result['CHANNEL_NAME'])
            description = str(result['DESCRIPTION'])

            channel = Channel(id=id, auth_key=auth_key, channel_id=channel_id,
                              channel_name=channel_name, description=description)
            channel_map[channel_id] = channel
        return channel_map

    return execute_query(QUERIES['query_channels'], run)


def find_channel(key: int) -> Channel:
    channel_map = get_all_channels()
    
    try:
        return channel_map[key]
    except KeyError:
        return None
