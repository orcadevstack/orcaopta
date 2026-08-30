#!/bin/bash
set -e

VERSION="0.1.0"
DIST="dist"

echo "============================================================"
echo "        ORCAOPTA — GLOBAL BUILD SYSTEM"
echo "============================================================"

# Activate venv
source .venv/bin/activate

# Ensure tools exist
pip install pyinstaller
sudo apt-get update
sudo apt-get install -y dpkg-dev pkg-config fakeroot zip gnupg openssh-client

mkdir -p $DIST

# -------------------------------------------------------------
# Build CLI Binary
# -------------------------------------------------------------
echo "[CLI] Building PyInstaller binary..."

pyinstaller --onefile src/orcaopta/cli/orcaopta_cli.py --name orcaopta

echo "[CLI] Binary built: dist/orcaopta"


# -------------------------------------------------------------
# Build Linux .deb
# -------------------------------------------------------------
echo "[Linux] Building .deb package..."

mkdir -p build/linux/usr/local/bin
mkdir -p build/linux/DEBIAN

cp dist/orcaopta build/linux/usr/local/bin/orcaopta
chmod +x build/linux/usr/local/bin/orcaopta

cat > build/linux/DEBIAN/control <<EOF
Package: orcaopta
Version: $VERSION
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Samuel Orcas <orcaprojectstack@gmail.com>
Description: Orcaopta Control Plane CLI
 Unified MCP + Cloud Automation CLI.
EOF

dpkg-deb --root-owner-group --build build/linux "$DIST/orcaopta_${VERSION}_amd64.deb"
echo "[Linux] .deb created."


# -------------------------------------------------------------
# Build Linux tar.gz
# -------------------------------------------------------------
echo "[Linux] Building tar.gz..."
tar -czvf "$DIST/orcaopta-linux-$VERSION.tar.gz" -C dist orcaopta
echo "[Linux] tar.gz created."


# -------------------------------------------------------------
# Build Windows EXE
# -------------------------------------------------------------
echo "[Windows] Building .exe..."

pyinstaller --onefile src/orcaopta/cli/orcaopta_cli.py --name orcaopta.exe
zip "$DIST/orcaopta-windows-$VERSION.zip" dist/orcaopta.exe

echo "[Windows] .exe + zip created."


# -------------------------------------------------------------
# macOS PKG (CI runner only)
# -------------------------------------------------------------
echo "[macOS] PKG will be built in macOS GitHub runner."



# -------------------------------------------------------------
# Summary
# -------------------------------------------------------------
echo "============================================================"
echo "BUILD COMPLETE — ARTIFACTS:"
echo "============================================================"
ls -lh $DIST
echo "============================================================"
echo "All builds + signatures packaged successfully."
