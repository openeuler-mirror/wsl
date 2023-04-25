#!/bin/bash

set -eE
trap cleanup EXIT

function cleanup() {
    [ ! -z "$(docker buildx ls | grep buildx-$release-$arch)" ] && docker buildx rm buildx-$release-$arch
    sleep 10
    docker ps -aq --filter ancestor=openeuler-wsl:$release-$arch | xargs -r docker stop 
    docker rmi openeuler-wsl:$release-$arch
}

[ -d $WORKSPACE/outdir/ ] && rm -rvf $WORKSPACE/outdir/* || mkdir -pv $WORKSPACE/outdir
docker info
docker buildx ls
docker ps -a
[ -z "$(docker buildx ls | grep buildx-$release-$arch)" ] && docker buildx create --bootstrap --use --name buildx-$release-$arch || docker buildx use buildx-$release-$arch
# build rootfs docker image
docker buildx build --build-arg REL_TAG=$release --platform linux/$arch --tag openeuler-wsl:$release-$arch --load --cache-from=type=local,src=/var/cache/buildx/$release-$arch --cache-to=type=local,dest=/var/cache/buildx/$release-$arch \
    $WORKSPACE/docker/
docker run --rm --platform linux/$arch openeuler-wsl:$release-$arch > $WORKSPACE/outdir/$release-$arch.tar.gz
ls -lh $WORKSPACE/outdir/