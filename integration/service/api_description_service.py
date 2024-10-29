from geoservice.data.db_helper import execute_query
from geoservice.data.DBResult import DBResult
from integration.model.entity.ApiDescription import ApiDescription
import json
from common.cache import cached

QUERIES = {
    "query_api_descriptions": """
        select  
            ID, API_NAME, API_URL, IS_ENABLED, IS_MOCKED, IS_LOG_ENABLED,
            BYPASS_AUTH, API_DESCRIPTION, MOCKED_RESPONSE
        from GIS.TBL_API_DESCRIPTION
    """
}

@cached()
def get_all_api_descriptions() -> dict[ApiDescription]:

    def run(db_result: DBResult):
        api_desc_map = {}
        results = db_result.results
        for result in results:
            id = int(result['ID'])
            api_name = str(result['API_NAME'])
            api_url = str(result['API_URL'])
            is_enabled = str(result['IS_ENABLED']) == "1"
            is_mocked = str(result['IS_MOCKED']) == "1"
            is_log_enabled = str(result['IS_LOG_ENABLED']) == "1"
            bypass_auth = str(result['BYPASS_AUTH']) == "1"
            api_description = str(result['API_DESCRIPTION'])
            mocked_response = None
            if result['MOCKED_RESPONSE']:
                mocked_response = json.loads(str(result['MOCKED_RESPONSE']))
                

            api_desc = ApiDescription(id=id, api_name=api_name, api_url=api_url,
                                     is_enabled=is_enabled, is_mocked=is_mocked,
                                     is_log_enabled=is_log_enabled, bypass_auth=bypass_auth,
                                     api_description=api_description, mocked_response=mocked_response)
            api_desc_map[api_url] = api_desc
        return api_desc_map

    return execute_query(QUERIES['query_api_descriptions'], run)


def find_api_description(key: str) -> ApiDescription:
    api_desc_map = get_all_api_descriptions()
    try:
        return api_desc_map[key]
    except KeyError:
        return None
