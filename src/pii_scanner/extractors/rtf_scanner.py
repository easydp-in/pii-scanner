"""Rich Text Format (.rtf) document extractor."""

import re
from collections import defaultdict
from pathlib import Path

from pii_scanner.core.models import FileScanResult, Finding
from pii_scanner.extractors.base import BaseExtractor


class RTFExtractor(BaseExtractor):
    """Extracts sensitive PII from Rich Text Format (.rtf) files."""

    def extract(self, file_path: str) -> FileScanResult:
        path = Path(file_path)
        file_size, modified_time = self.get_file_metadata(file_path)

        all_findings: list[Finding] = []
        findings_by_type: dict[str, int] = defaultdict(int)

        try:
            raw_text = path.read_text(encoding="utf-8", errors="replace")
            # Strip RTF control words and braces
            clean_text = re.sub(r"\\[a-zA-Z]+-?\d* ?", " ", raw_text)
            clean_text = clean_text.replace("{", " ").replace("}", " ")

            for line_idx, line in enumerate(clean_text.splitlines(), start=1):
                line_str = line.strip()
                if not line_str:
                    continue
                location = f"Line {line_idx}"
                findings = self.scan_text_segment(line_str, location)
                for f in findings:
                    all_findings.append(f)
                    findings_by_type[f.pii_type.value] += 1

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
