"""Pass 2 Edge AI NER module for deep unstructured PII detection."""

from pii_scanner.ai.edge_ner import LocalEdgeNER, check_system_resources

__all__ = ["LocalEdgeNER", "check_system_resources"]
