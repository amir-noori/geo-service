
cleanup:
	docker ps -a -q | xargs -r docker rm
	docker image ls -f"dangling=true" -q | xargs -r docker image rm

buildbase:
	docker build . -t geoubuntu -f ./docker/BUILD_BASE.Dockerfile --progress=plain

buildapp:
	docker build . -t geoubuntu_app -f ./docker/BUILD_APP.Dockerfile --build-arg mode=dev --progress=plain

build: buildbase buildapp

runapp:
	docker run -i -p 8000:8000 -t geoubuntu_app:latest /bin/bash