"""Local smoke test verifying CLI entrypoint against sample_data."""

from pathlib import Path

from pii_scanner.cli import run_cli


def test_smoke_scan_sample_data(tmp_path: Path) -> None:
    sample_dir = Path(__file__).resolve().parent.parent.parent / "sample_data"
    output_dir = tmp_path / "smoke_reports"

    exit_code = run_cli(
        [
            "scan",
            str(sample_dir),
            "--format",
            "html,json,cli",
            "--output-dir",
            str(output_dir),
            "--quiet",
        ]
    )

    assert exit_code == 0
    assert (output_dir / "scan_report.html").exists()
    assert (output_dir / "scan_report.json").exists()
