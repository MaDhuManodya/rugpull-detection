"""
app/utils/validators.py
────────────────────────
EVM address and blockchain input validators.
"""

from __future__ import annotations

import re

from app.core.exceptions import InvalidAddressException, InvalidChainException

# Valid EVM chains supported by this system
SUPPORTED_CHAINS = frozenset({"ethereum", "bsc"})

# EVM address regex: 0x followed by exactly 40 hex characters
_EVM_ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")


def validate_evm_address(address: str) -> str:
    """
    Validate an EVM-compatible blockchain address.

    Args:
        address: Raw address string (checksummed or lowercase).

    Returns:
        Lowercased address string if valid.

    Raises:
        InvalidAddressException: If the address format is invalid.
    """
    if not address:
        raise InvalidAddressException("Address must not be empty.")
    address = address.strip()
    if not _EVM_ADDRESS_RE.match(address):
        raise InvalidAddressException(
            f"Invalid EVM address format: '{address}'. "
            "Expected 0x followed by 40 hexadecimal characters."
        )
    return address.lower()


def validate_chain(chain: str) -> str:
    """
    Validate that the chain identifier is supported.

    Raises:
        InvalidChainException: If the chain is not supported.
    """
    chain = chain.lower().strip()
    if chain not in SUPPORTED_CHAINS:
        raise InvalidChainException(
            f"Unsupported chain: '{chain}'. Supported: {sorted(SUPPORTED_CHAINS)}"
        )
    return chain


def is_zero_address(address: str) -> bool:
    """Return True if the address is the EVM zero address."""
    return address.lower() == "0x" + "0" * 40


def is_contract_address(address: str) -> bool:
    """
    Heuristic check: contract addresses typically don't start with 0x000...
    This is a placeholder; actual contract detection requires on-chain RPC call.
    """
    return not is_zero_address(address)
