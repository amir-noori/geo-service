

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

