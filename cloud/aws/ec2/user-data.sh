#!/bin/bash
apt update -y
apt install docker.io -y
docker run -d -p 80:8000 orcaopta-api:latest
