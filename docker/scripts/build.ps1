Write-Host "Building orcaopta Docker image..."
docker build -t orcaopta-api -f ../docker/Dockerfile ..
Write-Host "Build complete."
