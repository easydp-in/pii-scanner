#!/usr/bin/env bash
# EasyDP Local PII Scanner — macOS .app Bundle and DMG/Zip Packager
# https://easydp.in
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
DIST_DIR="${ROOT_DIR}/dist"
BIN_NAME="${1:-easydp-scan-macos-universal}"

echo "============================================================"
echo "  Packaging EasyDP Scanner.app for macOS"
echo "============================================================"

mkdir -p "${DIST_DIR}"
APP_BUNDLE="${DIST_DIR}/EasyDP Scanner.app"
CONTENTS="${APP_BUNDLE}/Contents"
MACOS_DIR="${CONTENTS}/MacOS"
RESOURCES_DIR="${CONTENTS}/Resources"

rm -rf "${APP_BUNDLE}"
mkdir -p "${MACOS_DIR}" "${RESOURCES_DIR}"

# 1. Copy icon if available
if [ -f "${ROOT_DIR}/brand/AppIcon.icns" ]; then
  cp "${ROOT_DIR}/brand/AppIcon.icns" "${RESOURCES_DIR}/AppIcon.icns"
fi

# 2. Generate Info.plist
cat << 'EOF' > "${CONTENTS}/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleDisplayName</key>
    <string>EasyDP Scanner</string>
    <key>CFBundleExecutable</key>
    <string>EasyDP Scanner</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>in.easydp.scanner</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>EasyDP Scanner</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>0.1.1</string>
    <key>CFBundleVersion</key>
    <string>0.1.1</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# 3. Copy launcher command script
cp "${SCRIPT_DIR}/easydp-scan.command" "${RESOURCES_DIR}/easydp-scan.command"
chmod +x "${RESOURCES_DIR}/easydp-scan.command"

# Also place standalone easydp-scan.command in dist/
cp "${SCRIPT_DIR}/easydp-scan.command" "${DIST_DIR}/easydp-scan.command"
chmod +x "${DIST_DIR}/easydp-scan.command"

# 4. Copy binary into App Bundle MacOS directory if available
if [ -f "${DIST_DIR}/${BIN_NAME}" ]; then
  cp "${DIST_DIR}/${BIN_NAME}" "${MACOS_DIR}/easydp-scan"
  chmod +x "${MACOS_DIR}/easydp-scan"
  codesign --force --deep -s - "${MACOS_DIR}/easydp-scan" 2>/dev/null || true
  codesign --force --deep -s - "${DIST_DIR}/${BIN_NAME}" 2>/dev/null || true
fi

# 5. App executable launcher (runs interactive terminal session)
cat << 'EOF' > "${MACOS_DIR}/EasyDP Scanner"
#!/bin/bash
DIR="$(cd "$(dirname "$0")/../Resources" && pwd)"
open -a Terminal "${DIR}/easydp-scan.command"
EOF
chmod +x "${MACOS_DIR}/EasyDP Scanner"

# 6. Ad-hoc codesign .app
codesign --force --deep -s - "${APP_BUNDLE}" 2>/dev/null || true

# 7. Package into ZIP
cd "${DIST_DIR}"
ZIP_FILES=("EasyDP Scanner.app" "easydp-scan.command")
if [ -f "${DIST_DIR}/${BIN_NAME}" ]; then
  ZIP_FILES+=("${BIN_NAME}")
fi
zip -r EasyDP-Scanner-macOS.zip "${ZIP_FILES[@]}"
echo "✓ Created: ${DIST_DIR}/EasyDP-Scanner-macOS.zip"
echo "✓ Created: ${DIST_DIR}/easydp-scan.command"
echo "✓ Created: ${APP_BUNDLE}"
