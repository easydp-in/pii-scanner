"""Structured JSON reporter conforming to DPDP Data Inventory schema."""

import json
from dataclasses import asdict
from pathlib import Path

from pii_scanner import __homepage__, __version__
from pii_scanner.core.models import DataInventorySummary


class JSONReporter:
    """Generates machine-readable JSON inventory exports for compliance pipelines."""

    def to_dict(self, summary: DataInventorySummary) -> dict:
        """Serialize DataInventorySummary into an EasyDP-standard JSON dictionary."""
        data = asdict(summary)
        data["scan_timestamp"] = summary.scan_timestamp.isoformat()
        # Convert datetime in individual results
        for r in data["results"]:
            if "modified_time" in r and hasattr(r["modified_time"], "isoformat"):
                r["modified_time"] = r["modified_time"].isoformat()
            elif "modified_time" in r:
                r["modified_time"] = str(r["modified_time"])

        return {
            "@context": "https://easydp.in/schema/v1/pii-inventory.json",
            "generator": f"EasyDP Local PII Scanner v{__version__} ({__homepage__})",
            "legal_disclaimer": (
                "This document is an automated technical data inventory generated for privacy governance "
                "under the Digital Personal Data Protection (DPDP) Act, 2023. It does not constitute legal "
                "advice or statutory audit certification. Scans ran 100% locally with zero remote data egress."
            ),
            "data_ownership_inventory": {
                "target_path": summary.target_path,
                "scan_timestamp": summary.scan_timestamp.isoformat(),
                "total_files_scanned": summary.total_files_scanned,
                "total_sensitive_files": summary.total_sensitive_files,
                "total_clean_files": summary.total_clean_files,
                "total_pii_instances": summary.total_pii_instances,
                "by_category": summary.by_category,
                "by_type": summary.by_type,
                "high_risk_files": summary.high_risk_files,
                "retention_staleness": {
                    "files_over_1_year": summary.stale_files_over_1y,
                    "files_over_3_years": summary.stale_files_over_3y,
                },
            },
            "findings": data["results"],
        }

    def save(self, summary: DataInventorySummary, output_path: str) -> None:
        """Write formatted JSON to target file path."""
        payload = self.to_dict(summary)
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, mode="w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
