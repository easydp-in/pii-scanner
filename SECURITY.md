# Security Policy

EasyDP takes the security and privacy of this open-source scanner seriously. Because this tool handles sensitive personal data detection, zero-egress integrity and vulnerability prevention are our highest priorities.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Offline Guarantee, Zero-Egress & No Automated Data Sharing

EasyDP Local PII Scanner is engineered with an uncompromising zero-egress, zero-telemetry policy:
- **No Automated Data Sharing**: The scanner does not include any analytics beacons, remote telemetry, automated sync agents, or diagnostic collectors. No scan data or counts are transmitted automatically.
- **Strictly Offline**: No internet connection is required or attempted during scan execution. The software can run in completely air-gapped systems.
- **Automated Verification**: Every release is tested with automated socket isolation assertions in our CI pipeline to ensure zero outbound network connections occur during scanning.

## Reporting a Vulnerability

If you discover a security vulnerability or potential privacy leak:

1. **Do NOT report security vulnerabilities through public GitHub issues.**
2. Send an email to **security@easydp.in** with:
   - A description of the issue.
   - Steps to reproduce or a Proof of Concept (PoC).
   - The potential impact.
3. We will acknowledge receipt within 48 hours and work on a prompt remediation.
