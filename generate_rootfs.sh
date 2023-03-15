#!/bin/bash

ARGS=$1
if [ -z $ARGS ]; then
    ARGS="latest"
fi

echo exporting... this may take 2 minuts, please wait...
docker run --rm openeuler-wsl:$ARGS >./install.tar.gz
