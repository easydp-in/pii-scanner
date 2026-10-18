"""Standalone interactive HTML report generator with official EasyDP branding."""

from html import escape
from pathlib import Path

from pii_scanner import __guides_url__, __homepage__, __issues_url__, __version__
from pii_scanner.core.models import DataInventorySummary

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EasyDP Local PII Scanner — Data Inventory Report</title>
    <style>
        :root {
            --navy: #102338;
            --navy-2: #0B1928;
            --navy-card: #16293F;
            --navy-line: #1D3350;
            --gold: #D4A945;
            --gold-hover: #E5BE5E;
            --gold-deep: #B98A2E;
            --bg: #F5F7FA;
            --card-bg: #FFFFFF;
            --text-main: #14202E;
            --text-muted: #5C6B80;
            --border: #E5E9F0;
            --danger: #B23B27;
            --danger-bg: #FCEEEC;
            --warning: #B98A2E;
            --warning-bg: #F8F1E1;
            --success: #17754F;
            --success-bg: #E7F4EE;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
        body { background-color: var(--bg); color: var(--text-main); line-height: 1.5; padding-bottom: 60px; }
        .header { background: var(--navy); color: #EEF2F8; padding: 24px 32px; border-bottom: 3px solid var(--gold); box-shadow: 0 4px 12px rgba(16, 35, 56, 0.15); }
        .header-content { max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; }
        .logo-box { display: flex; align-items: center; gap: 12px; }
        .brand-name { font-size: 24px; font-weight: 700; letter-spacing: -0.4px; color: #FFFFFF; }
        .brand-name span { color: var(--gold); }
        .tagline { font-size: 12.5px; color: #A9B8CF; }
        .header-badges { display: flex; gap: 10px; align-items: center; }
        .badge { display: inline-flex; align-items: center; padding: 4px 12px; border-radius: 9999px; font-size: 12px; font-weight: 600; }
        .badge-offline { background: rgba(23, 117, 79, 0.2); color: #34C77B; border: 1px solid #17754F; }
        .badge-version { background: rgba(212, 169, 69, 0.15); color: var(--gold); border: 1px solid var(--gold); }

        .container { max-width: 1200px; margin: 28px auto; padding: 0 20px; }

        .alert-disclaimer { background-color: var(--warning-bg); border-left: 4px solid var(--gold-deep); padding: 16px 20px; border-radius: 6px; margin-bottom: 24px; }
        .alert-disclaimer h4 { color: #8A6516; font-size: 14px; font-weight: 700; display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
        .alert-disclaimer p { color: #5C450E; font-size: 13px; }

        .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-bottom: 28px; }
        .kpi-card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .kpi-title { font-size: 13px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
        .kpi-value { font-size: 32px; font-weight: 800; line-height: 1; }
        .kpi-sub { font-size: 12px; color: var(--text-muted); margin-top: 8px; }
        .val-danger { color: var(--danger); }
        .val-success { color: var(--success); }
        .val-primary { color: var(--navy); }
        .val-warning { color: var(--gold-deep); }

        .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-bottom: 28px; }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; flex-wrap: wrap; gap: 12px; }
        .card-title { font-size: 18px; font-weight: 700; color: var(--text-main); display: flex; align-items: center; gap: 8px; }

        .chart-row { display: flex; align-items: center; margin-bottom: 14px; }
        .chart-label { width: 180px; font-size: 13px; font-weight: 600; color: var(--text-main); }
        .chart-bar-bg { flex: 1; background: #E5E9F0; height: 16px; border-radius: 8px; overflow: hidden; margin: 0 12px; }
        .chart-bar-fill { height: 100%; border-radius: 8px; background: var(--navy); }
        .chart-count { width: 80px; font-size: 13px; font-weight: 700; text-align: right; color: var(--text-main); }

        .filter-bar { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
        .search-box { flex: 1; min-width: 240px; padding: 10px 14px; border: 1px solid var(--border); border-radius: 8px; font-size: 14px; }
        .search-box:focus { outline: none; border-color: var(--navy); box-shadow: 0 0 0 3px rgba(16, 35, 56, 0.15); }

        table { width: 100%; border-collapse: collapse; text-align: left; font-size: 14px; }
        th { background: #F1F5F9; padding: 12px 16px; font-weight: 600; color: var(--text-muted); border-bottom: 2px solid var(--border); }
        td { padding: 14px 16px; border-bottom: 1px solid var(--border); vertical-align: top; }
        tr:hover td { background-color: #F8FAFC; }
        .pill { display: inline-block; padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 600; margin: 2px 2px 2px 0; }
        .pill-aadhaar { background: #FBF3E2; color: #8A6516; border: 1px solid #E9D9B0; }
        .pill-pan { background: #E7F4EE; color: #17754F; border: 1px solid #B8E0CD; }
        .pill-gstin { background: #F8F1E1; color: #8A6516; border: 1px solid #E5D5A8; }
        .pill-phone { background: #F1F5F9; color: #46566B; border: 1px solid #CBD5E1; }
        .pill-email { background: #F1F5F9; color: #46566B; border: 1px solid #CBD5E1; }
        .pill-risk { background: var(--danger-bg); color: var(--danger); font-weight: 700; border: 1px solid #FECACA; }

        .masked-preview { font-family: monospace; font-size: 12px; background: #F1F5F9; padding: 2px 6px; border-radius: 4px; color: #334155; }
        .footer { text-align: center; margin-top: 40px; color: var(--text-muted); font-size: 13px; }
        .footer a { color: var(--gold-ink); text-decoration: none; font-weight: 600; }
    </style>
</head>
<body>

    <header class="header">
        <div class="header-content">
            <div class="logo-box">
                <svg width="38" height="38" viewBox="788 680 442 538" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" style="display:block; flex-shrink: 0;">
                    <path fill="#FFFFFF" d="M 1008.28 685.028 C 1018.41 690.524 1035.03 703.143 1046.2 710.048 C 1076.83 729.232 1109.68 744.621 1144.03 755.874 C 1157.71 760.522 1171.7 764.205 1185.9 766.896 C 1196.43 768.943 1207.05 770.559 1217.42 773.265 C 1223.95 774.674 1223.94 786.419 1224.25 792.065 C 1229.24 882.182 1220.1 977.57 1176 1057.86 C 1146.93 1110.77 1106.27 1152.82 1055.29 1184.83 C 1041.28 1193.63 1024.34 1203.56 1008.98 1209.21 C 992.194 1203.35 978.148 1195.11 963.114 1185.71 C 908.881 1151.79 865.755 1106.42 836.424 1049.33 C 832.552 1041.8 826.866 1031.48 829.611 1023.31 C 831.705 1020.93 839.376 1017.3 841.325 1019.76 C 850.306 1031.1 856.141 1045.9 863.512 1058.65 C 867.754 1065.93 872.306 1073.04 877.155 1079.94 C 909.686 1126.69 957.374 1165.26 1009 1189.25 C 1055.8 1164.72 1087.68 1142.69 1123.23 1102 C 1195.1 1019.77 1213.88 895.883 1205.41 789.704 C 1194.29 786.956 1181.34 785.306 1168.91 782.212 C 1124.35 771.4 1081.7 753.828 1042.45 730.107 C 1033.26 724.505 1016.88 714.701 1009.46 707.454 C 994.459 715.485 976.56 729.294 960.148 738.501 C 923.26 758.908 883.707 774.073 842.632 783.558 C 831.782 786.141 821.894 787.474 811.229 789.811 L 810.973 796.615 C 809.868 827.179 809.258 941.883 829.13 961.755 C 839.458 972.082 900.755 968.598 917.994 968.7 C 917.982 974.73 917.859 981.159 918.004 987.157 C 893.245 986.392 864.745 990.353 840.566 986.339 C 827.918 984.239 816.728 978.105 809.416 967.385 C 792.936 943.225 787.32 811.172 794.09 779.38 C 794.421 777.826 795.092 775.269 796.43 774.297 C 798.24 772.983 855.717 761.37 864.993 758.596 C 904.206 746.868 941.913 728.478 976.424 706.619 C 987.288 699.737 997.523 692.036 1008.28 685.028 z"/>
                    <path fill="#D4A945" d="M 945.975 887.498 C 945.157 861.946 943.564 838.955 962.345 818.743 C 973.725 806.412 989.581 799.169 1006.35 798.64 C 1023.37 798.075 1039.89 804.371 1052.22 816.112 C 1067.25 830.434 1070.84 846.88 1071.14 866.579 C 1071.18 873.574 1071.16 880.569 1071.05 887.563 C 1102.91 889.212 1098.9 914.461 1098.92 938.165 C 1098.94 950.4 1098.99 962.663 1098.71 974.886 C 1098.64 977.69 1096.61 980.711 1094.27 982.113 C 1092 983.479 1089.25 983.778 1086.75 982.93 C 1073.66 978.384 1086.9 919.883 1078.04 909.111 C 1074.67 905.013 1031.01 906.192 1024.85 906.418 C 996.211 907.468 967.226 903.636 939.526 908.455 C 934.637 909.342 936.043 949.567 935.95 955.792 L 918.141 955.3 C 917.742 928.381 909.76 890.088 945.975 887.498 z M 1052.86 887.447 C 1052.89 867.099 1055.28 846.97 1040.33 831.209 C 1032.21 822.632 1020.99 817.666 1009.18 817.42 C 997.38 817.242 985.996 821.776 977.55 830.016 C 961.788 845.626 964.346 866.905 964.233 887.677 C 985.135 887.894 1033.03 889.015 1052.86 887.447 z"/>
                    <path fill="#FFFFFF" d="M 945.975 887.498 C 945.157 861.946 943.564 838.955 962.345 818.743 C 973.725 806.412 989.581 799.169 1006.35 798.64 C 1023.37 798.075 1039.89 804.371 1052.22 816.112 C 1067.25 830.434 1070.84 846.88 1071.14 866.579 C 1071.18 873.574 1071.16 880.569 1071.05 887.563 L 1052.86 887.447 C 1052.89 867.099 1055.28 846.97 1040.33 831.209 C 1032.21 822.632 1020.99 817.666 1009.18 817.42 C 997.38 817.242 985.996 821.776 977.55 830.016 C 961.788 845.626 964.346 866.905 964.233 887.677 C 959.303 887.327 951.152 887.533 945.975 887.498 z"/>
                    <path fill="#D4A945" d="M 918.088 1000.12 L 936.022 999.898 C 936.231 1011.81 934.33 1037.77 938.568 1046.77 C 946.668 1054.8 1015.59 1048.85 1031.92 1050.65 C 1041.34 1051.69 1071.07 1051.66 1078.58 1046.94 C 1082.27 1041.63 1081 1024.79 1080.92 1017.63 C 1086.62 1017.9 1093.13 1017.82 1098.9 1017.88 L 1098.95 1034.59 C 1099.21 1057.56 1092.41 1068.39 1068.3 1068.66 C 1034.89 1069.34 1000.74 1068.39 967.457 1068.76 C 935.211 1069.12 916.375 1070.34 917.852 1030 C 918.173 1021.23 918.004 1009.3 918.088 1000.12 z"/>
                    <path fill="#D4A945" d="M 917.994 968.7 C 940.192 967.821 962.678 968.708 984.91 968.676 C 1001.14 968.653 1018.37 967.437 1034.51 968.757 C 1037.14 968.971 1039.75 969.215 1041.78 971.102 C 1043.58 972.776 1044.96 975.481 1044.94 978.008 C 1044.93 981.021 1043.57 983.907 1040.96 985.568 C 1034.96 989.379 933.041 987.176 918.004 987.157 C 917.859 981.159 917.982 974.73 917.994 968.7 z"/>
                </svg>
                <div>
                    <div class="brand-name">Easy<span style="color:#D4A945;">DP</span></div>
                    <div class="tagline">Local PII Scanner &amp; Data Inventory Dashboard</div>
                </div>
            </div>
            <div class="header-badges">
                <a href="__GUIDES_URL__" target="_blank" class="badge" style="background:rgba(212, 169, 69, 0.15);color:var(--gold);text-decoration:none;border:1px solid var(--gold);">📚 Free Checklists &amp; Guides</a>
                <span class="badge badge-offline">🔒 100% Offline (Zero Cloud Egress)</span>
                <span class="badge badge-version">v__VERSION__</span>
                <a href="__ISSUES_URL__" target="_blank" class="badge" style="background:#16293F;color:#E9776B;text-decoration:none;border:1px solid rgba(233, 119, 107, 0.4);">🐞 Report Error</a>
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
            📚 <a href="__GUIDES_URL__" target="_blank" style="color:var(--gold-deep); font-weight: 600;">Free DPDP Compliance Checklists &amp; Guides</a> • Scan Timestamp: __SCAN_TIMESTAMP__ UTC • <a href="__ISSUES_URL__" target="_blank">Report Error / Issue on GitHub</a>
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
            .replace("__ISSUES_URL__", str(__issues_url__))
            .replace("__GUIDES_URL__", str(__guides_url__))
            .replace("__SCAN_TIMESTAMP__", summary.scan_timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        )

    def save(self, summary: DataInventorySummary, output_path: str) -> None:
        """Write formatted HTML dashboard to target file path."""
        content = self.render(summary)
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
