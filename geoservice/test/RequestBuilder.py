from json import dumps
class ParcelRequestBuilder:
    @staticmethod
    def build_headers(auth_token):
        return {
            "Authorization": f"Basic {auth_token}"
        }
    
    @staticmethod
    def build_header_params(national_id, first_name, last_name):
        return {
            "nationalId": national_id,
            "firstName": first_name,
            "lastName": last_name
        }
        
    @staticmethod
    def build_find_parcel_info_by_centroid(longitude, latitude, srid="4326", distance=200):
        return {
            "longtitude": longitude,
            "latitude": latitude,
            "srid": srid,
            "distance": distance
        }
    
    @staticmethod
    def build_wrong_find_parcel_info_by_centroid(longitude, latitude, srid="4326", distance=200):
        return {
            "longtitude": longitude,
            "latitud": latitude,
            "srid": srid,
            "distance": distance
        }
    
    @staticmethod
    def build_find_parcel_info_post_content(national_id, first_name, last_name, longitude, latitude, lang="en_US", srid="4326", distance=200):
        return {
            "header": {
                "lang": lang,
                "params": ParcelRequestBuilder.build_header_params(national_id, first_name, last_name)
            },
            "body": ParcelRequestBuilder.build_find_parcel_info_by_centroid(longitude, latitude, srid, distance)
        }
    
    @staticmethod
    def build_wrong_find_parcel_info_post_content(national_id, first_name, last_name, longitude, latitude,lang="en_US", srid="4326", distance=200):
        return {
            "header": {
                "lang": lang,
                "params": ParcelRequestBuilder.build_header_params(national_id, first_name, last_name)
            },
            "body": ParcelRequestBuilder.build_wrong_find_parcel_info_by_centroid(longitude, latitude, srid, distance)
        }