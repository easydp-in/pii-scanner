# easydp-pii-scanner

> **Enterprise-grade, 100% offline DPDP Act compliance scanner for local files and accounting systems.**
> Powered by [EasyDP.in](https://easydp.in) — Built for India's Digital Personal Data Protection Act, 2023.

---

## Quick Start (NPX & NPM)

You can run `easydp-scan` directly via `npx` with zero installation:

### ⚡ Normal Mode (Instant statutory checksums & rules)
```bash
# Run scan on current directory
npx easydp-pii-scanner scan .

# Scan customer exports into reports/
npx easydp-pii-scanner scan ./my-data --format html,json
```

### 🧠 Local AI Mode (Deep extraction for names, addresses, health data)
```bash
# Run deep zero-shot CPU NER on current directory
npx easydp-pii-scanner scan . --local-ai

# Or install globally:
npm install -g easydp-pii-scanner
easydp-scan scan . --local-ai
```

---

## Key Features

- **100% Offline & Zero Egress**: All files are parsed in-memory on your local machine. No data or telemetry leaves your computer.
- **Dual Scan Modes**:
  - **⚡ Normal Mode**: Fast statutory checksums (>5,000 rec/sec) for Aadhaar ($D_5$), PAN, GSTIN (Mod-36), IFSC, and UPI.
  - **🧠 Local AI Mode (`--local-ai`)**: In-process zero-shot CPU NER model (`urchade/gliner_small-v2.1`, ~150MB) for unstructured Indian names, physical addresses, and sensitive health/medical data.
- **Accounting ERP Audit**: Direct loopback inspection of live Tally ERP 9 / TallyPrime party ledgers over Port 9000.
- **Comprehensive File Support**: Scans `.xlsx`, `.csv`, `.pdf`, `.docx`, `.odt`, `.rtf`, `.txt`, `.log`, `.json`, `.xml`, and `.sql`.
- **Audit-Ready Reports**: Generates interactive HTML dashboards (`reports/scan_report.html`) and structured JSON inventory catalogs (`reports/scan_report.json`).

---

## Requirements

Requires Python 3.10+ installed on the host machine. If you do not have Python installed, download the standalone air-gapped binary or macOS App directly from [GitHub Releases](https://github.com/easydp-in/pii-scanner/releases).

To use Local AI mode:
```bash
pip install "easydp-pii-scanner[ai]"
# or running --local-ai will offer to auto-install dependencies interactively
```

---

## License

Apache-2.0 License. Built with pride by [EasyDP](https://easydp.in).
