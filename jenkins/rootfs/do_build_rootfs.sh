#!/bin/bash

set -eE
trap cleanup EXIT

function cleanup() {
    [ ! -z "$(docker buildx ls | grep buildx-$release-$arch)" ] && docker buildx rm buildx-$release-$arch
    sleep 10
    docker ps -aq --filter ancestor=openeuler-wsl:$release-$arch | xargs -r docker stop
    docker rmi openeuler-wsl:$release-$arch
}

function print_args() {
    echo "server: $server"
    echo "baseuri: $baseuri"
    echo "WORKSPACE: $WORKSPACE"
    echo "release: $release"
    echo "arch: $arch"
    echo "branch: $branch"
    echo "date: $date"
}

[ -d $WORKSPACE/outdir/ ] && rm -rvf $WORKSPACE/outdir/* || mkdir -pv $WORKSPACE/outdir
docker info
docker buildx ls
docker ps -a
print_args
BUILD_TYPE="release"
touch $WORKSPACE/docker/openEuler-daily.repo
[ -z "$(docker buildx ls | grep buildx-$release-$arch)" ] && docker buildx create --bootstrap --use --name \
        buildx-$release-$arch || docker buildx use buildx-$release-$arch
# build rootfs docker image
if [ ! -z "$server" ] && [ ! -z "$baseuri" ] && [ ! -z "$branch" ] && [ ! -z "$date" ]; then
    REPO_BASE="$server"/"$baseuri"/"$branch"/"$date"
    sed "s|http://repo|${REPO_BASE}|g" $WORKSPACE/docker/openEuler.repo > $WORKSPACE/docker/openEuler-daily.repo
    BUILD_TYPE="daily"
fi
docker buildx build --build-arg BUILD_TYPE=$BUILD_TYPE --build-arg REL_TAG=$release --platform linux/$arch --tag \
        openeuler-wsl:$release-$arch --load --no-cache  --progress=plain $WORKSPACE/docker/
docker run --rm --platform linux/$arch openeuler-wsl:$release-$arch >$WORKSPACE/outdir/$release-$arch.tar.gz
ls -lh $WORKSPACE/outdir/
