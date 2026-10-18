"""Text extractor for plain text, markdown, configuration, and log files."""

from collections import defaultdict
from pathlib import Path

from pii_scanner.core.models import FileScanResult, Finding
from pii_scanner.extractors.base import BaseExtractor


class TextExtractor(BaseExtractor):
    """Extracts sensitive PII from text and log files line-by-line."""

    def extract(self, file_path: str) -> FileScanResult:
        path = Path(file_path)
        file_size, modified_time = self.get_file_metadata(file_path)

        all_findings: list[Finding] = []
        findings_by_type: dict[str, int] = defaultdict(int)

        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                for line_idx, line in enumerate(f, start=1):
                    line_str = line.strip()
                    if not line_str:
                        continue
                    location = f"Line {line_idx}"
                    line_findings = self.scan_text_segment(line_str, location)
                    for finding in line_findings:
                        all_findings.append(finding)
                        findings_by_type[finding.pii_type.value] += 1
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
