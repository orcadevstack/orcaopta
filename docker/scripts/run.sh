#!/bin/bash
echo "Running orcaopta-api container..."
docker run -p 8000:8000 --name orcaopta-api orcaopta-api
