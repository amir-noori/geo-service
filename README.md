

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


## Service:

### parcel service output:

    {

        "commonMetadata": {
            "state": "", // shamim.vahedsdo
            "stateCode": "", // mapping
            "cms": "801", // centroid.cms/shape.cms
            "section": "1", // centroid.txt_label/shape.label1 
            "district": "1", // centroid.txt_label/shape.label1
            "mainPlateNumber": "1" // centroid.txt_label/shape.label1
        },
        
        "ground": {
            "parcel": {
                "geom": "", // centroid.poly/shape.poly
                "type": "polygon"
                "crs": ""
            },

            "metaData": {
                "subsidiaryPlateNumber": "1" // deeds1.a11
                "partitioned": "1", // deeds1.a12
                "segment": "1", // deeds1.a13
                "area": "125.2" // deed9.i71
            },
        }

        "apartements": [
            {
                "metaData": {
                    "subsidiaryPlateNumber": "1" // deeds9.i76
                    "partitioned": "1", // arse.subsidiaryPlateNumber
                    "segment": "1", // deeds9.i64
                    "area": "125.2" // deeds9.i71
                }
            }
        ]

    }