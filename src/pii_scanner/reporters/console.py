"""Rich console reporter with EasyDP branding, legal disclaimer, and inventory tables."""

from io import StringIO

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from pii_scanner.core.models import DataInventorySummary

EASYDP_BANNER = """[bold cyan]
  ______                     _____  _____
 |  ____|                   |  __ \\|  __ \\
 | |__   __ _ ___ _   _     | |  | | |__) |
 |  __| / _` / __| | | |    | |  | |  ___/
 | |___| (_| \\__ \\ |_| |    | |__| | |
 |______\\__,_|___/\\__, |    |_____/|_|
                   __/ |  .in
                  |___/   Local PII Scanner
[/bold cyan]
[bold]EasyDP Local PII Scanner[/bold]
[dim]Enterprise-grade, 100% offline DPDP compliance scanner | [underline]https://easydp.in[/underline][/dim]
"""

DISCLAIMER_TEXT = """[bold yellow][!] LEGAL & COMPLIANCE DISCLAIMER[/bold yellow]
[dim]1. NOT LEGAL ADVICE: This automated scanner assists with information governance under India's
   DPDP Act, 2023. It does not constitute legal counsel or a statutory compliance audit.
2. USER AUTHORIZATION: The operator certifies lawful authority to scan target paths.
3. PRIVACY GUARANTEE: Scans run 100% locally. Zero raw personal data ever leaves this PC.
4. MASKING: All sensitive values (Aadhaar, PAN, etc.) are strictly masked in reports.[/dim]"""


class ConsoleReporter:
    """Renders formatted terminal output using Rich with EasyDP branding."""

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console(safe_box=True)

    def render_summary(self, summary: DataInventorySummary) -> str:
        """Render complete summary to string (for testing and logging) and prints it."""
        buf = StringIO()
        render_console = Console(file=buf, force_terminal=False, color_system=None, safe_box=True)

        # 1. EasyDP Banner & Disclaimer
        render_console.print(EASYDP_BANNER)
        render_console.print(Panel(DISCLAIMER_TEXT, border_style="yellow"))

        # 2. Key Metrics Overview Table
        overview_table = Table(title="Scan Overview & DPDP Metrics", border_style="cyan")
        overview_table.add_column("Metric", style="bold")
        overview_table.add_column("Value", style="green")

        overview_table.add_row("Target Path", summary.target_path)
        overview_table.add_row(
            "Scan Timestamp (UTC)", summary.scan_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        )
        overview_table.add_row("Total Files Scanned", str(summary.total_files_scanned))
        overview_table.add_row(
            "Sensitive Files Identified",
            f"[bold red]{summary.total_sensitive_files}[/bold red]"
            if summary.total_sensitive_files > 0
            else "0",
        )
        overview_table.add_row("Clean Files", str(summary.total_clean_files))
        overview_table.add_row("Total Sensitive PII Instances", str(summary.total_pii_instances))
        overview_table.add_row("High-Risk Exposure Files", str(len(summary.high_risk_files)))
        overview_table.add_row("Retention Alert (>1y old)", str(summary.stale_files_over_1y))
        overview_table.add_row("Retention Alert (>3y old)", str(summary.stale_files_over_3y))

        render_console.print(overview_table)

        # 3. Data Ownership Breakdown by Type
        if summary.by_type:
            types_table = Table(
                title="Data Ownership Breakdown (Types & Quantities)", border_style="blue"
            )
            types_table.add_column("PII Data Type", style="bold")
            types_table.add_column("Quantity Found", justify="right")
            types_table.add_column("Share of Total", justify="right")

            total_pii = max(summary.total_pii_instances, 1)
            for pii_type, count in sorted(
                summary.by_type.items(), key=lambda x: x[1], reverse=True
            ):
                share = (count / total_pii) * 100
                types_table.add_row(pii_type, str(count), f"{share:.1f}%")

            render_console.print(types_table)

        # 4. Sensitive Files Table
        sensitive_results = [r for r in summary.results if r.is_sensitive]
        if sensitive_results:
            files_table = Table(
                title="Sensitive Files & Findings Details", border_style="magenta"
            )
            files_table.add_column("File Name", style="bold")
            files_table.add_column("PII Count", justify="right")
            files_table.add_column("Findings Breakdown")
            files_table.add_column("Sample Masked Values")

            for res in sensitive_results[:20]:  # Top 20 in terminal
                breakdown = ", ".join(f"{k}: {v}" for k, v in res.findings_by_type.items())
                sample_str = ", ".join(f.masked_value for f in res.sample_findings[:3])
                files_table.add_row(res.file_name, str(res.findings_count), breakdown, sample_str)

            render_console.print(files_table)

        output_str = buf.getvalue()
        # Also print directly to user console
        self.console.print(EASYDP_BANNER)
        self.console.print(Panel(DISCLAIMER_TEXT, border_style="yellow"))
        self.console.print(overview_table)
        if summary.by_type:
            self.console.print(types_table)
        if sensitive_results:
            self.console.print(files_table)

        return output_str
