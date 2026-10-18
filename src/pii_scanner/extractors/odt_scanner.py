"""OpenDocument (.odt, .ods) document extractor using standard library zipfile."""

import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from pathlib import Path

from pii_scanner.core.models import FileScanResult, Finding
from pii_scanner.extractors.base import BaseExtractor

MAX_UNCOMPRESSED_ENTRY_SIZE = 50 * 1024 * 1024  # 50 MB


class ODTExtractor(BaseExtractor):
    """Extracts sensitive PII from OpenDocument (.odt, .ods) files."""

    def extract(self, file_path: str) -> FileScanResult:
        path = Path(file_path)
        file_size, modified_time = self.get_file_metadata(file_path)

        all_findings: list[Finding] = []
        findings_by_type: dict[str, int] = defaultdict(int)

        try:
            with zipfile.ZipFile(str(path), "r") as z:
                if "content.xml" not in z.namelist():
                    return FileScanResult(
                        file_path=str(path.resolve()),
                        file_name=path.name,
                        file_size_bytes=file_size,
                        modified_time=modified_time,
                        is_sensitive=False,
                        findings_count=0,
                        error_message="Invalid OpenDocument archive: content.xml not found",
                    )

                # Guard against zip bomb / excessive decompression attacks
                content_info = z.getinfo("content.xml")
                if content_info.file_size > MAX_UNCOMPRESSED_ENTRY_SIZE:
                    return FileScanResult(
                        file_path=str(path.resolve()),
                        file_name=path.name,
                        file_size_bytes=file_size,
                        modified_time=modified_time,
                        is_sensitive=False,
                        findings_count=0,
                        error_message="Decompression guardrail exceeded: entry size exceeds safety limits",
                    )

                xml_bytes = z.read("content.xml")
                tree = ET.fromstring(xml_bytes)

                p_idx = 0
                for elem in tree.iter():
                    if elem.tag.endswith("}p"):
                        p_idx += 1
                        text_runs = [t.text for t in elem.iter() if t.text]
                        para_str = "".join(text_runs).strip()
                        if not para_str:
                            continue
                        location = f"Para {p_idx}"
                        findings = self.scan_text_segment(para_str, location)
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
