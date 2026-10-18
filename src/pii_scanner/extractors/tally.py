"""Tally ERP 9 and Tally Prime XML localhost connector.

Queries Tally directly via its local HTTP interface (default port 9000)
to audit customer ledgers, sundry debtors, PANs, GSTINs, and contact details
without requiring any manual export.
"""

import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime

from pii_scanner.core.models import FileScanResult, Finding
from pii_scanner.extractors.base import BaseExtractor

TALLY_LEDGER_REQUEST_XML = """<ENVELOPE>
    <HEADER>
        <VERSION>1</VERSION>
        <TALLYREQUEST>Export</TALLYREQUEST>
        <TYPE>Data</TYPE>
        <ID>Ledger</ID>
    </HEADER>
    <BODY>
        <DESC>
            <STATICVARIABLES>
                <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
            </STATICVARIABLES>
        </DESC>
    </BODY>
</ENVELOPE>"""


class TallyConnector(BaseExtractor):
    """Direct local connector for Tally accounting software on the PC."""

    def __init__(self, host: str = "127.0.0.1", port: int = 9000, timeout_seconds: int = 5) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self.timeout = timeout_seconds

    def extract(self, file_path: str = "Tally ERP (localhost)") -> FileScanResult:
        """Alias for extract_ledgers for unified extractor interface."""
        return self.extract_ledgers()

    def extract_ledgers(self) -> FileScanResult:
        """Query Tally HTTP XML endpoint on localhost and scan ledgers."""
        url = f"http://{self.host}:{self.port}"
        req = urllib.request.Request(
            url,
            data=TALLY_LEDGER_REQUEST_XML.encode("utf-8"),
            headers={"Content-Type": "text/xml;charset=utf-8"},
            method="POST",
        )

        all_findings: list[Finding] = []
        findings_by_type: dict[str, int] = defaultdict(int)

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                xml_data = resp.read()
        except urllib.error.URLError as e:
            return FileScanResult(
                file_path=url,
                file_name="Tally ERP (localhost:9000)",
                file_size_bytes=0,
                modified_time=datetime.now(),
                is_sensitive=False,
                findings_count=0,
                error_message=f"Tally is offline or not listening on port {self.port}: {e.reason}",
            )
        except Exception as e:
            return FileScanResult(
                file_path=url,
                file_name="Tally ERP (localhost:9000)",
                file_size_bytes=0,
                modified_time=datetime.now(),
                is_sensitive=False,
                findings_count=0,
                error_message=f"Failed to query Tally on port {self.port}: {e}",
            )

        try:
            root = ET.fromstring(xml_data)
            # Iterate through LEDGER elements
            for ledger in root.iter("LEDGER"):
                ledger_name = ledger.attrib.get("NAME", "Unknown Ledger")

                for child in ledger:
                    if child.text and len(child.text.strip()) >= 3:
                        text_val = child.text.strip()
                        location = f"Ledger '{ledger_name}', Field <{child.tag}>"
                        segment_findings = self.scan_text_segment(text_val, location)
                        for finding in segment_findings:
                            all_findings.append(finding)
                            findings_by_type[finding.pii_type.value] += 1
        except ET.ParseError as e:
            return FileScanResult(
                file_path=url,
                file_name="Tally ERP (localhost:9000)",
                file_size_bytes=len(xml_data),
                modified_time=datetime.now(),
                is_sensitive=False,
                findings_count=0,
                error_message=f"Tally response was not valid XML: {e}",
            )

        return FileScanResult(
            file_path=url,
            file_name="Tally ERP (localhost:9000)",
            file_size_bytes=len(xml_data),
            modified_time=datetime.now(),
            is_sensitive=len(all_findings) > 0,
            findings_count=len(all_findings),
            findings_by_type=dict(findings_by_type),
            sample_findings=all_findings[:15],
        )
