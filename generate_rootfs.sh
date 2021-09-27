#!/bin/bash
if [[ "$(whoami)" != "root" ]]; then
    echo please run in root!
    exit 1
fi
cd docker
docker build . -t openeuler-wsl
docker run openeuler-wsl echo hello
echo exporting... this may take 2 minuts, please wait...
eval docker export $(docker ps -ql) | gzip > ../install.tar.gz