#!/bin/bash

source ./set_states_env.sh

export service_provider_port=8000

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

export PYTHONPATH=/opt/app:$PYTHONPATH
export oracle_client_home="/opt/app/oracle"
export LOG_LEVEL="DEBUG"
export locale="en_US"
export app_port=8000
export app_host="0.0.0.0"
export app_mode="dispatcher"

source bin/activate
fastapi dev --host $app_host --port $app_port app.py


