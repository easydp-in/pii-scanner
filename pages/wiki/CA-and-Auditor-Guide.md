# Chartered Accountants & Auditors Guide

A practical handbook for Chartered Accountants (CAs), Tax Consultants, and Internal Auditors performing local privacy and DPDP Act compliance reviews for Indian SMB clients.

---

## The CA Challenge: Trust & Client Privacy

Clients are rightfully hesitant to upload customer lists, Aadhaar cards, PAN registries, or Tally backups to cloud services.

"Your files never leave your computer" is an essential trust promise for audit workflows:
- EasyDP scanner runs 100% locally.
- Zero data egress: You can unplug the laptop from Wi-Fi before running the scan.
- Single `.exe` binary: Works on client PCs with zero Python or developer tools installed.

---

## Step-by-Step Audit Workflow on Client Machines

### Step 1: Copy the Standalone Binary
1. Download `pii-scanner-windows-amd64.exe` from [GitHub Releases](https://github.com/easydp-in/pii-scanner/releases).
2. Copy it to a USB drive or download it directly onto the client's PC (e.g. `C:\Audit\`).

### Step 2: Open Command Prompt / PowerShell
Press `Win + R`, type `powershell` (or `cmd`), and navigate to the folder:
```powershell
cd C:\Audit
```

### Step 3: Run the Scan on Client Folders
Pick the folders where customer and vendor data typically accumulates:
- `C:\Users\Admin\Desktop`
- `C:\Users\Admin\Documents`
- `C:\Users\Admin\Downloads` (high-risk zone for unmanaged Aadhaar/PAN PDFs)
- Shared network drive (`Z:\Accounts\`)

```powershell
.\pii-scanner-windows-amd64.exe scan "C:\Users\Admin\Documents" --format html,json --output-dir "C:\Audit\Reports"
```

### Step 4: Audit Tally Directly
If the client uses Tally on the same machine:
```powershell
.\pii-scanner-windows-amd64.exe tally --port 9000 --output-dir "C:\Audit\Reports"
```

### Step 5: Review the Interactive HTML Report
1. Open `C:\Audit\Reports\scan_report.html` in Chrome or Edge.
2. Review:
   - **Total PII instances**: Exact counts of Aadhaar, PAN, GSTIN, Phone, Email.
   - **Retention Risk**: Files older than 1 year or 3 years (flagging unlawful retention).
   - **High-Risk Files**: Sensitive files discovered in Downloads or Desktop folders.
3. Print or Save as PDF (`Ctrl + P`) for the audit working papers.
