# EasyDP Local PII Scanner Wiki

Welcome to the **EasyDP Local PII Scanner** documentation wiki!

This scanner is an open-source, offline-first compliance utility engineered to help organizations, Chartered Accountants (CAs), compliance officers, and IT teams locate and inventory personal data across Windows/macOS/Linux PCs and local accounting systems like Tally ERP.

---

## 🔒 The Core Privacy Promise: Zero Telemetry & 100% Local
- **No Cloud Uploads**: Customer files, Aadhaar numbers, PANs, and phone numbers **never leave the host PC**.
- **No Automated Telemetry**: The scanner contains zero analytics beacons, background trackers, or automated sync routines.
- **Air-Gapped Operation**: Unplug your internet or disable Wi-Fi; the scanner runs locally with 100% functionality.

---

## 📚 Wiki Sections

### 1. [CA & Auditor Guide](CA-and-Auditor-Guide)
A step-by-step guide for Chartered Accountants, Tax Practitioners, and Internal Auditors scanning client SMB PCs using single-file `.exe` binaries with zero Python required.

### 2. [Tally ERP 9 & Tally Prime Guide](Tally-ERP-Guide)
Detailed setup instructions for auditing customer ledgers, sundry debtors, and vendor PAN/GSTIN data directly via `localhost:9000` without manual export.

### 3. [DPDP Act 2023 Compliance & Data Inventory Mapping](DPDP-Act-Compliance-Mapping)
How scan results map to Data Fiduciary obligations (DIM-01, DIM-03), data retention risk limits, and the critical distinction between corporate vs. sole-proprietor B2B records.

### 4. [Statutory Checksum Algorithms](Statutory-Checksum-Algorithms)
Technical deep-dive into the error-detection algorithms used to eliminate false alarms:
- **Aadhaar**: Verhoeff dihedral group error-detection algorithm ($D_5$).
- **GSTIN**: 15-character Mod-36 checksum calculation.
- **PAN**: Legal entity classification logic (Individual vs Company vs Firm).

---

## 🚀 Quick Navigation
- [Main GitHub Repository](https://github.com/easydp-in/pii-scanner)
- [Official Website](https://easydp.in)
- [Download Standalone Releases](https://github.com/easydp-in/pii-scanner/releases)
