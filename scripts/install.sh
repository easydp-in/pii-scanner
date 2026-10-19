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

WANT_AI=0
for arg in "$@"; do
  if [ "${arg}" = "--local-ai" ] || [ "${arg}" = "--ai" ] || [ "${arg}" = "ai" ]; then
    WANT_AI=1
  fi
done
if [ "${INSTALL_AI:-0}" = "1" ]; then
  WANT_AI=1
fi

PKG_NAME="easydp-pii-scanner"
if [ "${WANT_AI}" = "1" ]; then
  PKG_NAME="easydp-pii-scanner[ai]"
  echo "=> Local AI Mode requested: installing with Pass 2 Edge AI dependencies (gliner, protobuf)..."
fi

if command -v python3 >/dev/null 2>&1; then
  echo "=> Installing ${PKG_NAME} via pip..."
  INSTALL_SUCCESS=0
  if [ -f "pyproject.toml" ]; then
    EXTRA_SPEC="."
    [ "${WANT_AI}" = "1" ] && EXTRA_SPEC=".[ai]"
    python3 -m pip install --quiet "${EXTRA_SPEC}" 2>/dev/null && INSTALL_SUCCESS=1 || \
    python3 -m pip install --quiet --break-system-packages "${EXTRA_SPEC}" 2>/dev/null && INSTALL_SUCCESS=1 || \
    python3 -m pip install --quiet --user --break-system-packages "${EXTRA_SPEC}" 2>/dev/null && INSTALL_SUCCESS=1 || true
  else
    python3 -m pip install --quiet --upgrade "${PKG_NAME}" 2>/dev/null && INSTALL_SUCCESS=1 || \
    python3 -m pip install --quiet --upgrade --break-system-packages "${PKG_NAME}" 2>/dev/null && INSTALL_SUCCESS=1 || \
    python3 -m pip install --quiet --user --break-system-packages "${PKG_NAME}" 2>/dev/null && INSTALL_SUCCESS=1 || \
    python3 -m pip install --quiet "git+https://github.com/${REPO}.git" 2>/dev/null && INSTALL_SUCCESS=1 || true
  fi

  # Ensure easydp-scan is available in INSTALL_DIR (~/.local/bin)
  TARGET_FILE="${INSTALL_DIR}/${BIN_NAME}"
  CLI_TARGET="$(python3 -c "import sysconfig, os; p = os.path.join(sysconfig.get_path('scripts'), 'easydp-scan'); print(p if os.path.exists(p) else '')" 2>/dev/null || true)"
  rm -f "${TARGET_FILE}"
  if [ -n "${CLI_TARGET}" ] && [ -x "${CLI_TARGET}" ] && [ "${CLI_TARGET}" != "${TARGET_FILE}" ]; then
    ln -sf "${CLI_TARGET}" "${TARGET_FILE}"
  else
    PY_BIN="$(command -v python3)"
    cat << EOF > "${TARGET_FILE}"
#!/usr/bin/env bash
exec "${PY_BIN}" -m pii_scanner.cli "\$@"
EOF
    chmod +x "${TARGET_FILE}"
  fi
else
  echo "=> Downloading pre-compiled standalone binary for ${OS}..."
  if [ "${OS}" = "darwin" ]; then
    BINARY_URL="https://github.com/${REPO}/releases/latest/download/easydp-scan-macos-universal"
  else
    BINARY_URL="https://github.com/${REPO}/releases/latest/download/easydp-scan-linux-${ARCH_TAG}"
  fi
  curl -fsSL "${BINARY_URL}" -o "${INSTALL_DIR}/${BIN_NAME}" || true
  chmod +x "${INSTALL_DIR}/${BIN_NAME}" 2>/dev/null || true
fi

# Attempt to link into /usr/local/bin for instant system-wide CLI access
if [ -w "/usr/local/bin" ] 2>/dev/null; then
  ln -sf "${INSTALL_DIR}/${BIN_NAME}" "/usr/local/bin/${BIN_NAME}" 2>/dev/null || true
fi

echo ""
echo "============================================================"
echo "  Installation Complete!"
echo "  Binary location: ${INSTALL_DIR}/${BIN_NAME}"
echo ""
echo "  Run an audit using:"
echo "    ⚡ Normal Mode:   ${BIN_NAME} scan . --format html,json"
echo "    🧠 Local AI Mode: ${BIN_NAME} scan . --local-ai"
echo ""
echo "  Or if ${INSTALL_DIR} is not in PATH:"
echo "    ~/.local/bin/${BIN_NAME} scan ."
echo "    ~/.local/bin/${BIN_NAME} scan . --local-ai"
echo "============================================================"
