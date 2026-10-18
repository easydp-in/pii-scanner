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
from pii_scanner.extractors.docx_scanner import DocxExtractor
from pii_scanner.extractors.excel_scanner import ExcelExtractor
from pii_scanner.extractors.odt_scanner import ODTExtractor
from pii_scanner.extractors.pdf_scanner import PDFExtractor
from pii_scanner.extractors.rtf_scanner import RTFExtractor
from pii_scanner.extractors.text_scanner import TextExtractor

DEFAULT_IGNORED_DIRS = {
    # Developer & Build Artifacts
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
    # OS System Directories (for whole-drive scans)
    "Windows",
    "Program Files",
    "Program Files (x86)",
    "$Recycle.Bin",
    "System Volume Information",
    "System",
    "Library",
    "Applications",
    "proc",
    "sys",
    "dev",
}


def get_common_user_directories() -> list[str]:
    """Return standard user data directories (Desktop, Documents, Downloads)."""
    home = Path.home()
    candidates = [
        home / "Desktop",
        home / "Documents",
        home / "Downloads",
        home / "OneDrive",
    ]
    return [str(p) for p in candidates if p.exists() and p.is_dir()]


DEFAULT_SUPPORTED_EXTENSIONS = {
    # Tabular & Spreadsheets
    ".csv": CSVExtractor,
    ".tsv": CSVExtractor,
    ".xlsx": ExcelExtractor,
    ".xlsm": ExcelExtractor,
    # Documents
    ".pdf": PDFExtractor,
    ".docx": DocxExtractor,
    ".dotx": DocxExtractor,
    ".odt": ODTExtractor,
    ".ods": ODTExtractor,
    ".rtf": RTFExtractor,
    # Text, Code & Structured Files
    ".txt": TextExtractor,
    ".log": TextExtractor,
    ".md": TextExtractor,
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

    def scan_directories(
        self,
        target_paths: list[str],
        progress_callback: Callable[[str, int, int], None] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> DataInventorySummary:
        """Scan multiple directory targets and aggregate findings into a single summary."""
        all_results: list[FileScanResult] = []
        by_category: dict[str, int] = defaultdict(int)
        by_type: dict[str, int] = defaultdict(int)
        high_risk_files: list[str] = []
        stale_1y = 0
        stale_3y = 0

        for path in target_paths:
            try:
                sub_summary = self.scan_directory(path, progress_callback, exclude_patterns)
                all_results.extend(sub_summary.results)
                for k, v in sub_summary.by_category.items():
                    by_category[k] += v
                for k, v in sub_summary.by_type.items():
                    by_type[k] += v
                high_risk_files.extend(sub_summary.high_risk_files)
                stale_1y += sub_summary.stale_files_over_1y
                stale_3y += sub_summary.stale_files_over_3y
            except Exception:
                continue

        total_files = len(all_results)
        sensitive_count = sum(1 for r in all_results if r.is_sensitive)
        total_pii = sum(by_type.values())

        return DataInventorySummary(
            scanner_version=__version__,
            scan_timestamp=datetime.now(timezone.utc),
            target_path=", ".join(target_paths),
            total_files_scanned=total_files,
            total_sensitive_files=sensitive_count,
            total_clean_files=total_files - sensitive_count,
            total_pii_instances=total_pii,
            by_category=dict(by_category),
            by_type=dict(by_type),
            high_risk_files=high_risk_files,
            stale_files_over_1y=stale_1y,
            stale_files_over_3y=stale_3y,
            results=all_results,
        )
