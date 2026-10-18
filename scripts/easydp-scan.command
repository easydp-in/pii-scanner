#!/usr/bin/env bash
# EasyDP Local PII Scanner — macOS Finder Double-Click Launcher
# https://easydp.in

DIR="$(cd "$(dirname "$0")" && pwd)"
clear

echo "============================================================"
echo "  EasyDP Local PII Scanner (macOS)"
echo "  Enterprise-Grade, 100% Offline DPDP Compliance Scanner"
echo "  https://easydp.in"
echo "============================================================"
echo ""
echo "Select scan target:"
echo "  1) Audit current directory [Default]"
echo "  2) Audit user data folders (Desktop, Documents, Downloads)"
echo "  3) Custom folder path"
echo ""
read -r -p "Enter choice [1-3, default: 1]: " CHOICE
CHOICE="${CHOICE:-1}"

# Locate binary
if [ -f "${DIR}/easydp-scan-macos-universal" ]; then
  BIN="${DIR}/easydp-scan-macos-universal"
elif [ -f "${DIR}/../MacOS/easydp-scan" ]; then
  BIN="${DIR}/../MacOS/easydp-scan"
elif [ -f "${DIR}/../MacOS/easydp-scan-macos-universal" ]; then
  BIN="${DIR}/../MacOS/easydp-scan-macos-universal"
elif [ -f "${DIR}/easydp-scan" ]; then
  BIN="${DIR}/easydp-scan"
elif [ -f "${DIR}/pii-scanner-darwin-universal" ]; then
  BIN="${DIR}/pii-scanner-darwin-universal"
elif command -v easydp-scan >/dev/null 2>&1; then
  BIN="easydp-scan"
else
  BIN="${DIR}/easydp-scan-macos-universal"
fi

# Ensure binary is executable and ad-hoc signed
chmod +x "${BIN}" 2>/dev/null || true
codesign --force --deep -s - "${BIN}" 2>/dev/null || true

OUT_DIR="${DIR}/reports"
mkdir -p "${OUT_DIR}"

case "${CHOICE}" in
  1)
    echo "=> Scanning current directory: ${DIR}..."
    "${BIN}" scan "${DIR}" --output-dir "${OUT_DIR}"
    ;;
  2)
    echo "=> Scanning standard user data folders..."
    "${BIN}" scan --user-dirs --output-dir "${OUT_DIR}"
    ;;
  3)
    read -r -p "Enter full folder path to scan: " CUSTOM_PATH
    echo "=> Scanning: ${CUSTOM_PATH}..."
    "${BIN}" scan "${CUSTOM_PATH}" --output-dir "${OUT_DIR}"
    ;;
esac

echo ""
echo "============================================================"
echo " Scan complete!"
if [ -f "${OUT_DIR}/scan_report.html" ]; then
  echo " Opening interactive report in browser..."
  open "${OUT_DIR}/scan_report.html"
fi
echo "============================================================"
echo ""
read -r -p "Press [Enter] to exit..."
