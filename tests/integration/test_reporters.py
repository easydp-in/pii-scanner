"""Integration tests for Terminal, JSON, and HTML report generators."""

import json
from pathlib import Path

from pii_scanner.core.engine import ScannerEngine
from pii_scanner.reporters.console import ConsoleReporter
from pii_scanner.reporters.html_rep import HTMLReporter
from pii_scanner.reporters.json_rep import JSONReporter
from pii_scanner.validators.verhoeff import calculate_verhoeff


def test_reporters_output(tmp_path: Path) -> None:
    # Setup test file
    valid_aadhaar = "36759834256" + calculate_verhoeff("36759834256")
    test_file = tmp_path / "data.csv"
    test_file.write_text(
        f"Name,Aadhaar,Phone\nJohn,{valid_aadhaar},9876543210\n",
        encoding="utf-8",
    )

    engine = ScannerEngine()
    summary = engine.scan_directory(str(tmp_path))

    # 1. Test Console Reporter
    console = ConsoleReporter()
    terminal_output = console.render_summary(summary)
    assert "EasyDP" in terminal_output
    assert "https://easydp.in" in terminal_output
    assert "LEGAL & COMPLIANCE DISCLAIMER" in terminal_output
    assert "Aadhaar Number" in terminal_output
    assert "Report false alarms, errors, or feedback" in terminal_output
    assert "https://github.com/easydp-in/pii-scanner/issues/new" in terminal_output

    # 2. Test JSON Reporter
    json_rep = JSONReporter()
    json_path = tmp_path / "report.json"
    json_rep.save(summary, str(json_path))

    assert json_path.exists()
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["@context"] == "https://easydp.in/schema/v1/pii-inventory.json"
    assert "EasyDP" in data["generator"]
    assert data["data_ownership_inventory"]["total_pii_instances"] >= 2
    assert "legal_disclaimer" in data

    # 3. Test HTML Reporter
    html_rep = HTMLReporter()
    html_path = tmp_path / "report.html"
    html_rep.save(summary, str(html_path))

    assert html_path.exists()
    html_content = html_path.read_text(encoding="utf-8")
    assert "EasyDP" in html_content
    assert "easydp.in" in html_content
    assert "Report Error" in html_content
    assert "https://github.com/easydp-in/pii-scanner/issues/new" in html_content
    assert (
        "LEGAL &amp; COMPLIANCE DISCLAIMER" in html_content
        or "LEGAL & COMPLIANCE DISCLAIMER" in html_content
    )
    assert (
        "Data Ownership &amp; PII Inventory" in html_content
        or "Data Ownership & PII Inventory" in html_content
    )
    assert "XXXX-XXXX-" in html_content  # Aadhaar masked
