#!/bin/bash
# Builds DockPet and assembles a proper macOS .app bundle with Info.plist and codesign.
# Usage: ./scripts/build_app.sh [--release]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
APP_NAME="DockPet"

CONFIG="debug"
SWIFT_BUILD_ARGS=""

if [[ "${1:-}" == "--release" ]]; then
    CONFIG="release"
    SWIFT_BUILD_ARGS="-c release"
fi

BUILD_DIR="$PROJECT_DIR/.build/$CONFIG"
APP_BUNDLE="$PROJECT_DIR/build/${APP_NAME}.app"

echo "[build] Building ${APP_NAME} (${CONFIG})..."
cd "$PROJECT_DIR"
swift build $SWIFT_BUILD_ARGS 2>&1

echo "[build] Assembling ${APP_NAME}.app bundle..."
rm -rf "$APP_BUNDLE"
mkdir -p "$APP_BUNDLE/Contents/MacOS"
mkdir -p "$APP_BUNDLE/Contents/Resources"

# Copy executable
cp "$BUILD_DIR/$APP_NAME" "$APP_BUNDLE/Contents/MacOS/$APP_NAME"

# Copy Info.plist
cp "$PROJECT_DIR/DockPet/Resources/Info.plist" "$APP_BUNDLE/Contents/Info.plist"

# Copy Assets
cp -R "$PROJECT_DIR/Assets" "$APP_BUNDLE/Contents/Resources/"

# Code sign with ad-hoc signature for Gatekeeper compatibility
echo "[build] Code signing bundle..."
codesign -s - --force --deep "$APP_BUNDLE"

echo "[build] App bundle created and signed at: $APP_BUNDLE"
echo "[build] Run with: open $APP_BUNDLE"
