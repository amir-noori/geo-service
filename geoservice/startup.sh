#!/bin/bash

# source ./set_states_env.sh

export service_provider_port=8001

# export oracle_version="11"
# export db_username="GIS"
# export db_password="123"
# export db_ip="192.168.24.52"
# export db_port="1521"
# export db_service="gisdb"

# export oracle_version="11"
# export db_username="test_user"
# export db_password="123"
# export db_ip="192.168.24.52"
# export db_port="1521"
# export db_service="oracle11db"

PWD=`pwd`

export PYTHONPATH=$PWD:$PYTHONPATH
export oracle_client_home="/opt/oracle"

export app_port="${app_port:-8001}" 
export dispatch_port="${dispatch_port:-8000}"
export app_host="0.0.0.0"
# app_mode must be set (values: "dispatcher" or "app" , default: "app")
export app_mode="${app_mode:-app}" 

# app_mode must be set (values: "dev" or "run" , default: "dev")
export app_level="${app_level:-dev}" 
export LOG_LEVEL="${LOG_LEVEL:-INFO}"
export LOG_DIR="${LOG_DIR:-/opt/log}"

export default_locale="${default_locale:-en_US}"
export LOG_FORMAT="${LOG_FORMAT}"

export enable_db_log="${enable_db_log:-true}" 
export enable_api_mock="${enable_api_mock:-false}"

source bin/activate

if [ $app_mode = "dispatcher" ]; then
   fastapi $app_level --host $app_host --port $dispatch_port $PWD/geoservice/app.py
else
  fastapi $app_level --host $app_host --port $app_port $PWD/geoservice/app.py
fi




