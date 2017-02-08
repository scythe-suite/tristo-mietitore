#!/bin/bash

docker build --build-arg userid="$(id -u)" -t scythe/tm .
