"""Excel workbook extractor (.xlsx / .xlsm) utilizing memory-optimized streaming."""

from collections import defaultdict
from pathlib import Path

import openpyxl

from pii_scanner.core.models import FileScanResult, Finding
from pii_scanner.extractors.base import BaseExtractor


class ExcelExtractor(BaseExtractor):
    """Extracts sensitive PII across all worksheets in Excel workbooks."""

    def extract(self, file_path: str) -> FileScanResult:
        path = Path(file_path)
        file_size, modified_time = self.get_file_metadata(file_path)

        all_findings: list[Finding] = []
        findings_by_type: dict[str, int] = defaultdict(int)

        try:
            # data_only=True evaluates formulas to cached values
            wb = openpyxl.load_workbook(filename=str(path), read_only=True, data_only=True)
            for sheetname in wb.sheetnames:
                ws = wb[sheetname]
                rows_iter = ws.iter_rows(values_only=True)

                try:
                    first_row = next(rows_iter, None)
                except StopIteration:
                    first_row = None

                headers: list[str] = []
                if first_row:
                    headers = [
                        str(c) if c is not None else f"Col {i + 1}" for i, c in enumerate(first_row)
                    ]

                for row_idx, row in enumerate(rows_iter, start=2):
                    for col_idx, cell_value in enumerate(row):
                        if cell_value is None:
                            continue
                        cell_str = str(cell_value).strip()
                        if len(cell_str) < 3:
                            continue

                        col_name = (
                            headers[col_idx] if col_idx < len(headers) else f"Col {col_idx + 1}"
                        )
                        location = f"Sheet '{sheetname}', Row {row_idx}, Col '{col_name}'"
                        cell_findings = self.scan_text_segment(cell_str, location, column_name=col_name)
                        for finding in cell_findings:
                            all_findings.append(finding)
                            findings_by_type[finding.pii_type.value] += 1
            wb.close()
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
