"""
app/collectors/parsers/liquidity.py
Liquidity Event Collector.
Decodes Pair creation, Add/Remove liquidity, and Swap events.
"""
from typing import Dict, Any
from web3.types import LogReceipt
from app.models.enums import LiquidityEventTypeEnum

class LiquidityParser:
    # Event signatures (keccak256 hashes)
    MINT_SIG = "0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f"
    BURN_SIG = "0xdccd412f0b1252819cb1fd330b93224cea42a452a051500e216314227181f4a9"
    SWAP_SIG = "0xd78ad95fa46c994b6551d0da85fc275fac0f10fd0796d5470df0a4274c10729c"

    @staticmethod
    def parse_log(log: LogReceipt) -> Dict[str, Any]:
        """Identifies and parses AMM Mint/Burn/Swap events."""
        topics = log.get("topics", [])
        if not topics:
            return None
            
        event_sig = topics[0].hex()
        
        event_type = None
        if event_sig == LiquidityParser.MINT_SIG:
            event_type = LiquidityEventTypeEnum.MINT
        elif event_sig == LiquidityParser.BURN_SIG:
            event_type = LiquidityEventTypeEnum.BURN
        elif event_sig == LiquidityParser.SWAP_SIG:
            event_type = LiquidityEventTypeEnum.SWAP
        else:
            return None
            
        return {
            "tx_hash": log.get("transactionHash").hex(),
            "log_index": log.get("logIndex"),
            "pool_address": log.get("address"),
            "event_type": event_type.value,
            "raw_data": log.get("data").hex(),
            "topics": [t.hex() for t in topics]
        }
