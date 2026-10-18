"""E2E tests for the easydp-scan / pii-scanner CLI interface."""

from pathlib import Path

from pii_scanner.cli import run_cli
from pii_scanner.validators.verhoeff import calculate_verhoeff


def test_cli_version(capsys: object) -> None:
    code = run_cli(["--version"])
    assert code == 0


def test_cli_scan_directory(tmp_path: Path) -> None:
    # Prepare sample dataset
    valid_aadhaar = "36759834256" + calculate_verhoeff("36759834256")
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    sample_file = data_dir / "customers.csv"
    sample_file.write_text(f"Name,Aadhaar\nTest,{valid_aadhaar}\n", encoding="utf-8")

    output_dir = tmp_path / "output_reports"

    # Invoke CLI
    exit_code = run_cli(
        [
            "scan",
            str(data_dir),
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


def test_cli_help() -> None:
    code = run_cli(["--help"])
    assert code == 0


def test_cli_no_args() -> None:
    code = run_cli([])
    assert code == 0


def test_cli_invalid_path(tmp_path: Path) -> None:
    code = run_cli(["scan", str(tmp_path / "non_existent_folder")])
    assert code == 1


def test_cli_tally(tmp_path: Path) -> None:
    from unittest.mock import MagicMock, patch

    mock_resp = MagicMock()
    mock_resp.read.return_value = b"<ENVELOPE><BODY><DATA></DATA></BODY></ENVELOPE>"
    mock_resp.__enter__.return_value = mock_resp

    out_dir = tmp_path / "tally_out"
    with patch("urllib.request.urlopen", return_value=mock_resp):
        code = run_cli(
            [
                "tally",
                "--port",
                "9000",
                "--output-dir",
                str(out_dir),
                "--format",
                "html,json,cli",
            ]
        )
        assert code == 0
        assert (out_dir / "tally_report.html").exists()
        assert (out_dir / "tally_report.json").exists()


def test_cli_user_dirs(tmp_path: Path) -> None:
    from unittest.mock import patch

    mock_dirs = [str(tmp_path)]
    (tmp_path / "note.txt").write_text("Contact: 9876543210", encoding="utf-8")

    with patch("pii_scanner.core.engine.get_common_user_directories", return_value=mock_dirs):
        code = run_cli(["scan", "--user-dirs", "-q", "-o", str(tmp_path / "out")])
        assert code == 0


def test_cli_report_error(capsys: object) -> None:
    from unittest.mock import patch

    with patch("webbrowser.open") as mock_open:
        # 1. Test subcommand with --no-browser
        code1 = run_cli(["report-error", "--no-browser"])
        assert code1 == 0
        mock_open.assert_not_called()

        # 2. Test flag with --no-browser
        code1_flag = run_cli(["--report-error", "--no-browser"])
        assert code1_flag == 0
        mock_open.assert_not_called()

        # 3. Test flag with browser open
        code2 = run_cli(["--report-error"])
        assert code2 == 0
        mock_open.assert_called_once_with("https://github.com/easydp-in/pii-scanner/issues/new")

    with patch("webbrowser.open") as mock_open2:
        code3 = run_cli(["--report-issue"])
        assert code3 == 0
        mock_open2.assert_called_once_with("https://github.com/easydp-in/pii-scanner/issues/new")


def test_cli_scan_creates_log_file(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "test.csv").write_text("Name,Phone\nAlice,9876543210\n", encoding="utf-8")
    out_dir = tmp_path / "reports"

    code = run_cli(["scan", str(data_dir), "-o", str(out_dir), "-q"])
    assert code == 0

    log_path = out_dir / "scanner.log"
    assert log_path.exists()
    log_content = log_path.read_text(encoding="utf-8")
    assert "EasyDP PII Scanner logging initialized" in log_content
    assert "test.csv" in log_content
    assert "Scan complete" in log_content


def test_cli_scan_custom_log_file(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "sample.txt").write_text("Contact me at info@example.com", encoding="utf-8")
    custom_log = tmp_path / "logs" / "custom_scan.log"

    code = run_cli(["scan", str(data_dir), "--log-file", str(custom_log), "-q"])
    assert code == 0

    assert custom_log.exists()
    log_text = custom_log.read_text(encoding="utf-8")
    assert "sample.txt" in log_text


def test_cli_scan_with_progress_and_completion_banner(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "doc.txt").write_text("Sample text with no PII", encoding="utf-8")
    out_dir = tmp_path / "out"

    # Non-quiet mode exercises Progress bar and print_completion_banner
    code = run_cli(["scan", str(data_dir), "-o", str(out_dir)])
    assert code == 0
    assert (out_dir / "scan_report.html").exists()
    assert (out_dir / "scanner.log").exists()
