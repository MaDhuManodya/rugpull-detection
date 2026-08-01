"""
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
