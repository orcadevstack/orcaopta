#!/usr/bin/env bash
set -e

VERSION="v0.1.0"
REPO="orcadevstack/orcaopta"

echo "Installing Orcaopta $VERSION..."

# Detect OS
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

echo "Detected OS: $OS"
echo "Detected Arch: $ARCH"

# Download release
URL="https://github.com/$REPO/releases/download/$VERSION/orcaopta-$VERSION.tar.gz"

echo "Downloading $URL..."
curl -sSL "$URL" -o /tmp/orcaopta.tar.gz

echo "Extracting..."
mkdir -p /opt/orcaopta
tar -xzf /tmp/orcaopta.tar.gz -C /opt/orcaopta

# Create symlink
ln -sf /opt/orcaopta/orcaopta /usr/local/bin/orcaopta

echo " Orcaopta installed!"
echo "Run: orcaopta start"


python3 /opt/orcaopta/src/orcaopta/main.py "$@"
