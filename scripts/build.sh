#!/bin/bash
set -e

VERSION="0.1.0"
DIST_DIR="dist"

echo "============================================================"
echo "        ORCAOPTA — CROSS PLATFORM BUILD SYSTEM"
echo "============================================================"

mkdir -p $DIST_DIR

# -------------------------------------------------------------
# Build Linux .deb
# -------------------------------------------------------------
echo "[Linux] Building .deb package..."

mkdir -p build/linux/usr/local/bin
mkdir -p build/linux/DEBIAN

# Copy CLI binary from venv
cp .venv/bin/orcaopta build/linux/usr/local/bin/
chmod +x build/linux/usr/local/bin/orcaopta

cat > build/linux/DEBIAN/control <<EOF
Package: orcaopta
Version: $VERSION
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Samuel Orcas <orcaprojectstack@gmail.com>
Description: Orcaopta Control Plane CLI
 Unified MCP + ML + RL + Cloud Automation CLI.
EOF

dpkg-deb --build build/linux "$DIST_DIR/orcaopta_${VERSION}_amd64.deb"
echo "[Linux] .deb created: $DIST_DIR/orcaopta_${VERSION}_amd64.deb"


# -------------------------------------------------------------
# Build Linux tar.gz
# -------------------------------------------------------------
echo "[Linux] Building tar.gz..."

mkdir -p build/linux-tar
cp .venv/bin/orcaopta build/linux-tar/
chmod +x build/linux-tar/orcaopta

tar -czvf "$DIST_DIR/orcaopta-linux-$VERSION.tar.gz" -C build/linux-tar orcaopta
echo "[Linux] tar.gz created."


# -------------------------------------------------------------
# Build Windows .exe
# -------------------------------------------------------------
echo "[Windows] Building .exe..."

pyinstaller --onefile src/orcaopta/cli/orcaopta_cli.py --name orcaopta
cp dist/orcaopta.exe "$DIST_DIR/orcaopta-$VERSION.exe"

# Windows zip
zip "$DIST_DIR/orcaopta-windows-$VERSION.zip" dist/orcaopta.exe
echo "[Windows] .exe + zip created."


# -------------------------------------------------------------
# Build macOS .pkg
# -------------------------------------------------------------
echo "[macOS] Building .pkg..."

mkdir -p build/macos/usr/local/bin
cp .venv/bin/orcaopta build/macos/usr/local/bin/
chmod +x build/macos/usr/local/bin/orcaopta

pkgbuild \
  --root build/macos \
  --identifier com.orcaopta.cli \
  --version $VERSION \
  --install-location /usr/local/bin \
  "$DIST_DIR/orcaopta-$VERSION.pkg"

echo "[macOS] .pkg created."


# -------------------------------------------------------------
# Build macOS tar.gz
# -------------------------------------------------------------
echo "[macOS] Building tar.gz..."

mkdir -p build/macos-tar
cp .venv/bin/orcaopta build/macos-tar/
chmod +x build/macos-tar/orcaopta

tar -czvf "$DIST_DIR/orcaopta-macos-$VERSION.tar.gz" -C build/macos-tar orcaopta
echo "[macOS] tar.gz created."


# -------------------------------------------------------------
# Summary
# -------------------------------------------------------------
echo "============================================================"
echo "BUILD COMPLETE — ARTIFACTS:"
echo "============================================================"
ls -lh $DIST_DIR
echo "============================================================"
echo "All builds packaged successfully."
