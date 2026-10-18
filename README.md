# EasyDP Local PII Scanner

<p align="center">
  <a href="https://easydp.in">
    <img src="https://raw.githubusercontent.com/easydp-in/pii-scanner/main/EasyDP-Local-PII-Scanner-flow.png" alt="EasyDP Local PII Scanner Architecture" width="650"/>
  </a>
</p>

<p align="center">
  <strong>Enterprise-grade, 100% offline local PII scanner for Indian DPDP Act compliance.</strong><br>
  Find customer data across your PCs, local files, and Tally ERP with zero cloud uploads.
</p>

<p align="center">
  <a href="https://github.com/easydp-in/pii-scanner/actions/workflows/ci.yml"><img src="https://github.com/easydp-in/pii-scanner/actions/workflows/ci.yml/badge.svg" alt="CI Status"/></a>
  <a href="https://github.com/easydp-in/pii-scanner/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-blue.svg" alt="License"/></a>
  <a href="https://pypi.org/project/easydp-pii-scanner/"><img src="https://img.shields.io/pypi/v/easydp-pii-scanner.svg?color=green" alt="PyPI Version"/></a>
  <a href="https://www.npmjs.com/package/@easydp/pii-scanner"><img src="https://img.shields.io/npm/v/@easydp/pii-scanner.svg?color=red" alt="NPM Version"/></a>
  <a href="https://easydp.in"><img src="https://img.shields.io/badge/Powered%20By-EasyDP.in-0ea5e9" alt="EasyDP.in"/></a>
</p>

---

> ### ⚠️ Legal & Compliance Disclaimer
> 1. **Not Legal Advice**: This software is an automated scanner for information governance and privacy risk assessment under India's Digital Personal Data Protection (DPDP) Act, 2023. It does **not** constitute legal advice, statutory audit certification, or an official audit guarantee.
> 2. **User Authorization**: The operator certifies that they have lawful authority and consent to scan the target files, drives, or accounting systems.
> 3. **100% Local Guarantee**: Scans execute entirely on your machine. No raw files, names, Aadhaar numbers, PANs, or phone numbers are ever transmitted to any remote server.
> 4. **Safe Masking**: In compliance with the Aadhaar Act regulations, all sensitive identifiers are masked (e.g., `XXXX-XXXX-1234`) across console logs and generated reports.
>
> *Read the full [DISCLAIMER.md](DISCLAIMER.md) before deployment.*

---

## Key Features

- **Strict Checksum Verification**: Eliminates false positives by validating statutory check digits:
  - **Aadhaar**: Verhoeff dihedral group algorithm ($D_5$).
  - **PAN Card**: Format verification, entity type classification (Individual, Company, Firm, HUF, Trust), and 5th-character check.
  - **GSTIN**: State code validation (01–37, 97, 99), embedded PAN checksum, and statutory Mod-36 check digit.
  - **Bank IFSC**: RBI bank & branch code pattern validation.
  - **UPI VPA**: Verification of payment handles (`@okhdfcbank`, `@paytm`, `@ybl`, etc.).
  - **Indian Mobile Numbers**: Digit-boundary isolated 10-digit validation (+91 / 0 / 6–9).
  - **Email Addresses**: RFC compliant email pattern matching.
- **Data Ownership & DPDP Inventory**: Directly surfaces what data types and quantities your organization owns:
  - Breakdown by category (Identity, Financial, Contact).
  - File density & concentration mapping.
  - High-risk directory exposure alerts (`Downloads/`, `Desktop/`, shared drives).
  - Retention risk alerts (files untouched for >1 year and >3 years).
- **Direct Tally ERP Integration**: Audits customer ledgers and sundry debtors directly from Tally on `localhost:9000` without requiring manual export.
- **Interactive Offline HTML Dashboard**: Generates a self-contained, responsive HTML report with searchable tables, category filters, and visualization charts.
- **Zero-Egress Security**: Formally verified via automated socket isolation assertions during tests.

---

## Installation

Choose the installation method best suited for your operating system:

### 1. One-Line Installer (macOS & Linux)
```bash
curl -fsSL https://raw.githubusercontent.com/easydp-in/pii-scanner/main/scripts/install.sh | bash
```

### 2. Windows PowerShell One-Line Installer
```powershell
irm https://raw.githubusercontent.com/easydp-in/pii-scanner/main/scripts/install.ps1 | iex
```

### 3. Homebrew (macOS / Linux)
```bash
brew tap easydp-in/tap
brew install easydp-scan
```

### 4. NPM / NPX (Node.js Developers)
```bash
# Run instantly without installing:
npx @easydp/pii-scanner scan ./my-data

# Or install globally:
npm install -g @easydp/pii-scanner
```

### 5. Python / Pip / Pipx
```bash
pipx run easydp-pii-scanner scan .
# Or via pip
pip install easydp-pii-scanner
```

### 6. Precompiled Standalone Binaries (Offline PCs)
Download single-file executables with zero dependencies from [GitHub Releases](https://github.com/easydp-in/pii-scanner/releases):
- **Windows**: `pii-scanner-windows-amd64.exe`
- **macOS**: `pii-scanner-darwin-universal`
- **Linux**: `pii-scanner-linux-amd64`

---

## Quickstart & Usage

### Scan Local Files & Folders
```bash
# Scan current directory and generate interactive HTML & JSON reports:
easydp-scan scan . --format html,json,cli --output-dir ./reports

# Scan a specific customer export directory:
easydp-scan scan /path/to/customer/files -f html -o ./reports

# Exclude specific folders:
easydp-scan scan . --exclude "node_modules,temp_archive"
```

### Audit Local Tally ERP
Ensure Tally ERP 9 or Tally Prime is running on your PC (port 9000 enabled):
```bash
easydp-scan tally --port 9000 --format html,cli --output-dir ./tally_reports
```

---

## Output Formats

### 1. Interactive HTML Dashboard
A standalone, self-contained report (`scan_report.html`) complete with:
- EasyDP branding and executive summary KPI cards.
- Horizontal distribution bar charts of personal data types owned.
- Real-time client-side search box and category filter pills.
- Masked sample previews for verified findings.

### 2. DPDP Inventory JSON
Machine-readable JSON (`scan_report.json`) conforming to `@context: "https://easydp.in/schema/v1/pii-inventory.json"` for integration into internal compliance registers.

### 3. Rich Terminal Output
Formatted color-coded tables summarizing metrics, counts, and sample findings directly in your terminal.

---

## Test-Driven Development (TDD) Architecture

This project enforces strict TDD with four distinct testing tiers:

```bash
# Run Unit, Integration, and E2E suites with coverage:
pytest tests/unit tests/integration tests/e2e -v --cov=pii_scanner

# Run privacy network isolation test:
pytest tests/e2e/test_privacy_network_isolation.py -v

# Run smoke test on sample data:
pytest tests/smoke/test_binary_smoke.py -v

# Lint and type check:
ruff check . && ruff format --check . && mypy src/
```

---

## Contributing

We welcome contributions! Please review [CONTRIBUTING.md](CONTRIBUTING.md) for conventional commit guidelines and developer setup.

---

## License

Copyright © 2026 [EasyDP](https://easydp.in).  
Distributed under the **Apache License, Version 2.0**. See [LICENSE](LICENSE) for details.
