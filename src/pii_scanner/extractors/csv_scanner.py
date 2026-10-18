"""Streaming CSV extractor capable of handling diverse delimiters and encodings."""

import csv
from collections import defaultdict
from pathlib import Path

from pii_scanner.core.models import FileScanResult, Finding
from pii_scanner.extractors.base import BaseExtractor


class CSVExtractor(BaseExtractor):
    """Extracts PII from CSV files with streaming row processing."""

    SUPPORTED_ENCODINGS = ("utf-8", "utf-8-sig", "latin1", "cp1252", "utf-16")

    def extract(self, file_path: str) -> FileScanResult:
        path = Path(file_path)
        file_size, modified_time = self.get_file_metadata(file_path)

        all_findings: list[Finding] = []
        findings_by_type: dict[str, int] = defaultdict(int)

        # Attempt to open file with supported encodings
        for encoding in self.SUPPORTED_ENCODINGS:
            try:
                with open(path, encoding=encoding, errors="replace") as f:
                    # Sniff delimiter from sample
                    sample = f.read(4096)
                    f.seek(0)
                    delimiter = ","
                    try:
                        dialect = csv.Sniffer().sniff(sample, delimiters=",\t;|")
                        delimiter = dialect.delimiter
                    except csv.Error:
                        if ";" in sample and sample.count(";") > sample.count(","):
                            delimiter = ";"
                        elif "\t" in sample:
                            delimiter = "\t"

                    reader = csv.reader(f, delimiter=delimiter)
                    headers: list[str] = []
                    try:
                        headers = next(reader, [])
                    except StopIteration:
                        pass

                    for row_idx, row in enumerate(reader, start=2):
                        for col_idx, cell in enumerate(row):
                            if not cell or len(cell.strip()) < 3:
                                continue
                            col_name = (
                                headers[col_idx] if col_idx < len(headers) else f"Col {col_idx + 1}"
                            )
                            location = f"Row {row_idx}, '{col_name}'"
                            cell_findings = self.scan_text_segment(
                                cell, location, column_name=col_name
                            )
                            for finding in cell_findings:
                                all_findings.append(finding)
                                findings_by_type[finding.pii_type.value] += 1
                break  # Successfully parsed
            except UnicodeError:
                continue
            except Exception as e:
                return FileScanResult(
                    file_path=str(path.resolve()),
                    file_name=path.name,
                    file_size_bytes=file_size,
                    modified_time=modified_time,
                    is_sensitive=False,
                    findings_count=0,
                    error_message=str(e),
                )

        return FileScanResult(
            file_path=str(path.resolve()),
            file_name=path.name,
            file_size_bytes=file_size,
            modified_time=modified_time,
            is_sensitive=len(all_findings) > 0,
            findings_count=len(all_findings),
            findings_by_type=dict(findings_by_type),
            sample_findings=all_findings[:10],
        )
