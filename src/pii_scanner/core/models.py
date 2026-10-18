"""Core data models and type definitions for EasyDP Local PII Scanner."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class PIICategory(str, Enum):
    """Broad categories aligned with DPDP Data Inventory Mapping (DIM-01)."""

    IDENTITY = "Identity & Official Identifiers"
    FINANCIAL = "Financial & Banking Details"
    CONTACT = "Contact & Communications"


class PIIType(str, Enum):
    """Specific PII data types validated by exact checksums or strict heuristics."""

    AADHAAR = "Aadhaar Number"
    PAN = "PAN Card"
    NAME = "Person Name"
    GSTIN = "GSTIN (Tax ID)"
    IFSC = "Bank IFSC Code"
    UPI = "UPI VPA Handle"
    PHONE = "Indian Mobile Number"
    EMAIL = "Email Address"
    ADDRESS = "Postal Address"
    PINCODE = "Indian PIN Code"

    @property
    def category(self) -> PIICategory:
        if self in (PIIType.AADHAAR, PIIType.PAN, PIIType.NAME):
            return PIICategory.IDENTITY
        if self in (PIIType.GSTIN, PIIType.IFSC, PIIType.UPI):
            return PIICategory.FINANCIAL
        return PIICategory.CONTACT


# Precomputed O(1) lookups from PII type string value to PIICategory / category name
PII_VALUE_TO_CATEGORY: dict[str, PIICategory] = {pt.value: pt.category for pt in PIIType}
PII_VALUE_TO_CATEGORY_STR: dict[str, str] = {pt.value: pt.category.value for pt in PIIType}


@dataclass
class Finding:
    """Individual sensitive data finding with location and safe redacted preview."""

    pii_type: PIIType
    masked_value: str
    location: str  # e.g., "Row 42, Column 'Aadhaar'" or "Line 12"
    confidence: float = 1.0  # 1.0 for checksum-validated data
    entity_info: str | None = None  # e.g., "Individual" or "Company" for PAN


@dataclass
class FileScanResult:
    """Scan outcome for a single file or data source."""

    file_path: str
    file_name: str
    file_size_bytes: int
    modified_time: datetime
    is_sensitive: bool = False
    findings_count: int = 0
    findings_by_type: dict[str, int] = field(default_factory=dict)
    sample_findings: list[Finding] = field(default_factory=list)
    error_message: str | None = None


@dataclass
class DataInventorySummary:
    """Aggregate data ownership and governance summary for DPDP inventory."""

    scanner_version: str
    scan_timestamp: datetime
    target_path: str
    total_files_scanned: int
    total_sensitive_files: int
    total_clean_files: int
    total_pii_instances: int
    by_category: dict[str, int] = field(default_factory=dict)
    by_type: dict[str, int] = field(default_factory=dict)
    high_risk_files: list[str] = field(default_factory=list)
    stale_files_over_1y: int = 0
    stale_files_over_3y: int = 0
    results: list[FileScanResult] = field(default_factory=list)
    skipped_targets: list[str] = field(default_factory=list)
