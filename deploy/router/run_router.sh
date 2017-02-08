#!/bin/bash

docker rm -f router
docker rm -f portainer

mkdir -p "$(pwd)/var/portainer"

docker run --name portainer -v "$(pwd)/var/portainer":/data -p 9000:9000 -v /var/run/docker.sock:/var/run/docker.sock -d portainer/portainer -H unix:///var/run/docker.sock
docker run --name router --network scythe -p 80:80 -v "$(pwd)/etc/nginx.conf":/etc/nginx/nginx.conf:ro -v $(pwd)/html:/usr/share/nginx/html:ro -d nginx:alpine
date > html/now.txt
curl http://$(hostname)/now.txt
