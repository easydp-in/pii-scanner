"""Integration tests for Tally ERP 9 / Prime localhost:9000 XML connector."""

from unittest.mock import MagicMock, patch

from pii_scanner.core.models import PIIType
from pii_scanner.extractors.tally import TallyConnector
from pii_scanner.validators.gstin import calculate_gstin_check_digit

MOCK_TALLY_RESPONSE = """<ENVELOPE>
    <BODY>
        <DATA>
            <COLLECTION>
                <LEDGER NAME="M/S Sharma Traders">
                    <PARENT>Sundry Debtors</PARENT>
                    <PARTYGSTIN>{gstin}</PARTYGSTIN>
                    <INCOMETAXNUMBER>ABCPD1234F</INCOMETAXNUMBER>
                    <LEDGERPHONE>9876543210</LEDGERPHONE>
                    <EMAIL>accounts@sharmatraders.in</EMAIL>
                </LEDGER>
                <LEDGER NAME="Cash">
                    <PARENT>Cash-in-Hand</PARENT>
                </LEDGER>
            </COLLECTION>
        </DATA>
    </BODY>
</ENVELOPE>"""


def test_tally_connector_with_mock_response() -> None:
    gstin_prefix = "27AAACR1234A1Z"
    valid_gstin = gstin_prefix + calculate_gstin_check_digit(gstin_prefix)
    xml_content = MOCK_TALLY_RESPONSE.format(gstin=valid_gstin).encode("utf-8")

    mock_resp = MagicMock()
    mock_resp.read.return_value = xml_content
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        connector = TallyConnector(host="127.0.0.1", port=9000)
        result = connector.extract_ledgers()

        assert result.is_sensitive is True
        assert result.findings_by_type[PIIType.GSTIN.value] == 1
        assert result.findings_by_type[PIIType.PAN.value] == 1
        assert result.findings_by_type[PIIType.PHONE.value] == 1
        assert result.findings_by_type[PIIType.EMAIL.value] == 1


def test_tally_connector_offline() -> None:
    # Port 59999 should not have a server listening
    connector = TallyConnector(host="127.0.0.1", port=59999, timeout_seconds=1)
    result = connector.extract_ledgers()

    assert result.is_sensitive is False
    assert result.error_message is not None
    assert "Tally is offline or not listening on port 59999" in result.error_message


def test_tally_connector_rejects_remote_hosts() -> None:
    import pytest

    with pytest.raises(
        ValueError, match="Security restriction: TallyConnector strictly permits loopback"
    ):
        TallyConnector(host="192.168.1.100")

    with pytest.raises(
        ValueError, match="Security restriction: TallyConnector strictly permits loopback"
    ):
        TallyConnector(host="evil-vault.internal")
