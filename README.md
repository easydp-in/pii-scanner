# EasyDP Local PII Scanner

<p align="center">
  <a href="https://easydp.in">
    <img src="https://raw.githubusercontent.com/easydp-in/pii-scanner/main/EasyDP-Local-PII-Scanner-flow.png" alt="EasyDP Local PII Scanner Architecture" width="650"/>
  </a>
</p>

<p align="center">
  <strong>Enterprise-grade, 100% offline local PII & B2B scanner for Indian DPDP Act compliance.</strong><br>
  Discover and inventory personal data across local PC storage, shared folders, and Tally ERP with zero cloud uploads.
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
> 2. **User Authorization**: The operator certifies that they have lawful authority and consent to scan target files, drives, or accounting systems.
> 3. **100% Local Guarantee**: Scans execute entirely on your machine. No raw files, names, Aadhaar numbers, PANs, or phone numbers are ever transmitted to any remote server.
> 4. **Safe Masking**: In compliance with the Aadhaar Act regulations, all sensitive identifiers are masked (e.g., `XXXX-XXXX-1234`) across console logs and generated reports.
>
> *Read the full [DISCLAIMER.md](DISCLAIMER.md) before deployment.*

---

## Features

### 1. Comprehensive Coverage for Both B2C & B2B Data
- **B2B Commercial & Tax Identifiers**:
  - **GSTIN**: Validates 15-character Goods and Services Tax Identification Numbers across all Indian states (01–37, 97, 99), verifying the embedded PAN and statutory **Mod-36 check digit**.
  - **Entity-Classified PANs**: Automatically categorizes the 4th character of PAN into:
    - `C` = Incorporated Company (Pvt Ltd / Ltd)
    - `F` = Partnership Firm / Limited Liability Partnership (LLP)
    - `H` = Hindu Undivided Family (HUF)
    - `T` = Trust / NGO
    - `A` = Association of Persons (AOP)
    - `P` = Individual / Sole Proprietor
  - **Tally ERP 9 / Prime Ledgers**: Connects via `localhost:9000` to inspect `Sundry Debtors` (B2B clients) and `Sundry Creditors` (vendors) directly without manual export.
  - **Commercial Banking**: Bank branch IFSC codes (`SBIN0***234`) across payment vouchers and vendor payout sheets.
- **B2C Personal Identifiers**:
  - **Aadhaar Numbers**: Validates the 12th check digit using the **Verhoeff dihedral group algorithm ($D_5$)**. Enforces UIDAI constraints (numbers cannot begin with `0` or `1`).
  - **Indian Mobile Numbers**: Enforces National Numbering Plan (+91 / 0 / 6–9) with digit-boundary isolation, eliminating false substring matches on timestamps or invoice serials.
  - **UPI Virtual Payment Addresses**: Identifies handles (`user@okhdfcbank`, `mobile@paytm`, `name@ybl`).
  - **Email Addresses**: RFC compliant email pattern matching for personal and corporate mailboxes.

### 2. Data Ownership & Governance Metrics
- **Types & Quantities Owned**: Surfaces exact counts per PII type and broad categories (*Identity*, *Financial*, *Contact*).
- **High-Risk Exposure Alerts**: Flags sensitive files located in unprotected directories (`Downloads/`, `Desktop/`, shared network drives).
- **Retention Staleness Risk**: Identifies files untouched for >1 year and >3 years to prevent unlawful retention under the DPDP Act.

### 3. Reporting Formats
- **Interactive HTML Dashboard**: Self-contained, responsive offline report with search box, filter pills, distribution charts, and masked previews.
- **DPDP JSON Inventory**: Conforms to `@context: "https://easydp.in/schema/v1/pii-inventory.json"` for enterprise data catalogs.
- **Rich Terminal Summary**: Instant command-line status with EasyDP ASCII banner and colored tables.

---

## Installation

Choose the installation method suited for your platform:

### Method 1: Pre-Compiled Standalone Binaries (Recommended for Windows SMBs & CAs)
Requires **zero Python or Node installation**. Download the single executable from [GitHub Releases](https://github.com/easydp-in/pii-scanner/releases):
- **Windows**: `pii-scanner-windows-amd64.exe`
- **macOS**: `pii-scanner-darwin-universal` (Apple Silicon & Intel)
- **Linux**: `pii-scanner-linux-amd64`

### Method 2: One-Line Install Script
**On macOS & Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/easydp-in/pii-scanner/main/scripts/install.sh | bash
```

**On Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/easydp-in/pii-scanner/main/scripts/install.ps1 | iex
```

### Method 3: Homebrew (macOS & Linux)
```bash
brew tap easydp-in/tap
brew install easydp-scan
```

### Method 4: NPM / NPX (JavaScript & Web Developers)
```bash
# Run instantly without installing:
npx @easydp/pii-scanner scan ./my-data

# Or install globally:
npm install -g @easydp/pii-scanner
```

### Method 5: Python / Pip / Pipx
```bash
# Isolated CLI installation via pipx:
pipx run easydp-pii-scanner scan .

# Or via standard pip:
pip install easydp-pii-scanner
```

---

## Multi-OS & Installation Coverage in CI/CD

Our GitHub Actions pipeline continuously tests the scanner across operating systems and distribution channels:

| Operating System | Unit & Integration | E2E Isolation | Pip Package | NPM Wrapper | Shell / PS1 Script | PyInstaller Binary |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Ubuntu Linux (x86_64)** | ✅ | ✅ | ✅ | ✅ | ✅ (`install.sh`) | ✅ |
| **macOS (Universal / Apple Silicon)** | ✅ | ✅ | ✅ | ✅ | ✅ (`install.sh`) | ✅ |
| **Windows 10/11 (AMD64)** | ✅ | ✅ | ✅ | ✅ | ✅ (`install.ps1`) | ✅ (`.exe`) |

---

## Quickstart & Usage

### 1. Scan Local Files & Folders
```bash
# Scan current folder and generate HTML & JSON reports in ./reports:
easydp-scan scan . --format html,json,cli --output-dir ./reports

# Scan customer exports on a specific drive:
easydp-scan scan "D:\Client_Accounts" --format html --output-dir ./reports

# Exclude temporary or build directories:
easydp-scan scan . --exclude "node_modules,temp_archive"

# Quiet mode for automated CI/CD pipelines:
easydp-scan scan ./data -f json -q
```

### 2. Audit Local Tally ERP
Ensure Tally ERP 9 or Tally Prime is running on your machine (ODBC/HTTP port 9000 enabled):
```bash
easydp-scan tally --port 9000 --format html,cli --output-dir ./tally_reports
```

---

## Troubleshooting & FAQs

### Q1: Is my data uploaded to any cloud or external server?
**No.** EasyDP Local PII Scanner is built strictly with an offline-first architecture. All file discovery, text extraction, checksum validation, and report generation execute 100% locally on your machine. Our automated test suite includes socket-level hooks that fail the build if any outbound network connection is attempted during a scan.

### Q2: Does the scanner cover B2B data (suppliers, vendors, corporate clients)?
**Yes.** The scanner covers B2B data through:
1. **GSTIN Checksum Validation**: Validates 15-digit GST numbers for suppliers and commercial parties.
2. **Entity-Classified PANs**: Distinguishes companies (`C`), partnership firms (`F`), trusts (`T`), and HUFs (`H`) from individual proprietors (`P`).
3. **Sole Proprietors**: Under the DPDP Act 2023, sole proprietorship data **is** personal data because it uses the proprietor's personal PAN and name. EasyDP identifies this automatically.
4. **Tally ERP Ledgers**: Directly scans `Sundry Creditors` (suppliers) and `Sundry Debtors` (buyers).

### Q3: How do I scan Tally ERP 9 or Tally Prime?
1. Open Tally ERP 9 or Tally Prime.
2. Ensure local ODBC/HTTP server is enabled in Tally:
   - Go to `F12: Configure` > `Advanced Configuration`.
   - Set **Tally is acting as** to `Both` or `Server`.
   - Set **Port** to `9000`.
3. Open your terminal or Command Prompt and run:
   ```bash
   easydp-scan tally --port 9000
   ```
4. If Tally is closed or not listening, the scanner will inform you with a clear notice without crashing.

### Q4: Why didn't a 12-digit number get flagged as an Aadhaar number?
Aadhaar validation is **not** a simple 12-digit regex match. It enforces statutory checksum rules:
- Must pass the **Verhoeff dihedral algorithm** ($D_5$) on the 12th check digit.
- UIDAI rules dictate that legitimate Aadhaar numbers never begin with `0` or `1`.
Random 12-digit transaction numbers, barcodes, or credit card substrings fail the Verhoeff check and are ignored to avoid false alarms.

### Q5: How do I run this on a non-technical accountant's Windows machine?
Download the standalone executable `pii-scanner-windows-amd64.exe` from [Releases](https://github.com/easydp-in/pii-scanner/releases). No Python or dependencies are required. Simply open PowerShell or Command Prompt in the folder and run:
```powershell
.\pii-scanner-windows-amd64.exe scan "C:\Users\Admin\Documents"
```

### Q6: How do I open and share the generated HTML report?
The generated `scan_report.html` is completely self-contained. It contains inline CSS and vanilla JavaScript with zero external CDN dependencies:
- Double-click the file to open it in Chrome, Edge, Safari, or Firefox.
- Works 100% offline (you can unplug your Wi-Fi and the report still functions).
- You can print or save it as a PDF directly from your browser (`Ctrl+P` / `Cmd+P`).

### Q7: What if I have huge Excel sheets or multi-gigabyte CSVs?
EasyDP Local PII Scanner uses memory-efficient streaming:
- CSVs are parsed row-by-row without buffering the whole file in memory.
- Excel files (`.xlsx`) use `openpyxl` read-only streaming mode.
- If you have specific folders you wish to skip, pass `--exclude "folder_name"`.

---

## Test-Driven Development (TDD) Commands

```bash
# Run all Unit, Integration, E2E, and Smoke tests:
pytest tests/ -v --cov=pii_scanner --cov-report=term-missing

# Run privacy network isolation test:
pytest tests/e2e/test_privacy_network_isolation.py -v

# Run linting and type analysis:
ruff check . && ruff format --check . && mypy src/
```

---

## Contributing & License

Contributions are welcome! Please follow [CONTRIBUTING.md](CONTRIBUTING.md) for conventional commits.

Copyright © 2026 [EasyDP](https://easydp.in).  
Distributed under the **Apache License, Version 2.0**. See [LICENSE](LICENSE) for details.
