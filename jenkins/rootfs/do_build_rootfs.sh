#!/bin/bash

set -eE
set -o pipefail
trap cleanup EXIT

function cleanup() {
    set +eE
    [ ! -z "$(docker buildx ls | grep buildx-$release-$arch)" ] && docker buildx rm buildx-$release-$arch
    return 0
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
else
    REPO_BASE="https://repo.openeuler.org"
    ver=$(curl -s $REPO_BASE |grep -Eo "openEuler-$release-?(LTS)?-?(SP[1-9]+)?"|tail -n 1)
    REPO_BASE="$REPO_BASE/$ver"
fi

if [ $arch == "x86_64" ];then
    wslarch=amd64
elif [ $arch == "aarch64" ];then
    wslarch=arm64
fi
curl -OL --fail $REPO_BASE/docker_img/$arch/openEuler-docker.$arch.tar.xz
image_name=$(docker load -i openEuler-docker.$arch.tar.xz| grep -Eo "openeuler-$release-?(lts)?-?(sp[1-9]+)?"| tail -n 1)
docker export $(docker create --rm --platform linux/$wslarch $image_name:latest) --output="$WORKSPACE/docker/$image_name.tar"
docker buildx build --build-arg BUILD_TYPE=$BUILD_TYPE --build-arg PLATFORM=$wslarch --platform linux/$wslarch --tag \
        openeuler-wsl:$release --load --no-cache --build-arg IMAGE_NAME=$image_name --progress=plain $WORKSPACE/docker/
docker run --rm --platform linux/$wslarch openeuler-wsl:$release >$WORKSPACE/outdir/$release-$arch.tar.gz
ls -lh $WORKSPACE/outdir/
