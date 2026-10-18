# @easydp/pii-scanner

> **Enterprise-grade, 100% offline DPDP Act compliance scanner for local files and accounting systems.**
> Powered by [EasyDP.in](https://easydp.in) — Built for India's Digital Personal Data Protection Act, 2023.

---

## Quick Start

You can run `easydp-scan` directly via `npx` with zero installation:

```bash
# Run scan on current directory
npx @easydp/pii-scanner scan .

# Or install globally
npm install -g @easydp/pii-scanner
easydp-scan scan ./my-data-folder --format html,json
```

---

## Key Features

- **100% Offline & Zero Egress**: All files are parsed in-memory on your local machine. No data or telemetry leaves your computer.
- **Statutory Checksum Algorithms**:
  - **Aadhaar**: UIDAI Verhoeff $D_5$ dihedral group checksum validation.
  - **GSTIN**: 15-character Mod-36 state-jurisdiction checksum.
  - **PAN**: Statutory entity classification decoding (`P`, `C`, `F`, etc.).
  - **Banking & UPI**: IFSC routing code verification and UPI VPA validation.
- **Accounting ERP Audit**: Direct loopback inspection of live Tally ERP 9 / TallyPrime party ledgers over Port 9000.
- **Comprehensive File Support**: Scans `.xlsx`, `.csv`, `.pdf`, `.docx`, `.odt`, `.rtf`, `.txt`, `.log`, `.json`, `.xml`, and `.sql`.
- **Audit-Ready Reports**: Generates interactive HTML dashboards (`reports/scan_report.html`) and structured JSON inventory catalogs (`reports/scan_report.json`).

---

## Requirements

Requires Python 3.10+ installed on the host machine. If you do not have Python installed, download the standalone air-gapped binary or macOS App directly from [GitHub Releases](https://github.com/easydp-in/pii-scanner/releases).

---

## License

Apache-2.0 License. Built with pride by [EasyDP](https://easydp.in).
