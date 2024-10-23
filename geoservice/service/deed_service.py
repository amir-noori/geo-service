
from geoservice.data.db_helper import execute_query
from geoservice.data.DBResult import DBResult
from  geoservice.common.constants import *
from geoservice.model.entity.Parcel import *
from geoservice.util.lang_util import gibberish_to_fa
from log.logger import logger

log = logger()

QUERIES = {
    "query_deeds1_by_volume": """
        SELECT 
            a52 as STATE, 
            a54 as ADDRESS, 
            a19 as AREA,
            a11 as SUBSIDIARY_PLATE_NUMBER,
            a12 as PARTITIONED,
            a13 as SEGMENT
        from gis.DEEDS1 d1
        WHERE 
            a28 is null and
            a0 = '{volume_code}' and 
            a1 = '{volume_number}' and 
            a2 = '{page_number}'
    """,

    "query_deeds9_by_volume": """
        SELECT 
            i71 as LEGAL_AREA, 
            i64 as SEGMENT, 
            i75 as SUBSIDIARY_PLATE_NUMBER
        from gis.DEEDS9 d9
        WHERE 
            i89 is null and
            i0 = '{volume_code}' and 
            i1 = '{volume_number}' and 
            i2 = '{page_number}' and
            i52D not in ('cldk','cldkSfhSfkhdShpnhed') and
            i75 is not null and
            i76 is not null and
            i64 like 'A%G%'
    """
}


def find_deed(deed: Deed):

    def run(db_result: DBResult):
        results = db_result.results

        for result in results:
            state = None
            if result['STATE']:
                state = gibberish_to_fa(str(result['STATE']))
            address = str(result['ADDRESS'])
            area = str(result['AREA'])
            subsidiary_plate_number = str(result['SUBSIDIARY_PLATE_NUMBER'])
            partitioned = str(result['PARTITIONED'])
            segment = str(result['SEGMENT'])
            result = Deed(state=state, address_text=address, volume_code=deed.volume_code,
                        volume_number=deed.volume_number, page_number=deed.page_number,
                        legal_area=area, subsidiary_plate_number=subsidiary_plate_number,
                        partitioned=partitioned, segment=segment)
            log.debug(f"retrieved deed: {result}")
            return deed

        return None

    query_deed = QUERIES['query_deeds1_by_volume'].format(
        volume_code=deed.volume_code,
        volume_number=deed.volume_number,
        page_number=deed.page_number
    )

    deed = execute_query(query_deed, run)
    parts = find_deed_parts(deed)
    deed.deed_parts = parts

    return deed


def find_deed_parts(deed: Deed):

    def run(db_result: DBResult):
        results = db_result.results

        deed_parts = []
        for result in results:
            area = str(result['LEGAL_AREA'])
            subsidiary_plate_number = str(result['SUBSIDIARY_PLATE_NUMBER'])
            segment = str(result['SEGMENT'])
            part = DeedPart(legal_area=area, segment=segment,
                            subsidiary_plate_number=subsidiary_plate_number)
            deed_parts.append(part)

        return deed_parts

    deed_parts = []
    if deed:
        query_deed_parts = QUERIES['query_deeds9_by_volume'].format(
            volume_code=deed.volume_code,
            volume_number=deed.volume_number,
            page_number=deed.page_number
        )
        
        deed_parts = execute_query(query_deed_parts, run)
    
    return deed_parts
