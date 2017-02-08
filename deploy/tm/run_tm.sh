#!/bin/bash

conf="$1/conf.py"
uploads="$1/uploads"
name=$(echo "$1" | sed "s/\//-/")
name="${name%/}"

if [ ! -r "$conf" ]; then
    echo "please specify a conf file"
    exit 1
fi

edconf=$(mktemp /tmp/output.XXXXXXXXXX) || { echo "failed to create temp file"; exit 1; }
sed 's/^UPLOAD_DIR\s*=.*/UPLOAD_DIR = "\/uploads"/' "$conf" | sed "1i BASE_URL = 'http://$(hostname)/tm/$1/'" > "$edconf"

mkdir -p "$uploads"
if docker ps -a  | grep -q "$name"; then
    echo "Killing old instance..." $(docker rm -f "$name")
fi
did=$(docker run -l scythe=tm --name "$name" -d --network=scythe -v "$(pwd)/$uploads":/uploads -v "$edconf":/app/conf.py:ro scythe/tm)
echo "Running '$name' with conf '$conf' and uploads in '$uploads' (docker id '$did')..."
