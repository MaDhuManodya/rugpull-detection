"""
app/collectors/parsers/transaction.py
Transaction Collector.
Parses native transfers, ERC-20 transfers, and contract interactions.
"""
from typing import Any, Dict
from web3.types import TxData
from app.models.enums import TxTypeEnum

class TransactionParser:
    @staticmethod
    def parse_transaction(tx: TxData, block_timestamp: int) -> Dict[str, Any]:
        """
        Decomposes transaction into sender, receiver, value, gas used, and calldata.
        Categorizes transaction type based on calldata signatures.
        """
        # Basic parsing logic
        input_data = tx.get("input", "")
        tx_type = TxTypeEnum.OTHER
        
        # Simple heuristic for ERC20 transfers / approvals
        if input_data.startswith("0xa9059cbb"):
            tx_type = TxTypeEnum.TRANSFER
        elif input_data.startswith("0x095ea7b3"):
            tx_type = TxTypeEnum.APPROVAL
            
        return {
            "tx_hash": tx.get("hash").hex(),
            "block_number": tx.get("blockNumber"),
            "block_timestamp": block_timestamp,
            "transaction_index": tx.get("transactionIndex"),
            "from_address": tx.get("from"),
            "to_address": tx.get("to"),
            "value_wei": str(tx.get("value", 0)),
            "gas_used": tx.get("gas"),
            "gas_price_wei": str(tx.get("gasPrice", 0)),
            "tx_type": tx_type.value,
            "raw_input": input_data
        }
