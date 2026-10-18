#!/usr/bin/env bash
# EasyDP Local PII Scanner — One-Line Installer for macOS & Linux
# https://easydp.in
set -euo pipefail

REPO="easydp-in/pii-scanner"
INSTALL_DIR="${HOME}/.local/bin"
BIN_NAME="easydp-scan"

echo "============================================================"
echo "  EasyDP Local PII Scanner Installer"
echo "  Enterprise-Grade, 100% Offline DPDP Compliance Scanner"
echo "  https://easydp.in"
echo "============================================================"

OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"

case "${ARCH}" in
  x86_64|amd64) ARCH_TAG="amd64" ;;
  arm64|aarch64) ARCH_TAG="arm64" ;;
  *) echo "Unsupported architecture: ${ARCH}"; exit 1 ;;
esac

mkdir -p "${INSTALL_DIR}"

if command -v python3 >/dev/null 2>&1; then
  echo "=> Installing easydp-pii-scanner via pip..."
  python3 -m pip install --quiet --upgrade pip
  python3 -m pip install --quiet --upgrade "easydp-pii-scanner" || {
    echo "=> Installing directly from GitHub repository..."
    python3 -m pip install --quiet "git+https://github.com/${REPO}.git"
  }
else
  echo "=> Downloading pre-compiled standalone binary for ${OS}-${ARCH_TAG}..."
  BINARY_URL="https://github.com/${REPO}/releases/latest/download/pii-scanner-${OS}-${ARCH_TAG}"
  curl -fsSL "${BINARY_URL}" -o "${INSTALL_DIR}/${BIN_NAME}"
  chmod +x "${INSTALL_DIR}/${BIN_NAME}"
fi

echo ""
echo "============================================================"
echo "  Installation Complete!"
echo "  Run a scan using:"
echo "    easydp-scan scan ./my-files --format html,json"
echo "============================================================"
