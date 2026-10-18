#!/usr/bin/env bash
# ==============================================================================
# NETSpeed by RipoN - macOS Build & Packaging Script
# Generates a standalone macOS Menu Bar Application (.app) and Drag-and-Drop Disk Image (.dmg)
# ==============================================================================

set -euo pipefail

echo "================================================="
echo "  Building NETSpeed for macOS"
echo "  Author: RipoN"
echo "================================================="

# 1. Ensure Dependencies
echo "[1/4] Installing / Verifying Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip install pyinstaller

# 2. Generate Apple .icns Icon from NetSpeed.png
echo "[2/4] Generating NetSpeed.icns from NetSpeed.png..."
if command -v sips &> /dev/null && command -v iconutil &> /dev/null; then
    ICONSET="NetSpeed.iconset"
    rm -rf "${ICONSET}"
    mkdir -p "${ICONSET}"

    sips -z 16 16     NetSpeed.png --out "${ICONSET}/icon_16x16.png" > /dev/null
    sips -z 32 32     NetSpeed.png --out "${ICONSET}/icon_16x16@2x.png" > /dev/null
    sips -z 32 32     NetSpeed.png --out "${ICONSET}/icon_32x32.png" > /dev/null
    sips -z 64 64     NetSpeed.png --out "${ICONSET}/icon_32x32@2x.png" > /dev/null
    sips -z 128 128   NetSpeed.png --out "${ICONSET}/icon_128x128.png" > /dev/null
    sips -z 256 256   NetSpeed.png --out "${ICONSET}/icon_128x128@2x.png" > /dev/null
    sips -z 256 256   NetSpeed.png --out "${ICONSET}/icon_256x256.png" > /dev/null
    sips -z 512 512   NetSpeed.png --out "${ICONSET}/icon_256x256@2x.png" > /dev/null
    sips -z 512 512   NetSpeed.png --out "${ICONSET}/icon_512x512.png" > /dev/null

    iconutil -c icns "${ICONSET}" -o NetSpeed.icns
    rm -rf "${ICONSET}"
    echo "  -> NetSpeed.icns successfully generated."
fi

# 3. Build .app Bundle with PyInstaller
echo "[3/4] Compiling NETSpeed.app via PyInstaller..."
rm -rf build dist
pyinstaller --clean --noconfirm NETSpeed.spec

# 4. Create DMG Installer
echo "[4/4] Creating NETSpeed-macOS.dmg..."
DMG_DIR="dist/dmg_staging"
rm -rf "${DMG_DIR}" dist/NETSpeed-macOS.dmg
mkdir -p "${DMG_DIR}"

cp -R "dist/NETSpeed.app" "${DMG_DIR}/"
ln -s /Applications "${DMG_DIR}/Applications"

hdiutil create -volname "NETSpeed" -srcfolder "${DMG_DIR}" -ov -format UDZO "dist/NETSpeed-macOS.dmg"
rm -rf "${DMG_DIR}"

echo "================================================="
echo "  Build Complete!"
echo "  macOS App:  dist/NETSpeed.app"
echo "  macOS DMG:  dist/NETSpeed-macOS.dmg"
echo "================================================="
