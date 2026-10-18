"""Core orchestration engine for local file discovery, routing, and PII inventory aggregation."""

import os
from collections import defaultdict
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

from pii_scanner import __version__
from pii_scanner.core.models import (
    DataInventorySummary,
    FileScanResult,
    PIIType,
)
from pii_scanner.extractors.base import BaseExtractor
from pii_scanner.extractors.csv_scanner import CSVExtractor
from pii_scanner.extractors.excel_scanner import ExcelExtractor
from pii_scanner.extractors.text_scanner import TextExtractor

DEFAULT_IGNORED_DIRS = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "dist",
    "build",
    ".idea",
    ".vscode",
}

DEFAULT_SUPPORTED_EXTENSIONS = {
    ".csv": CSVExtractor,
    ".xlsx": ExcelExtractor,
    ".xlsm": ExcelExtractor,
    ".txt": TextExtractor,
    ".log": TextExtractor,
    ".md": TextExtractor,
    ".tsv": CSVExtractor,
    ".json": TextExtractor,
    ".xml": TextExtractor,
    ".sql": TextExtractor,
    ".yaml": TextExtractor,
    ".yml": TextExtractor,
}


class ScannerEngine:
    """Discovers, scans, and aggregates data ownership & PII inventory metrics."""

    def __init__(
        self,
        ignored_dirs: set[str] | None = None,
        custom_extractors: dict[str, type[BaseExtractor]] | None = None,
    ) -> None:
        self.ignored_dirs = set(ignored_dirs) if ignored_dirs is not None else DEFAULT_IGNORED_DIRS
        self.extractors_map: dict[str, BaseExtractor] = {}

        # Instantiate extractors
        mapping = custom_extractors or DEFAULT_SUPPORTED_EXTENSIONS
        for ext, ext_cls in mapping.items():
            self.extractors_map[ext.lower()] = ext_cls()

    def scan_directory(
        self,
        target_path: str,
        progress_callback: Callable[[str, int, int], None] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> DataInventorySummary:
        """Recursively scan a path and compile a comprehensive DPDP data inventory summary."""
        target = Path(target_path).resolve()
        if not target.exists():
            raise FileNotFoundError(f"Target path does not exist: {target_path}")

        files_to_scan: list[Path] = []
        if target.is_file():
            files_to_scan.append(target)
        else:
            for root, dirs, files in os.walk(target):
                # Filter out ignored directories in-place
                dirs[:] = [d for d in dirs if d not in self.ignored_dirs and not d.startswith(".")]

                for f in files:
                    ext = Path(f).suffix.lower()
                    if ext in self.extractors_map:
                        full_p = Path(root) / f
                        if exclude_patterns:
                            if any(pattern in str(full_p) for pattern in exclude_patterns):
                                continue
                        files_to_scan.append(full_p)

        total_files = len(files_to_scan)
        results: list[FileScanResult] = []
        by_category: dict[str, int] = defaultdict(int)
        by_type: dict[str, int] = defaultdict(int)
        high_risk_files: list[str] = []
        stale_1y = 0
        stale_3y = 0

        now = datetime.now()
        for idx, file_p in enumerate(files_to_scan, start=1):
            if progress_callback:
                progress_callback(file_p.name, idx, total_files)

            ext = file_p.suffix.lower()
            extractor = self.extractors_map.get(ext)
            if not extractor:
                continue

            scan_res = extractor.extract(str(file_p))
            results.append(scan_res)

            # Check staleness
            days_old = (now - scan_res.modified_time).days
            if days_old > 365 * 3:
                stale_3y += 1
            elif days_old > 365:
                stale_1y += 1

            if scan_res.is_sensitive:
                # Accumulate type and category counts
                for pii_type_str, count in scan_res.findings_by_type.items():
                    by_type[pii_type_str] += count
                    # Map to category
                    for pt in PIIType:
                        if pt.value == pii_type_str:
                            by_category[pt.category.value] += count
                            break

                # High risk identification: Downloads/Desktop or dense findings
                path_str = str(file_p)
                if (
                    "download" in path_str.lower()
                    or "desktop" in path_str.lower()
                    or scan_res.findings_count >= 5
                ):
                    high_risk_files.append(str(file_p))

        sensitive_count = sum(1 for r in results if r.is_sensitive)
        total_pii = sum(by_type.values())

        return DataInventorySummary(
            scanner_version=__version__,
            scan_timestamp=datetime.now(timezone.utc),
            target_path=str(target),
            total_files_scanned=total_files,
            total_sensitive_files=sensitive_count,
            total_clean_files=total_files - sensitive_count,
            total_pii_instances=total_pii,
            by_category=dict(by_category),
            by_type=dict(by_type),
            high_risk_files=high_risk_files,
            stale_files_over_1y=stale_1y,
            stale_files_over_3y=stale_3y,
            results=results,
        )
