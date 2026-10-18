"""Microsoft Word (.docx, .dotx) document extractor using standard library zipfile."""

import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from pathlib import Path

from pii_scanner.core.models import FileScanResult, Finding
from pii_scanner.extractors.base import BaseExtractor

MAX_UNCOMPRESSED_ENTRY_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_TOTAL_UNCOMPRESSED_SIZE = 150 * 1024 * 1024  # 150 MB


class DocxExtractor(BaseExtractor):
    """Extracts sensitive PII from Word (.docx, .dotx) documents."""

    def extract(self, file_path: str) -> FileScanResult:
        path = Path(file_path)
        file_size, modified_time = self.get_file_metadata(file_path)

        all_findings: list[Finding] = []
        findings_by_type: dict[str, int] = defaultdict(int)

        try:
            with zipfile.ZipFile(str(path), "r") as z:
                xml_targets = [
                    name
                    for name in z.namelist()
                    if name == "word/document.xml"
                    or name.startswith("word/header")
                    or name.startswith("word/footer")
                ]

                if not xml_targets:
                    return FileScanResult(
                        file_path=str(path.resolve()),
                        file_name=path.name,
                        file_size_bytes=file_size,
                        modified_time=modified_time,
                        is_sensitive=False,
                        findings_count=0,
                        error_message="Invalid DOCX archive: word/document.xml not found",
                    )

                # Guard against zip bomb / excessive decompression attacks
                target_infos = [z.getinfo(name) for name in xml_targets]
                total_uncompressed = sum(info.file_size for info in target_infos)
                if (
                    any(info.file_size > MAX_UNCOMPRESSED_ENTRY_SIZE for info in target_infos)
                    or total_uncompressed > MAX_TOTAL_UNCOMPRESSED_SIZE
                ):
                    return FileScanResult(
                        file_path=str(path.resolve()),
                        file_name=path.name,
                        file_size_bytes=file_size,
                        modified_time=modified_time,
                        is_sensitive=False,
                        findings_count=0,
                        error_message="Decompression guardrail exceeded: entry or total size exceeds safety limits",
                    )

                for target_xml in xml_targets:
                    part_label = Path(target_xml).stem
                    xml_bytes = z.read(target_xml)
                    tree = ET.fromstring(xml_bytes)

                    p_idx = 0
                    for elem in tree.iter():
                        if elem.tag.endswith("}p"):
                            p_idx += 1
                            text_runs = [
                                t.text for t in elem.iter() if t.text and t.tag.endswith("}t")
                            ]
                            para_str = "".join(text_runs).strip()
                            if not para_str:
                                continue
                            location = f"{part_label}, Para {p_idx}"
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
