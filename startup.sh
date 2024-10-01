
export oracle_version="12"
export db_username="GIS"
export db_password="123"
export db_ip="192.168.24.52"
export db_port="1521"
export db_service="gisdb"

# export oracle_version="11"
# export db_username="test_user"
# export db_password="123"
# export db_ip="192.168.24.52"
# export db_port="1521"
# export db_service="oracle11db"

export app_port=8000
export app_host="0.0.0.0"

fastapi dev --reload --host $app_host --port $app_port app.py