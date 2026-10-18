"""Standalone interactive HTML report generator with official EasyDP branding."""

from html import escape
from pathlib import Path

from pii_scanner import __homepage__, __version__
from pii_scanner.core.models import DataInventorySummary

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EasyDP Local PII Scanner — Data Inventory Report</title>
    <style>
        :root {
            --primary: #1E3A8A;
            --primary-light: #3B82F6;
            --accent: #0EA5E9;
            --bg: #F8FAFC;
            --card-bg: #FFFFFF;
            --text-main: #0F172A;
            --text-muted: #64748B;
            --border: #E2E8F0;
            --danger: #EF4444;
            --danger-bg: #FEF2F2;
            --warning: #F59E0B;
            --warning-bg: #FFFBEB;
            --success: #10B981;
            --success-bg: #ECFDF5;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
        body { background-color: var(--bg); color: var(--text-main); line-height: 1.5; padding-bottom: 60px; }
        .header { background: linear-gradient(135deg, #1E3A8A 0%, #1E40AF 100%); color: white; padding: 24px 32px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
        .header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; }
        .logo-box { display: flex; align-items: center; gap: 12px; }
        .logo-icon { width: 40px; height: 40px; background: white; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 800; color: var(--primary); font-size: 20px; }
        .brand-name { font-size: 24px; font-weight: 700; letter-spacing: -0.5px; }
        .brand-name span { color: #60A5FA; }
        .tagline { font-size: 13px; color: #BFDBFE; }
        .header-badges { display: flex; gap: 10px; align-items: center; }
        .badge { display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; }
        .badge-offline { background: rgba(16, 185, 129, 0.2); color: #A7F3D0; border: 1px solid #059669; }
        .badge-version { background: rgba(255, 255, 255, 0.15); color: white; }

        .container { max-width: 1200px; margin: 28px auto; padding: 0 20px; }

        .alert-disclaimer { background-color: var(--warning-bg); border-left: 4px solid var(--warning); padding: 16px 20px; border-radius: 6px; margin-bottom: 24px; }
        .alert-disclaimer h4 { color: #92400E; font-size: 14px; font-weight: 700; display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
        .alert-disclaimer p { color: #78350F; font-size: 13px; }

        .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-bottom: 28px; }
        .kpi-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .kpi-title { font-size: 13px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
        .kpi-value { font-size: 32px; font-weight: 800; line-height: 1; }
        .kpi-sub { font-size: 12px; color: var(--text-muted); margin-top: 8px; }
        .val-danger { color: var(--danger); }
        .val-success { color: var(--success); }
        .val-primary { color: var(--primary-light); }
        .val-warning { color: var(--warning); }

        .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 28px; }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
        .card-title { font-size: 18px; font-weight: 700; color: var(--text-main); display: flex; align-items: center; gap: 8px; }

        .chart-row { display: flex; align-items: center; margin-bottom: 14px; }
        .chart-label { width: 180px; font-size: 13px; font-weight: 600; color: var(--text-main); }
        .chart-bar-bg { flex: 1; background: #E2E8F0; height: 16px; border-radius: 8px; overflow: hidden; margin: 0 12px; }
        .chart-bar-fill { height: 100%; border-radius: 8px; background: linear-gradient(90deg, #3B82F6, #1D4ED8); }
        .chart-count { width: 80px; font-size: 13px; font-weight: 700; text-align: right; color: var(--text-main); }

        .filter-bar { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
        .search-box { flex: 1; min-width: 240px; padding: 10px 14px; border: 1px solid var(--border); border-radius: 8px; font-size: 14px; }
        .search-box:focus { outline: none; border-color: var(--primary-light); box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2); }

        table { width: 100%; border-collapse: collapse; text-align: left; font-size: 14px; }
        th { background: #F1F5F9; padding: 12px 16px; font-weight: 600; color: var(--text-muted); border-bottom: 2px solid var(--border); }
        td { padding: 14px 16px; border-bottom: 1px solid var(--border); vertical-align: top; }
        tr:hover td { background-color: #F8FAFC; }
        .pill { display: inline-block; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 600; margin: 2px 2px 2px 0; }
        .pill-aadhaar { background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
        .pill-pan { background: #F5F3FF; color: #6D28D9; border: 1px solid #DDD6FE; }
        .pill-gstin { background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
        .pill-phone { background: #FEF3C7; color: #B45309; border: 1px solid #FDE68A; }
        .pill-email { background: #F3F4F6; color: #374151; border: 1px solid #E5E7EB; }
        .pill-risk { background: var(--danger-bg); color: var(--danger); font-weight: 700; border: 1px solid #FECACA; }

        .masked-preview { font-family: monospace; font-size: 12px; background: #F1F5F9; padding: 2px 6px; border-radius: 4px; color: #334155; }
        .footer { text-align: center; margin-top: 40px; color: var(--text-muted); font-size: 13px; }
        .footer a { color: var(--primary-light); text-decoration: none; font-weight: 600; }
    </style>
</head>
<body>

    <header class="header">
        <div class="header-content">
            <div class="logo-box">
                <div class="logo-icon">E</div>
                <div>
                    <div class="brand-name">EasyDP<span>.in</span></div>
                    <div class="tagline">Local PII Scanner & Data Inventory Dashboard</div>
                </div>
            </div>
            <div class="header-badges">
                <span class="badge badge-offline">🔒 100% Offline (Zero Cloud Egress)</span>
                <span class="badge badge-version">v__VERSION__</span>
            </div>
        </div>
    </header>

    <div class="container">

        <div class="alert-disclaimer">
            <h4>⚠️ LEGAL &amp; COMPLIANCE DISCLAIMER</h4>
            <p>
                This automated data inventory was produced locally on this machine to assist with internal privacy governance
                under India's Digital Personal Data Protection (DPDP) Act, 2023. It does not constitute formal legal counsel or statutory audit certification.
                In compliance with the Aadhaar Act and privacy principles, all sensitive numbers are strictly masked.
            </p>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Total Files Scanned</div>
                <div class="kpi-value val-primary">__TOTAL_FILES__</div>
                <div class="kpi-sub">Target: __TARGET_PATH__</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Sensitive Files Detected</div>
                <div class="kpi-value val-danger">__SENSITIVE_FILES__</div>
                <div class="kpi-sub">__CLEAN_FILES__ clean files without personal data</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Total PII Instances</div>
                <div class="kpi-value val-warning">__TOTAL_PII__</div>
                <div class="kpi-sub">Verified via statutory checksums &amp; rules</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Retention Risk (&gt;1 Year)</div>
                <div class="kpi-value">__STALE_FILES__</div>
                <div class="kpi-sub">__STALE_3Y__ files older than 3 years</div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h3 class="card-title">📊 Data Ownership &amp; PII Inventory by Type</h3>
                <span style="font-size: 13px; color: var(--text-muted);">Surfacing what personal data your organization holds</span>
            </div>
            <div id="chartContainer">
                __CHART_ROWS__
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h3 class="card-title">📁 Sensitive Files &amp; Location Registry</h3>
                <input type="text" id="searchInput" class="search-box" placeholder="Filter by file name or data type..." onkeyup="filterTable()">
            </div>
            <table id="filesTable">
                <thead>
                    <tr>
                        <th>File Name &amp; Path</th>
                        <th>PII Count</th>
                        <th>Detected Data Types</th>
                        <th>Sample Masked Findings</th>
                    </tr>
                </thead>
                <tbody>
                    __TABLE_ROWS__
                </tbody>
            </table>
        </div>

        <div class="footer">
            Generated locally by <a href="__HOMEPAGE__" target="_blank">EasyDP.in</a> — India's Data Protection &amp; DPDP Compliance Platform.<br>
            Scan Timestamp: __SCAN_TIMESTAMP__ UTC
        </div>

    </div>

    <script>
        function filterTable() {
            var input = document.getElementById("searchInput");
            var filter = input.value.toLowerCase();
            var rows = document.getElementById("filesTable").getElementsByTagName("tr");
            for (var i = 1; i < rows.length; i++) {
                var rowText = rows[i].innerText.toLowerCase();
                rows[i].style.display = rowText.includes(filter) ? "" : "none";
            }
        }
    </script>
</body>
</html>
"""


class HTMLReporter:
    """Generates a modern, interactive, offline HTML report with EasyDP branding."""

    def render(self, summary: DataInventorySummary) -> str:
        """Render the complete HTML document as a string."""
        # 1. Build chart rows
        chart_rows: list[str] = []
        total_pii = max(summary.total_pii_instances, 1)
        for pii_type, count in sorted(summary.by_type.items(), key=lambda x: x[1], reverse=True):
            pct = max(min(int((count / total_pii) * 100), 100), 4)
            chart_rows.append(f"""
                <div class="chart-row">
                    <div class="chart-label">{escape(pii_type)}</div>
                    <div class="chart-bar-bg">
                        <div class="chart-bar-fill" style="width: {pct}%;"></div>
                    </div>
                    <div class="chart-count">{count:,} ({pct}%)</div>
                </div>
            """)
        chart_html = (
            "".join(chart_rows) if chart_rows else "<p style='color:#64748B;'>No PII detected.</p>"
        )

        # 2. Build table rows
        table_rows: list[str] = []
        sensitive_files = [r for r in summary.results if r.is_sensitive]
        for r in sensitive_files:
            # Pills for types
            pills = []
            for t_name, t_cnt in r.findings_by_type.items():
                pills.append(f"<span class='pill pill-aadhaar'>{escape(t_name)}: {t_cnt}</span>")
            if "download" in r.file_path.lower() or "desktop" in r.file_path.lower():
                pills.append("<span class='pill pill-risk'>⚠️ High-Risk Folder</span>")
            pills_html = "".join(pills)

            # Sample masked values
            samples = []
            for f in r.sample_findings[:3]:
                samples.append(f"<span class='masked-preview'>{escape(f.masked_value)}</span>")
            samples_html = " ".join(samples)

            table_rows.append(f"""
                <tr>
                    <td>
                        <strong>{escape(r.file_name)}</strong><br>
                        <span style="font-size: 11px; color: #64748B;">{escape(r.file_path)}</span>
                    </td>
                    <td><strong>{r.findings_count}</strong></td>
                    <td>{pills_html}</td>
                    <td>{samples_html}</td>
                </tr>
            """)
        table_html = (
            "".join(table_rows)
            if table_rows
            else "<tr><td colspan='4' style='text-align:center;'>No sensitive files detected. All scanned files are clean.</td></tr>"
        )

        return (
            HTML_TEMPLATE.replace("__VERSION__", str(__version__))
            .replace("__HOMEPAGE__", str(__homepage__))
            .replace("__TOTAL_FILES__", str(summary.total_files_scanned))
            .replace("__SENSITIVE_FILES__", str(summary.total_sensitive_files))
            .replace("__CLEAN_FILES__", str(summary.total_clean_files))
            .replace("__TOTAL_PII__", str(summary.total_pii_instances))
            .replace("__TARGET_PATH__", escape(summary.target_path))
            .replace("__STALE_FILES__", str(summary.stale_files_over_1y))
            .replace("__STALE_3Y__", str(summary.stale_files_over_3y))
            .replace("__CHART_ROWS__", chart_html)
            .replace("__TABLE_ROWS__", table_html)
            .replace("__SCAN_TIMESTAMP__", summary.scan_timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        )

    def save(self, summary: DataInventorySummary, output_path: str) -> None:
        """Write formatted HTML dashboard to target file path."""
        content = self.render(summary)
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
