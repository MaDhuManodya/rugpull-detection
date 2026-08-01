"""
app/tests/test_api/test_validators.py
──────────────────────────────────────
Tests for EVM address validators.
"""

from __future__ import annotations

import pytest

from app.core.exceptions import InvalidAddressException, InvalidChainException
from app.utils.validators import (
    is_zero_address,
    validate_chain,
    validate_evm_address,
)


def test_valid_address_lowercase() -> None:
    """Valid lowercase address should be accepted."""
    addr = validate_evm_address("0x1f9840a85d5af5bf1d1762f925bdaddc4201f984")
    assert addr == "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"


def test_valid_address_checksummed() -> None:
    """Checksummed address should be lowercased and accepted."""
    addr = validate_evm_address("0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984")
    assert addr == "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984"


def test_invalid_address_too_short() -> None:
    with pytest.raises(InvalidAddressException):
        validate_evm_address("0x1234")


def test_invalid_address_no_prefix() -> None:
    with pytest.raises(InvalidAddressException):
        validate_evm_address("1f9840a85d5af5bf1d1762f925bdaddc4201f984")


def test_empty_address() -> None:
    with pytest.raises(InvalidAddressException):
        validate_evm_address("")


def test_valid_chain_ethereum() -> None:
    assert validate_chain("ethereum") == "ethereum"


def test_valid_chain_bsc() -> None:
    assert validate_chain("BSC") == "bsc"


def test_invalid_chain() -> None:
    with pytest.raises(InvalidChainException):
        validate_chain("solana")


def test_is_zero_address() -> None:
    assert is_zero_address("0x" + "0" * 40) is True
    assert is_zero_address("0x1f9840a85d5af5bf1d1762f925bdaddc4201f984") is False
