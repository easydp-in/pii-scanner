"""Command Line Interface (CLI) for EasyDP Local PII Scanner.

Usage:
    easydp-scan scan [PATH] [--format html,json,cli] [--output-dir ./reports]
    easydp-scan tally [--port 9000]
"""

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)

from pii_scanner import __homepage__, __issues_url__, __version__
from pii_scanner.core.engine import ScannerEngine
from pii_scanner.core.logger import setup_scanner_logging
from pii_scanner.extractors.tally import TallyConnector
from pii_scanner.reporters.console import ConsoleReporter
from pii_scanner.reporters.html_rep import HTMLReporter
from pii_scanner.reporters.json_rep import JSONReporter


def configure_windows_terminal() -> None:
    """Ensure Windows terminal handles UTF-8 characters without cp1252 charmap crashes."""
    if sys.platform == "win32":
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="easydp-scan",
        description="EasyDP Local PII Scanner - Enterprise-grade, 100% offline DPDP compliance scanner.",
        epilog=f"Learn more at {__homepage__} | Powered by EasyDP.in",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"EasyDP Local PII Scanner v{__version__} ({__homepage__})",
    )
    parser.add_argument(
        "--report-error",
        "--report-issue",
        action="store_true",
        help="Open GitHub Issues page in your default browser to report an error or false positive",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Print the URL instead of launching the default browser (used with --report-error)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: scan
    scan_parser = subparsers.add_parser("scan", help="Scan local files and directories for PII")
    scan_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Target folder or file path to scan (default: current directory)",
    )
    scan_parser.add_argument(
        "-f",
        "--format",
        default="cli,html",
        help="Comma-separated output formats: cli, html, json (default: cli,html)",
    )
    scan_parser.add_argument(
        "-o",
        "--output-dir",
        default="./reports",
        help="Directory to save generated report files (default: ./reports)",
    )
    scan_parser.add_argument(
        "--log-file",
        default=None,
        help="Path to write detailed processing and troubleshooting logs (default: <output-dir>/scanner.log)",
    )
    scan_parser.add_argument(
        "-e",
        "--exclude",
        default="",
        help="Comma-separated path substrings to exclude from scan",
    )
    scan_parser.add_argument(
        "-u",
        "--user-dirs",
        action="store_true",
        help="Automatically scan standard user data folders (Desktop, Documents, Downloads, OneDrive)",
    )
    scan_parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress terminal summary output (useful for CI/CD pipelines)",
    )

    # Command: tally
    tally_parser = subparsers.add_parser(
        "tally", help="Scan local Tally ERP 9 / Prime ledger accounts"
    )
    tally_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Tally HTTP host (default: 127.0.0.1)",
    )
    tally_parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=9000,
        help="Tally HTTP port (default: 9000)",
    )
    tally_parser.add_argument(
        "-f",
        "--format",
        default="cli,html",
        help="Output formats: cli, html, json",
    )
    tally_parser.add_argument(
        "-o",
        "--output-dir",
        default="./reports",
        help="Directory to save reports",
    )
    tally_parser.add_argument(
        "--log-file",
        default=None,
        help="Path to write detailed processing and troubleshooting logs (default: <output-dir>/scanner.log)",
    )
    tally_parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress terminal output",
    )

    # Command: report-error
    report_parser = subparsers.add_parser(
        "report-error",
        help="Open GitHub Issues page to report a bug or false positive",
    )
    report_parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Print the URL instead of launching the default browser",
    )

    return parser


def print_completion_banner(
    console: Console,
    html_out: Path | None,
    json_out: Path | None,
    log_path: Path | None,
) -> None:
    """Print clickable report links and the EasyDP enterprise CTA banner."""
    console.print()
    if html_out and html_out.exists():
        html_uri = f"file://{html_out.resolve()}"
        console.print(
            f" [bold green]✔[/bold green] [bold]Interactive HTML Report:[/bold] [underline cyan][link={html_uri}]{html_uri}[/link][/underline cyan]"
        )
    if json_out and json_out.exists():
        json_uri = f"file://{json_out.resolve()}"
        console.print(
            f" [bold green]✔[/bold green] [bold]JSON Inventory Export:[/bold]  [underline cyan][link={json_uri}]{json_uri}[/link][/underline cyan]"
        )
    if log_path and log_path.exists():
        log_uri = f"file://{log_path.resolve()}"
        console.print(
            f" [bold green]✔[/bold green] [bold]Processing & Audit Log:[/bold] [underline cyan][link={log_uri}]{log_uri}[/link][/underline cyan]"
        )

    cta_content = (
        "[bold white]Ready to automate DPDP compliance, RoPA management & continuous data discovery?[/bold white]\n\n"
        "  🚀 [bold cyan]Sign up for the complete EasyDP Governance Platform:[/bold cyan]\n"
        "     [bold underline green][link=https://easydp.in]https://easydp.in[/link][/bold underline green]\n\n"
        "  [dim]• Automated Data Mapping & RoPA (Section 8)\n"
        "  • Continuous Database, Cloud & Endpoint Scanners\n"
        "  • Statutory DPDP Notice & Grievance Redressal[/dim]"
    )
    console.print()
    console.print(
        Panel(
            cta_content,
            title="[bold yellow]✨ EasyDP Enterprise Governance[/bold yellow]",
            border_style="cyan",
            padding=(1, 2),
        )
    )


def run_cli(args: list[str] | None = None) -> int:
    """Execute CLI parser with given arguments, returning exit code."""
    configure_windows_terminal()
    parser = create_parser()

    if args is None:
        args = sys.argv[1:]

    # Default to --help if no arguments provided
    if not args:
        parser.print_help()
        return 0

    try:
        parsed = parser.parse_args(args)
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 0

    if getattr(parsed, "report_error", False) or parsed.command == "report-error":
        no_browser = getattr(parsed, "no_browser", False)
        print(f"[EasyDP] GitHub Issues & Error Reporting: {__issues_url__}")
        if not no_browser:
            import webbrowser

            webbrowser.open(__issues_url__)
        return 0

    if parsed.command == "scan":
        from pii_scanner.core.engine import get_common_user_directories

        targets = [parsed.path]
        if parsed.user_dirs:
            detected_dirs = get_common_user_directories()
            if detected_dirs:
                targets = detected_dirs

        formats = [f.strip().lower() for f in parsed.format.split(",") if f.strip()]
        out_dir = Path(parsed.output_dir)
        excludes = [ex.strip() for ex in parsed.exclude.split(",") if ex.strip()]

        log_target = (
            Path(parsed.log_file) if getattr(parsed, "log_file", None) else out_dir / "scanner.log"
        )
        active_log_path = setup_scanner_logging(log_target)
        console = Console(safe_box=True)

        engine = ScannerEngine()
        summary = None

        if parsed.quiet:
            try:
                if len(targets) == 1:
                    summary = engine.scan_directory(targets[0], exclude_patterns=excludes)
                else:
                    summary = engine.scan_directories(targets, exclude_patterns=excludes)
            except Exception as e:
                print(f"[Error] Failed to scan {targets}: {e}", file=sys.stderr)
                return 1
        else:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold cyan]{task.description}[/bold cyan]"),
                BarColumn(bar_width=35),
                TaskProgressColumn(),
                MofNCompleteColumn(),
                TimeElapsedColumn(),
                console=console,
                transient=True,
            ) as progress:
                scan_task = None

                def on_progress(filename: str, current: int, total: int) -> None:
                    nonlocal scan_task
                    short_name = filename if len(filename) <= 28 else filename[:25] + "..."
                    if scan_task is None:
                        scan_task = progress.add_task(
                            f"Analyzing [bold]{short_name}[/bold]", total=total
                        )
                    progress.update(
                        scan_task,
                        completed=current,
                        description=f"Analyzing [bold]{short_name}[/bold]",
                    )

                try:
                    if len(targets) == 1:
                        summary = engine.scan_directory(
                            targets[0],
                            progress_callback=on_progress,
                            exclude_patterns=excludes,
                        )
                    else:
                        summary = engine.scan_directories(
                            targets,
                            progress_callback=on_progress,
                            exclude_patterns=excludes,
                        )
                except Exception as e:
                    print(f"[Error] Failed to scan {targets}: {e}", file=sys.stderr)
                    return 1

        # Output reporters
        if "cli" in formats and not parsed.quiet:
            ConsoleReporter(console=console).render_summary(summary)

        html_out: Path | None = None
        if "html" in formats:
            html_out = out_dir / "scan_report.html"
            HTMLReporter().save(summary, str(html_out))

        json_out: Path | None = None
        if "json" in formats:
            json_out = out_dir / "scan_report.json"
            JSONReporter().save(summary, str(json_out))

        if not parsed.quiet:
            print_completion_banner(console, html_out, json_out, active_log_path)

        return 0

    elif parsed.command == "tally":
        formats = [f.strip().lower() for f in parsed.format.split(",") if f.strip()]
        out_dir = Path(parsed.output_dir)

        log_target = (
            Path(parsed.log_file) if getattr(parsed, "log_file", None) else out_dir / "scanner.log"
        )
        active_log_path = setup_scanner_logging(log_target)
        console = Console(safe_box=True)

        connector = TallyConnector(host=parsed.host, port=parsed.port)
        result = connector.extract_ledgers()

        # Wrap in summary
        from datetime import datetime, timezone

        from pii_scanner.core.models import DataInventorySummary

        summary = DataInventorySummary(
            scanner_version=__version__,
            scan_timestamp=datetime.now(timezone.utc),
            target_path=f"http://{parsed.host}:{parsed.port} (Tally ERP)",
            total_files_scanned=1,
            total_sensitive_files=1 if result.is_sensitive else 0,
            total_clean_files=0 if result.is_sensitive else 1,
            total_pii_instances=result.findings_count,
            by_category={},
            by_type=result.findings_by_type,
            high_risk_files=[],
            stale_files_over_1y=0,
            stale_files_over_3y=0,
            results=[result],
        )

        if result.error_message:
            console.print(f"[EasyDP] Notice: {result.error_message}")

        if "cli" in formats and not parsed.quiet:
            ConsoleReporter(console=console).render_summary(summary)

        html_out: Path | None = None
        if "html" in formats:
            html_out = out_dir / "tally_report.html"
            HTMLReporter().save(summary, str(html_out))

        json_out: Path | None = None
        if "json" in formats:
            json_out = out_dir / "tally_report.json"
            JSONReporter().save(summary, str(json_out))

        if not parsed.quiet:
            print_completion_banner(console, html_out, json_out, active_log_path)

        return 0

    else:
        parser.print_help()
        return 0


def main() -> None:
    """Standard console script entrypoint."""
    sys.exit(run_cli())


if __name__ == "__main__":
    main()
