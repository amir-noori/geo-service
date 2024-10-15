
cleanup:
	docker ps -a -q | xargs -r docker rm
	docker image ls -f"dangling=true" -q | xargs -r docker image rm

buildbase:
	docker build . -t geoubuntu -f ./docker/BUILD_BASE.Dockerfile --progress=plain

buildapp:
	docker build . -t geoubuntu_app -f ./docker/BUILD_APP.Dockerfile --build-arg mode=dev --progress=plain

buildapprun:
	docker build . -t geoubuntu_app -f ./docker/BUILD_APP.Dockerfile --build-arg mode=run --progress=plain

build: buildbase buildapp

runapp:
	docker run -i -p 8001:8001 --env-file ./docker/env.app.list -t geoubuntu_app:latest /bin/bash

rundispatcher:
	docker run -i -p 8000:8000 --env-file ./docker/env.dispatcher.list -t geoubuntu_app:latest  /bin/bash