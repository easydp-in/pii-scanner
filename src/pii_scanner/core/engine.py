"""Core orchestration engine for local file discovery, routing, and PII inventory aggregation."""

import logging
import os
from collections import defaultdict
from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pii_scanner import __version__
from pii_scanner.core.models import (
    DataInventorySummary,
    FileScanResult,
)
from pii_scanner.extractors.base import BaseExtractor
from pii_scanner.extractors.csv_scanner import CSVExtractor
from pii_scanner.extractors.docx_scanner import DocxExtractor
from pii_scanner.extractors.excel_scanner import ExcelExtractor
from pii_scanner.extractors.odt_scanner import ODTExtractor
from pii_scanner.extractors.pdf_scanner import PDFExtractor
from pii_scanner.extractors.rtf_scanner import RTFExtractor
from pii_scanner.extractors.text_scanner import TextExtractor

logger = logging.getLogger("pii_scanner.engine")

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


DEFAULT_SUPPORTED_EXTENSIONS: dict[str, type[BaseExtractor]] = {
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


class ExtractorRegistry:
    """Pluggable registry mapping file extensions to BaseExtractor instances with singleton reuse."""

    def __init__(
        self,
        custom_mapping: Mapping[str, type[BaseExtractor] | BaseExtractor] | None = None,
        ai_ner: Any | None = None,
    ) -> None:
        self._extractors: dict[str, BaseExtractor] = {}
        self.ai_ner = ai_ner
        if custom_mapping:
            for ext, item in custom_mapping.items():
                self.register(ext, item)
        else:
            self._load_defaults()

    def _load_defaults(self) -> None:
        csv_ext = CSVExtractor(ai_ner=self.ai_ner)
        excel_ext = ExcelExtractor(ai_ner=self.ai_ner)
        pdf_ext = PDFExtractor(ai_ner=self.ai_ner)
        docx_ext = DocxExtractor(ai_ner=self.ai_ner)
        odt_ext = ODTExtractor(ai_ner=self.ai_ner)
        rtf_ext = RTFExtractor(ai_ner=self.ai_ner)
        text_ext = TextExtractor(ai_ner=self.ai_ner)

        defaults: dict[str, BaseExtractor] = {
            ".csv": csv_ext,
            ".tsv": csv_ext,
            ".xlsx": excel_ext,
            ".xlsm": excel_ext,
            ".pdf": pdf_ext,
            ".docx": docx_ext,
            ".dotx": docx_ext,
            ".odt": odt_ext,
            ".ods": odt_ext,
            ".rtf": rtf_ext,
            ".txt": text_ext,
            ".log": text_ext,
            ".md": text_ext,
            ".json": text_ext,
            ".xml": text_ext,
            ".sql": text_ext,
            ".yaml": text_ext,
            ".yml": text_ext,
        }
        for ext, inst in defaults.items():
            self._extractors[ext.lower()] = inst

    def set_ai_ner(self, ai_ner: Any | None) -> None:
        """Update ai_ner across all registered extractors."""
        self.ai_ner = ai_ner
        for inst in self._extractors.values():
            inst.set_ai_ner(ai_ner)

    def register(self, ext: str, extractor_or_cls: type[BaseExtractor] | BaseExtractor) -> None:
        """Register or override an extractor for a given file extension."""
        normalized = ext.lower() if ext.startswith(".") else f".{ext.lower()}"
        if isinstance(extractor_or_cls, type):
            inst = extractor_or_cls()
            if self.ai_ner is not None:
                inst.set_ai_ner(self.ai_ner)
            self._extractors[normalized] = inst
        else:
            if self.ai_ner is not None:
                extractor_or_cls.set_ai_ner(self.ai_ner)
            self._extractors[normalized] = extractor_or_cls

    def get(self, ext: str) -> BaseExtractor | None:
        """Retrieve the extractor instance registered for the extension."""
        return self._extractors.get(ext.lower())

    def supported_extensions(self) -> set[str]:
        """Return the set of currently registered extensions."""
        return set(self._extractors.keys())

    def __contains__(self, ext: str) -> bool:
        return ext.lower() in self._extractors


class ScannerEngine:
    """Discovers, scans, and aggregates data ownership & PII inventory metrics."""

    def __init__(
        self,
        ignored_dirs: set[str] | None = None,
        custom_extractors: Mapping[str, type[BaseExtractor]] | None = None,
        registry: ExtractorRegistry | None = None,
        ai_ner: Any | None = None,
    ) -> None:
        self.ignored_dirs = set(ignored_dirs) if ignored_dirs is not None else DEFAULT_IGNORED_DIRS
        self.ai_ner = ai_ner
        if registry is not None:
            self.registry = registry
            if ai_ner is not None:
                self.registry.set_ai_ner(ai_ner)
        elif custom_extractors is not None:
            self.registry = ExtractorRegistry(custom_extractors, ai_ner=ai_ner)
        else:
            self.registry = ExtractorRegistry(ai_ner=ai_ner)

    @property
    def extractors_map(self) -> dict[str, BaseExtractor]:
        """Backward-compatibility property exposing the internal mapping."""
        return self.registry._extractors

    def discover_files(
        self,
        target_path: str | Path,
        exclude_patterns: list[str] | None = None,
    ) -> list[Path]:
        """Discover all supported candidate files under a single target path."""
        target = Path(target_path).resolve()
        if not target.exists():
            raise FileNotFoundError(f"Target path does not exist: {target_path}")

        files_to_scan: list[Path] = []
        if target.is_file():
            if target.suffix.lower() in self.registry:
                files_to_scan.append(target)
        else:
            for root, dirs, files in os.walk(target):
                # Filter out ignored directories in-place
                dirs[:] = [d for d in dirs if d not in self.ignored_dirs and not d.startswith(".")]

                for f in sorted(files):
                    ext = Path(f).suffix.lower()
                    if ext in self.registry:
                        full_p = Path(root) / f
                        if exclude_patterns:
                            if any(pattern in str(full_p) for pattern in exclude_patterns):
                                continue
                        files_to_scan.append(full_p)
        return files_to_scan

    def _scan_file_list(
        self,
        files_to_scan: list[Path],
        target_label: str,
        progress_callback: Callable[[str, int, int], None] | None = None,
    ) -> DataInventorySummary:
        """Scan a pre-discovered list of files and compute DPDP metrics."""
        total_files = len(files_to_scan)
        results: list[FileScanResult] = []
        by_category: dict[str, int] = defaultdict(int)
        by_type: dict[str, int] = defaultdict(int)
        high_risk_files: list[str] = []
        stale_1y = 0
        stale_3y = 0

        logger.info("Commencing scan of %d candidate files for '%s'...", total_files, target_label)
        now = datetime.now(timezone.utc)
        for idx, file_p in enumerate(files_to_scan, start=1):
            if progress_callback:
                progress_callback(file_p.name, idx, total_files)

            ext = file_p.suffix.lower()
            extractor = self.registry.get(ext)
            if not extractor:
                logger.debug(
                    "Skipping unsupported extension [%d/%d]: %s", idx, total_files, file_p.name
                )
                continue

            scan_res = extractor.extract(str(file_p))
            results.append(scan_res)

            if scan_res.error_message:
                logger.warning(
                    "Error parsing file [%d/%d] %s: %s",
                    idx,
                    total_files,
                    file_p.name,
                    scan_res.error_message,
                )
            else:
                logger.debug(
                    "Scanned [%d/%d] %s (%d bytes): %d findings",
                    idx,
                    total_files,
                    file_p.name,
                    scan_res.file_size_bytes,
                    scan_res.findings_count,
                )

            # Check staleness with timezone-aware normalization
            mod_time = scan_res.modified_time
            if mod_time.tzinfo is None:
                mod_time = mod_time.replace(tzinfo=timezone.utc)
            days_old = (now - mod_time).days
            if days_old > 365 * 3:
                stale_3y += 1
            elif days_old > 365:
                stale_1y += 1

            if scan_res.is_sensitive:
                from pii_scanner.core.models import PII_VALUE_TO_CATEGORY_STR, PIICategory

                for pii_type_str, count in scan_res.findings_by_type.items():
                    by_type[pii_type_str] += count
                    category_name = PII_VALUE_TO_CATEGORY_STR.get(
                        pii_type_str, PIICategory.CONTACT.value
                    )
                    by_category[category_name] += count

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

        logger.info(
            "Scan complete for '%s'. Total: %d, Sensitive: %d, Clean: %d, Total PII: %d",
            target_label,
            total_files,
            sensitive_count,
            total_files - sensitive_count,
            total_pii,
        )

        return DataInventorySummary(
            scanner_version=__version__,
            scan_timestamp=datetime.now(timezone.utc),
            target_path=target_label,
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

    def scan_directory(
        self,
        target_path: str,
        progress_callback: Callable[[str, int, int], None] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> DataInventorySummary:
        """Recursively scan a path and compile a comprehensive DPDP data inventory summary."""
        files = self.discover_files(target_path, exclude_patterns=exclude_patterns)
        return self._scan_file_list(files, str(Path(target_path).resolve()), progress_callback)

    def scan_directories(
        self,
        target_paths: list[str],
        progress_callback: Callable[[str, int, int], None] | None = None,
        exclude_patterns: list[str] | None = None,
    ) -> DataInventorySummary:
        """Scan multiple directory targets and aggregate findings into a single summary."""
        all_files: list[Path] = []
        skipped_targets: list[str] = []

        for path in target_paths:
            try:
                found = self.discover_files(path, exclude_patterns=exclude_patterns)
                for f in found:
                    if f not in all_files:
                        all_files.append(f)
            except Exception as e:
                skipped_targets.append(f"{path}: {e}")
                continue

        summary = self._scan_file_list(all_files, ", ".join(target_paths), progress_callback)
        summary.skipped_targets = skipped_targets
        return summary
