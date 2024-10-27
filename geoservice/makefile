
cleanup:
	docker ps -a -q | xargs -r docker rm
	docker image ls -f"dangling=true" -q | xargs -r docker image rm

buildbase:
	docker build . -t geoubuntu -f ./geoservice/docker/BUILD_BASE.Dockerfile --progress=plain

buildapp:
	docker build . -t geoubuntu_app -f ./geoservice/docker/BUILD_APP.Dockerfile --build-arg mode=dev --progress=plain

buildapprun:
	docker build . -t geoubuntu_app -f ./geoservice/docker/BUILD_APP.Dockerfile --build-arg mode=run --progress=plain

build: buildbase buildapp

runapp:
	docker run -i -p 9001:9001 --env-file ./geoservice/docker/env.app.list -t geoubuntu_app:latest /bin/bash

rundispatcher:
	docker run -i -p 9000:9000 --env-file ./geoservice/docker/env.dispatcher.list -t geoubuntu_app:latest  /bin/bash


dockercp:
	for i in `docker ps | grep geoubuntu_app | awk '{print $1}'`; do echo "cp to $i"; docker cp . $i:/opt/app; done
