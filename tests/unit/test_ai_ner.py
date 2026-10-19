"""Unit tests for Pass 2 Local Edge AI NER inference and integration."""

from unittest.mock import MagicMock, patch

from pii_scanner.ai.edge_ner import LocalEdgeNER
from pii_scanner.cli import run_cli
from pii_scanner.core.models import PIICategory, PIIType
from pii_scanner.extractors.text_scanner import TextExtractor


def test_local_edge_ner_availability() -> None:
    with patch("importlib.util.find_spec", return_value=MagicMock()):
        assert LocalEdgeNER.is_available() is True
    with patch("importlib.util.find_spec", return_value=None):
        assert LocalEdgeNER.is_available() is False


def test_local_edge_ner_predict_with_mock() -> None:
    ner = LocalEdgeNER()
    # When model is not loaded, returns empty list
    assert ner.predict_entities("Some sample text here") == []

    # Mock the internal GLiNER model
    mock_gliner = MagicMock()
    mock_gliner.predict_entities.return_value = [
        {"text": "Rahul Dravid", "label": "person name", "score": 0.98},
        {"text": "Indiranagar", "label": "address", "score": 0.92},
        {"text": "hypertension", "label": "medical condition", "score": 0.89},
    ]
    ner._model = mock_gliner

    results = ner.predict_entities("Patient Rahul Dravid lives at Indiranagar with hypertension.")
    assert len(results) == 3
    assert results[0]["text"] == "Rahul Dravid"
    assert results[0]["label"] == "person name"

    # Short string should be skipped without calling model
    mock_gliner.reset_mock()
    assert ner.predict_entities("hi") == []
    mock_gliner.predict_entities.assert_not_called()


def test_base_extractor_with_ai_ner() -> None:
    mock_ner = MagicMock()
    mock_ner.predict_entities.return_value = [
        {"text": "Sunita Williams", "label": "person name", "score": 0.97},
        {"text": "Sector 4, Dwarka", "label": "address", "score": 0.91},
        {"text": "cardiac arrest", "label": "medical condition", "score": 0.88},
    ]

    extractor = TextExtractor(ai_ner=mock_ner)
    findings = extractor.scan_text_segment(
        "Subject Sunita Williams was treated at Sector 4, Dwarka after suffering cardiac arrest.",
        "Line 1",
    )

    types_found = {f.pii_type for f in findings}
    assert PIIType.NAME in types_found
    assert PIIType.ADDRESS in types_found
    assert PIIType.HEALTH in types_found

    # Verify HEALTH category and masking
    health_finding = next(f for f in findings if f.pii_type == PIIType.HEALTH)
    assert health_finding.pii_type.category == PIICategory.HEALTH
    assert health_finding.masked_value == "c***t"
    assert health_finding.confidence == 0.88


def test_base_extractor_ai_deduplication() -> None:
    """If Pass 1 rule validator and Pass 2 AI find the same entity, it must be deduplicated."""
    mock_ner = MagicMock()
    # Mock AI returning an entity that Pass 1 regex also finds (e.g. John Doe)
    mock_ner.predict_entities.return_value = [
        {"text": "Dr. Ramesh Sharma", "label": "person name", "score": 0.95},
    ]

    extractor = TextExtractor(ai_ner=mock_ner)
    # "Dr. Ramesh Sharma" will be matched by Pass 1 PersonNameValidator
    findings = extractor.scan_text_segment(
        "Attending physician: Dr. Ramesh Sharma at the regional clinic.",
        "Line 10",
    )

    name_findings = [f for f in findings if f.pii_type == PIIType.NAME]
    # Deduplication ensures it is recorded only once for the same location and masked value
    assert len(name_findings) == 1


def test_cli_ai_missing_dependency(capsys) -> None:  # type: ignore[no-untyped-def]
    with patch("pii_scanner.ai.edge_ner.LocalEdgeNER.is_available", return_value=False):
        exit_code = run_cli(["scan", ".", "--ai", "-q"])
        assert exit_code == 1


def test_cli_ai_flag_wiring(tmp_path) -> None:  # type: ignore[no-untyped-def]
    test_file = tmp_path / "notes.txt"
    test_file.write_text("Patient Vikram Sarabhai reports acute asthma.", encoding="utf-8")

    mock_ner = MagicMock()
    mock_ner.predict_entities.return_value = [
        {"text": "Vikram Sarabhai", "label": "person name", "score": 0.96},
        {"text": "acute asthma", "label": "medical condition", "score": 0.91},
    ]

    with patch("pii_scanner.ai.edge_ner.LocalEdgeNER") as MockNERClass:
        mock_instance = MockNERClass.return_value
        mock_instance.is_available.return_value = True
        mock_instance.predict_entities = mock_ner.predict_entities

        exit_code = run_cli(
            [
                "scan",
                str(tmp_path),
                "--ai",
                "-f",
                "json",
                "-o",
                str(tmp_path / "out"),
                "-q",
            ]
        )
        assert exit_code == 0
