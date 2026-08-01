import os

PARSERS_DIR = "app/collectors/parsers"
os.makedirs(PARSERS_DIR, exist_ok=True)

# 1. Transaction Parser
with open(f"{PARSERS_DIR}/transaction.py", "w") as f:
    f.write('''"""
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
''')

# 2. Contract Parser
with open(f"{PARSERS_DIR}/contract.py", "w") as f:
    f.write('''"""
app/collectors/parsers/contract.py
Smart Contract Collector.
Fetches bytecode, ABIs, metadata, and verification status via Explorer APIs.
"""
import httpx
from app.core.config import settings
from app.models.enums import ChainEnum

class ContractParser:
    @staticmethod
    async def fetch_contract_metadata(address: str, chain: ChainEnum) -> dict:
        """
        Fetches ABI and source code from Etherscan/BscScan if verified.
        """
        if chain == ChainEnum.ETHEREUM:
            api_url = settings.etherscan_api_url
            api_key = settings.etherscan_api_key
        else:
            api_url = settings.bscscan_api_url
            api_key = settings.bscscan_api_key
            
        if not api_url or not api_key:
            return {"is_verified": False, "abi": None}
            
        params = {
            "module": "contract",
            "action": "getsourcecode",
            "address": address,
            "apikey": api_key
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, params=params)
            data = response.json()
            
            if data.get("status") == "1" and data.get("result"):
                result = data["result"][0]
                return {
                    "is_verified": True,
                    "abi": result.get("ABI"),
                    "compiler_version": result.get("CompilerVersion"),
                    "source_code": result.get("SourceCode"),
                    "contract_name": result.get("ContractName")
                }
                
        return {"is_verified": False, "abi": None}
''')

# 3. Liquidity Parser
with open(f"{PARSERS_DIR}/liquidity.py", "w") as f:
    f.write('''"""
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
''')

# 4. Wallet Parser
with open(f"{PARSERS_DIR}/wallet.py", "w") as f:
    f.write('''"""
app/collectors/parsers/wallet.py
Wallet Collector.
Extracts wallet metadata and handles classification (EOA vs Contract).
"""
from web3 import AsyncWeb3
from app.models.enums import WalletTypeEnum

class WalletParser:
    @staticmethod
    async def classify_wallet(w3: AsyncWeb3, address: str) -> dict:
        """Determines if an address is an EOA or a smart contract."""
        code = await w3.eth.get_code(address)
        is_contract = len(code) > 2  # '0x' means empty
        
        wallet_type = WalletTypeEnum.CONTRACT if is_contract else WalletTypeEnum.EOA
        
        return {
            "address": address,
            "is_contract": is_contract,
            "wallet_type": wallet_type.value
        }
''')

# 5. Token Parser
with open(f"{PARSERS_DIR}/token.py", "w") as f:
    f.write('''"""
app/collectors/parsers/token.py
Token Metadata Collector.
Fetches Name, Symbol, Decimals, Total Supply.
"""
from web3 import AsyncWeb3
from app.collectors.core.connector import blockchain_connector
from app.models.enums import ChainEnum

# Minimal ERC20 ABI for metadata
ERC20_ABI = [
    {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}], "type": "function"}
]

class TokenParser:
    @staticmethod
    async def fetch_token_metadata(address: str, chain: ChainEnum) -> dict:
        """Fetches basic ERC20 metadata."""
        w3 = blockchain_connector.get_provider(chain)
        contract = w3.eth.contract(address=w3.to_checksum_address(address), abi=ERC20_ABI)
        
        metadata = {"address": address, "chain": chain.value}
        
        try:
            metadata["name"] = await contract.functions.name().call()
        except Exception:
            metadata["name"] = None
            
        try:
            metadata["symbol"] = await contract.functions.symbol().call()
        except Exception:
            metadata["symbol"] = None
            
        try:
            metadata["decimals"] = await contract.functions.decimals().call()
        except Exception:
            metadata["decimals"] = None
            
        try:
            metadata["total_supply"] = str(await contract.functions.totalSupply().call())
        except Exception:
            metadata["total_supply"] = None
            
        return metadata
''')

# Init file
with open(f"{PARSERS_DIR}/__init__.py", "w") as f:
    f.write('''from .transaction import TransactionParser
from .contract import ContractParser
from .liquidity import LiquidityParser
from .wallet import WalletParser
from .token import TokenParser

__all__ = [
    "TransactionParser",
    "ContractParser",
    "LiquidityParser",
    "WalletParser",
    "TokenParser",
]
''')

print("Generated Parsers.")
