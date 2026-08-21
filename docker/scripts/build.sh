#!/bin/bash
echo "Building orcaopta Docker image..."
docker build -t orcaopta-api -f ../docker/Dockerfile ..
echo "Build complete."
