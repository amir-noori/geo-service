from geoservice.data.db_helper import execute_insert
from integration.model.entity.DbMessageLog import DbMessageLog

QUERIES = {
    "insert_db_message_log": """
        insert into TBL_MESSAGE_LOG
        (ID, TRACKING_ID, SERVICE_KEY, SOURCE_IP, METHOD, DESTINATION_IP, REQUEST_URL, CHANNEL_ID,
        REQUEST_TIMESTAMP,
        RESPONSE_TIMESTAMP, REQUEST_MESSAGE, RESPONSE_MESSAGE, DOWNSTREAM_REQUEST, DOWNSTREAM_RESPONSE, 
        EXCEPTION)
        values (TBL_MESSAGE_LOG_SEQ.NEXTVAL, :TRACKING_ID, :SERVICE_KEY, :SOURCE_IP, :METHOD, :DESTINATION_IP, :REQUEST_URL,
                :CHANNEL_ID,
                :REQUEST_TIMESTAMP, :RESPONSE_TIMESTAMP, :REQUEST_MESSAGE, :RESPONSE_MESSAGE, 
                :DOWNSTREAM_REQUEST, :DOWNSTREAM_RESPONSE, :EXCEPTION)
    """
}


def save_db_message_log(message_log: DbMessageLog) -> None:

    params = [message_log.tracking_id, message_log.service_key, message_log.source_ip,
              message_log.method, message_log.destination_ip, message_log.request_url,
              message_log.channel_id,
              message_log.request_time, message_log.response_time, message_log.request,
              message_log.response, None, None, message_log.exception]

    execute_insert(QUERIES['insert_db_message_log'], params)
