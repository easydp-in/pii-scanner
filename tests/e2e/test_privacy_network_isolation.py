"""E2E Privacy Guard Test: Asserts that zero outbound network connections occur during scanning."""

import socket
from pathlib import Path

import pytest

from pii_scanner.core.engine import ScannerEngine
from pii_scanner.reporters.html_rep import HTMLReporter
from pii_scanner.reporters.json_rep import JSONReporter


def test_zero_network_egress_during_scan(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifies that no socket connections are opened to the internet during scanning and report generation."""
    network_call_attempted = False

    def forbidden_connect(self: socket.socket, address: tuple[str, int] | str) -> None:
        nonlocal network_call_attempted
        network_call_attempted = True
        raise ConnectionError(f"Privacy Guard: Outbound network call forbidden: {address}")

    monkeypatch.setattr(socket.socket, "connect", forbidden_connect)

    # Create dummy data
    test_file = tmp_path / "offline_audit.csv"
    test_file.write_text("Customer,PAN\nRahul,ABCPD1234F\n", encoding="utf-8")

    # Run scan
    engine = ScannerEngine()
    summary = engine.scan_directory(str(tmp_path))

    # Generate reports
    html_rep = HTMLReporter()
    html_path = tmp_path / "offline_report.html"
    html_rep.save(summary, str(html_path))

    json_rep = JSONReporter()
    json_path = tmp_path / "offline_report.json"
    json_rep.save(summary, str(json_path))

    # Assert zero network calls
    assert network_call_attempted is False
    assert html_path.exists()
    assert json_path.exists()
