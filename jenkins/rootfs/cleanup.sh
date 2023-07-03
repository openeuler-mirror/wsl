#!/bin/bash

docker info
docker images
docker ps -a
docker buildx ls
docker buildx du
docker container prune -f
docker image prune -f
