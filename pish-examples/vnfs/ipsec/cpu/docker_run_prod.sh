#!/usr/bin/env bash

docker stop ipsec-cpu
docker rm ipsec-cpu 

docker run --rm -ti \
    -p 80:80 \
    --name ipsec-cpu \
    ipsec-cpu
