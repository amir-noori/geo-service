

## commands

to run the app in development mode:

    fastapi dev --reload --host 0.0.0.0 --port 8000 app.py

or edit the `startup.sh` and simply run:

    ./startup.sh


## docker commands:

    # build base docker image
    make buildbase

    # build app docker image
    make buildapp

    # run and connect immediately
    make runapp

    # to copy files to container
    docker cp HOST_PATH CONTAINER_ID:CONTAINER_PATH

    # to save images:
    docker save -o /vagrant/geoubuntu.tar geoubuntu
    docker save -o /vagrant/geoubuntu_app.tar geoubuntu_app



## db grants

    CREATE USER test_user IDENTIFIED BY 123;

    GRANT CONNECT TO test_user;
    GRANT CREATE SESSION TO test_user;
    
    grant all on gis.TBL_CHANNEL to test_user;
    grant all on gis.TBL_API_DESCRIPTION to test_user;
    grant all on gis.TBL_LAND_CLAIM to test_user;
    grant all on gis.TBL_MESSAGE_LOG to test_user;
    
    grant select on gis.TBL_CHANNEL_SEQ to test_user;
    grant select on gis.TBL_API_DESCRIPTION_SEQ to test_user;
    grant select on gis.TBL_LAND_CLAIM_SEQ to test_user;
    grant select on gis.TBL_MESSAGE_LOG_SEQ to test_user;

