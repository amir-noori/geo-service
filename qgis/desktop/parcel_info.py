import requests
import json


service_ip = "192.168.1.63"
service_port = "8001"

base_url = f"http://{service_ip}:{service_port}/"
url_path = f"parcels/find_parcel_info_by_centroid/?"

def call_parcel_info_service(latitude, longtitude):
    url_params = f"latitude={latitude}&longtitude={longtitude}"
    url = f"{base_url}{url_path}{url_params}"
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        response_content = json.loads(response.content.decode('utf-8'))
        print(response_content)
    else:
        print(f"error code: {response.status_code}")
        print("error", response.content)


call_parcel_info_service(33.1194320,46.1747897)