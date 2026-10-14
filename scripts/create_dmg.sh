#!/bin/bash
# Creates a distributable macOS DMG disk image for DockPet.
# Usage: ./scripts/create_dmg.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
APP_NAME="DockPet"
DMG_NAME="${APP_NAME}.dmg"
DMG_PATH="$PROJECT_DIR/build/${DMG_NAME}"
STAGING_DIR="$PROJECT_DIR/build/dmg_staging"

# 1. Build release application bundle
echo "[dmg] Building release bundle..."
"$SCRIPT_DIR/build_app.sh" --release

# 2. Prepare staging directory
echo "[dmg] Preparing DMG contents..."
rm -rf "$STAGING_DIR"
mkdir -p "$STAGING_DIR"

# Copy signed app bundle
cp -R "$PROJECT_DIR/build/${APP_NAME}.app" "$STAGING_DIR/"

# Create /Applications symlink for drag-and-drop installation
ln -s /Applications "$STAGING_DIR/Applications"

# 3. Create compressed DMG
echo "[dmg] Generating disk image..."
rm -f "$DMG_PATH"
hdiutil create \
    -volname "$APP_NAME" \
    -srcfolder "$STAGING_DIR" \
    -ov \
    -format UDZO \
    "$DMG_PATH"

# 4. Clean up staging
rm -rf "$STAGING_DIR"

echo "[dmg] Successfully created: $DMG_PATH"
ls -lh "$DMG_PATH"
