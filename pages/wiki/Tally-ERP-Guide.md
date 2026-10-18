# Tally ERP 9 & Tally Prime Integration Guide

EasyDP Local PII Scanner can query Tally ERP 9 and Tally Prime directly on the local machine through Tally's internal HTTP interface (default port 9000).

This allows CAs and compliance teams to audit customer ledgers, sundry debtors, and supplier PAN/GSTIN data **without requiring the client to manually export any Excel or XML files**.

---

## Prerequisites: Enabling Port 9000 in Tally

Before scanning, ensure that Tally is configured to accept local queries:

### For Tally Prime:
1. Open Tally Prime.
2. Press **F1** (`Help`) > **Settings** > **Connectivity**.
3. Under **Client/Server configuration**:
   - Set **TallyPrime acts as**: `Both` (or `Server`).
   - Set **Enable ODBC**: `Yes`.
   - Set **Port**: `9000`.
4. Restart TallyPrime to apply the changes.

### For Tally.ERP 9:
1. Open Tally.ERP 9.
2. Press **F12** (`Configure`) > **Advanced Configuration**.
3. Under **Client/Server Configuration**:
   - Set **Tally.ERP 9 acts as**: `Both` (or `Server`).
   - Set **Enable ODBC**: `Yes`.
   - Set **Port**: `9000`.
4. Press `Ctrl + A` to save and accept the prompt to restart Tally.

---

## Running the Tally Scan

Open your terminal, Command Prompt, or PowerShell:

```bash
# Default scan on localhost:9000
easydp-scan tally --port 9000 --format html,json,cli --output-dir ./tally_reports
```

### Options:
- `--host`: Target host IP (default: `127.0.0.1`).
- `--port`: Tally port (default: `9000`).
- `--format`: Desired output format: `html`, `json`, `cli` (default: `cli,html`).
- `--output-dir`: Destination path for reports (default: `./reports`).
- `--quiet`: Suppress terminal output for script automation.

---

## What Data Does the Scanner Extract?

The scanner sends a local TDL (Tally Definition Language) XML query requesting the `Ledger` collection and checks the following XML fields:
- `<NAME>`: Ledger / Party legal business name
- `<PARTYGSTIN>`: Party GSTIN (validated with Mod-36 checksum)
- `<INCOMETAXNUMBER>`: Party PAN card (classified into Individual vs Corporate)
- `<LEDGERPHONE>`: Contact mobile number
- `<EMAIL>`: Contact email address
- `<ADDRESS>`: Billing and shipping addresses

---

## Troubleshooting Common Tally Connection Issues

### "Tally is offline or not listening on port 9000"
- Verify that Tally is running and open on the PC.
- Check if another application is using port 9000 (`netstat -ano | findstr 9000` on Windows).
- If your Tally is configured on a different port (e.g. 9001), specify `--port 9001`.
